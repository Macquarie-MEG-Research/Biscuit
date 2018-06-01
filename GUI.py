__author__ = "Matt Sanderson"

from tkinter import *
from tkinter import PanedWindow as tkPanedWindow
from tkinter import filedialog, simpledialog, messagebox
from tkinter.ttk import *

import pickle
import os.path as path
from os import listdir, getcwd
import datetime
import threading

from platform import system as os_name

from mne_bids import raw_to_bids

from FileTypes import generic_file

from ToBIDS import process_folder
from FileIO import create_folder
from EnhancedTreeview import EnhancedTreeview

from InfoContainer import InfoContainer
from InfoEntries import InfoEntry, InfoLabel
from InfoManager import InfoManager

from utils import *

DEFAULTSETTINGS = {"DATA_PATH": "",
                   "MATLAB_PATH": "",
                   "SHOW_ASSOC_MESSAGE":True}

root = Tk()
root.geometry("1080x600")

class main(Frame):
    def __init__(self, master):
        self.master = master
        self.master.title("Biscuit")
        # this directory is weird because the cwd is the parent folder, not the Biscuit folder. Maybe because vscode?
        try:
            if os_name() == 'Windows':
                self.master.iconbitmap('biscuit_icon_windows.ico')
            else:
                # this doesn't work :'(
                img = PhotoImage(file='biscuit.png')
                #self.master.tk.call('wm', 'iconphoto', self.master._w, img)
                self.master.wm_iconphoto(True, img)
                #self.master.wm_iconbitmap(img)
        except:
            pass
        Frame.__init__(self, self.master)

        # this will be a dictionary containing any preloaded data from MNE
        # when we click on a folder to load its information, the object will be
        # placed in this dictionary so that we can then avoid reloading it later
        # as each load of data takes ~0.5s
        self.preloaded_data = dict()

        self._load_settings()

        self.context = None                 # the type of data selected

        self.selected_files = None          # the current set of selected files
        self.prev_selected_files = None     # the previous set. Keep as a buffer in case it is needed (it is for the file association!)

        self.r_click_menu = RightClick(self)

        self._create_widgets()
        self._create_menus()

        self._drag_mode = None

        self._fill_file_tree('')

        # this dictionary will consist of keys which are the file paths to the .con files, and the values will
        # be a list of associated .mrk files
        # all other files (.hsp, .elp) are automatically associated by name I hope...
        self.file_groups = dict()

        self.treeview_select_mode = "NORMAL"        # the different operating modes of the treeview.
        # this will allow us to put the treeview in different modes (eg. select a file when prompted etc)
        # options: "ASSOCIATING", "NORMAL"

        # set some tag configurations
        self.file_treeview.tag_configure('ASSOC_FILES', foreground="Green")

    def _fill_file_tree(self, parent, directory = None):
        """
        Iterate over the folder structure and list all the files in the treeview

        This function will need to be improved so that when multiple acquisitions are in a single folder it doesn't create multiple folders
        """
        if directory is None:
            # in this case we are at the root
            dir_ = self.settings["DATA_PATH"]
        else:
            dir_ = directory

        # we want to put folders above files (it looks nicer!!)
        num_folders = 0

        for file in listdir(dir_):
            fname, ext = path.splitext(file)

            fullpath = path.join(dir_, file)
            
            if path.isdir(fullpath):
                folder = self.file_treeview.insert(parent, num_folders,
                                                   values=['', fullpath],
                                                   text=fname, open=False)
                num_folders += 1
                self._fill_file_tree(folder, directory=fullpath)
            else:
                self.file_treeview.insert(parent, 'end', values=[ext, fullpath],
                                          text=fname, open=False, tags=(ext))

    def _load_settings(self):
        # first, attempt to load the settings file:
        try:
            with open('settings.pkl', 'rb') as settings:
                self.settings = pickle.load(settings)
            # we can compare the read settings and default ones to allow for the settings file
            # to automatically update itself if required.
            if self.settings.keys() != DEFAULTSETTINGS.keys():
                for setting in DEFAULTSETTINGS:
                    if self.settings.get(setting, None) is None:
                        self.settings[setting] = DEFAULTSETTINGS[setting]
        except:
            # in this case we have no settings file so we need to create a new one
            self.settings = DEFAULTSETTINGS

        # now we want to validate the settings tp ensure that the path specified actually exists etc
        if not path.exists(self.settings["DATA_PATH"]):
            # the specified path for the data doesn't exist.
            # this is probably due to changing computer or something...
            # get the user to enter a new path
            self._get_data_location()
        if not path.exists(self.settings["MATLAB_PATH"]):
            self._get_matlab_location()

    def _write_settings(self):
        with open('settings.pkl', 'wb') as settings:
            pickle.dump(self.settings, settings)

    def _create_menus(self):
        """
        Create the menus
        """
        # main menu bar
        self.menu_bar = Menu(self.master)
        # options menu
        self.options_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Options", menu=self.options_menu)

        # add options to the options menu:
        self.options_menu.add_command(label="Root directory", command=self._get_data_location)
        self.options_menu.add_command(label="Matlab path", command=self._get_matlab_location)

        # finally, tell the GUI to include the menu bar
        self.master.config(menu=self.menu_bar)

    def _create_widgets(self):
        # create all the visual elements required

        # middle frame section
        main_frame = Frame(self.master)
        self.pw = tkPanedWindow(main_frame, orient=HORIZONTAL, sashrelief=RIDGE, sashpad=1, sashwidth=4)
        # frame for the treeview
        treeview_frame = Frame(self.pw, width=1000, height=400)
        self.file_treeview = EnhancedTreeview(treeview_frame,
                                      columns = ["dtype", "filepath"],
                                      selectmode = 'extended',
                                      displaycolumns = ["dtype"])
        self.file_treeview.enhance(allow_dnd = False,
                                   scrollbars=['y', 'x'],
                                   leftclick=self._select_treeview_entry,
                                   rightclick=self._right_click_treeview_entry,
                                   multiclick=self._select_multiple)        # not used at the moment. Just reverting back to default selection stuff
        self.file_treeview.heading("#0", text = "Directory Structure")
        self.file_treeview.heading("dtype", text = "Type")
        self.file_treeview.column("dtype", width=50, minwidth=35, stretch=False)

        #self.file_treeview.bind('<ButtonPress-1>', self.column_check)
        #self.file_treeview.bind("<B1-Motion>", self.column_drag, add='+')

        #self.file_treeview.grid(row=2, column=0, sticky="nsew", in_=treeview_frame, columnspan=10, rowspan=10)
        self.file_treeview.pack(side=LEFT, fill=BOTH, expand=1)
        treeview_frame.grid(column=0, row=0, sticky="nsew")
        self.pw.add(treeview_frame)

        self.file_treeview.root_path = self.settings["DATA_PATH"]

        # frame for the notebook panel
        #notebook_frame = Frame(main_frame, width=100, height=300)
        self.info_notebook = InfoManager(self.pw)
        self.info_notebook.draw()
        # info frame
        #self.info_frame = Frame(notebook_frame)

        #self.info_notebook.grid(column=1, row=0, sticky="nsew")
        self.pw.add(self.info_notebook)
        self.info_notebook.grid_propagate(0)
        #self.info_notebook.pack(fill=BOTH, expand=1)
        #treeview_frame.grid(row=0, column=0, sticky="nsew")
        #notebook_frame.grid(row=0, column=1, sticky="nsew")
        #notebook_frame.pack(side=LEFT, fill=BOTH, expand=1)
        self.pw.grid(column=0, row=0, sticky="nsew")
        main_frame.grid(column=0, row=0, sticky="nsew")

        #mf = Frame(self.master)
        self.exitButton = Button(main_frame, text = "Exit", command = self._quit)
        #self.exitButton.pack(side=LEFT)
        self.exitButton.grid(column=0, row=1, columnspan=2)

        # add resizing stuff:
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    # not gonna worry about this for now...
    def column_check(self, event):
        print(self.file_treeview.identify_region(event.x, event.y), 'reg')
        if self.file_treeview.identify_region(event.x, event.y) == 'separator':
            self._drag_mode = 'separator' 
            left_col = self.file_treeview.identify_column(event.x)
            right_col = '#{}'.format(int(left_col.lstrip('#'))+1)
            print(left_col, right_col)
            print(self.file_treeview.column(left_col, 'width'))
            print(self.file_treeview.column(right_col, 'width'))
            #right_column = '#%i' % (int(tree.identify_column(event.x)[1:]) + 1)

    # this either...
    def column_drag(self, event):
        if self._drag_mode == 'separator':
            print('hi')

    def _populate_info_panel(self, sids):
        """
        This will receive the list of all selected tree entries
        """
        self.info_notebook.data = [self.preloaded_data.get(id_, None) for id_ in sids if self.preloaded_data.get(id_, None) is not None]
        # if the info panel needs to be redrawn, redraw it
        if self.info_notebook.requires_update:
            self.info_notebook.populate()
            self.info_notebook.draw()

    def _right_click_treeview_entry(self, event):
        # have a separate function to wrap the call to the RightClick .popup method.
        # This will allow us to do some logic to allow for nicer right-clicking
        # Ie. if you right click on an entry that is not the focus, we want it to
        # become the focus.
        # Otherwise if we right click on an entry that has focus we want to get all
        # objects that have focus.
        right_clicked_id = self.file_treeview.identify_row(event.y)
        highlighted_ids = self.file_treeview.selection()
        if right_clicked_id in highlighted_ids:
            pass
        else:
            highlighted_ids = (right_clicked_id,)
            self.file_treeview.selection_set(highlighted_ids)
            self.file_treeview.focus(right_clicked_id)

        self.set_context()
        self.r_click_menu.set_current_selected()
        self.r_click_menu.popup(event)

    def _select_single(self, event):
        sid = self.file_treeview.identify_row(event.y)
        self.file_treeview.selection_set(sid)

    def _select_multiple(self, event):
        print("woo!")
        sid = self.file_treeview.identify_row(event.y)
        if sid in self.file_treeview.selection():
            self.file_treeview.selection_remove(sid)
        else:
            self.file_treeview.selection_add(sid)
        self._select_treeview_entry(event)

    def _select_treeview_entry(self, event):
        # currently needs to have the folder name and prefix the same (need to change!!!)                                   ###############
        # we also need to put some of this stuff in a separate thread as the function to change to selecting a folder currently takes longer than
        # the reasonable amount of time someone would wait to do a drag and drop event, so the function is being triggered
        sids = self.file_treeview.selection()
        self.set_context()
        self._clear_tags(event)
        t = threading.Thread(target=self._preload_data, args=[sids])
        t.start()

        # we won't have a problem with this yet since the data *has* to be preloaded
        # before we can do assignment of mrk's to con's
        if self.context == ('.CON',):
            self._highlight_associated_mrks(event)

    def _clear_tags(self, event):
        tag_list = ['ASSOC_FILES']
        for tag in tag_list:
            for sid in self.file_treeview.tag_has(tag):
                #tags = self.file_treeview.item(sid)['tags']
                #tags.remove(tag)
                self.file_treeview.item(sid, tags=[])

    # might want to make this function a bit more general to apply and remove generic modifcations
    def _highlight_associated_mrks(self, event):
        """
        Give any .mrk items that are associated with the selected .con file the 'ASSOC_FILES' tag.
        This will case them to be automatically drawn in a different colour
        """

        id_ = self.selected_files[0]
        con_file = self.preloaded_data.get(id_, None)
        # we will have None if the preloading of the data isn't complete
        # if this is so, return, and this function will be called again on completion of the preloading
        if con_file is not None:
            # get the associated mrk files if any
            for mrk_file in con_file.required_info['associated_mrks']:
                # these are mrk_file objects, so their id will be the id of their entry in the treeview
                self.file_treeview.item(mrk_file.ID, tags=['ASSOC_FILES'])
        else:
            return

    def set_context(self):
        """
        ctx describes the context under which the menu was evoked
        the options are:
        'GROUP'
        'SINGLE'
        '<dtype>' (where dtype is a particular data type, eg '.con')
        'MIXED' (used in conjunction with a 'GROUP' type)
        we can also have multiple contexts specified as entries of a tuple
        """
        if self.prev_selected_files != self.selected_files:
            # assign the previous set of selected files if they have changed
            self.prev_selected_files = self.selected_files
        # now get the current set of selected files
        self.selected_files = self.file_treeview.selection()
        if len(self.selected_files) > 1:
            dtypes = set()
            for _ in self.selected_files:
                dtypes.add(self.file_treeview.item(self.selected_files[0])['values'][0])
            if len(dtypes) == 1:
                # get the only data type selected to indicate all are the same
                self.context = ("GROUP", dtypes.pop().upper())
            else:
                # this indicates we have a mixed set of data types
                self.context = ("GROUP", "MIXED")
        elif len(self.selected_files) == 1:
            # only a single file is selected. Determine the data type if any
            dtype = self.file_treeview.item(self.selected_files[0])['values'][0]
            if dtype != '':
                self.context = (dtype.upper(),)
            else:
                self.context = ('FOLDER',)
        else:
            self.context = None

    def _preload_data(self, sids):
        # this function will load the file information
        # we have this as a separate function so it can be threaded to avoid locking up the GUI's main thread
        # This takes a list of sids (should be the files that are selected, but doesn't have to) and loads
        # any that aren't already in the preloaded data

        for id_ in sids:
            data = self.preloaded_data.get(id_, None)
            if data is not None:
                # data is already preloaded. Move onto the next id
                continue
            else:
                ext, path_ = self.file_treeview.item(id_)['values']
                if path.isdir(path_):
                    # create the info container
                    IC = InfoContainer(id_, path_, self)
                    # then add it to the list of preloaded data
                    self.preloaded_data[id_] = IC
                else:
                    # get the class for the extension
                    cls_ = get_object_class(ext)
                    # if we don't have a folder then instantiate the class
                    if not isinstance(cls_, str):
                        obj = cls_(id_, path_, self)
                        # if it is of generic type, give it it's data type and let it determine whether it is an unknown file type or not
                        if isinstance(obj, generic_file):
                            obj.dtype = ext
                        # finally, add the object to the preloaded data
                        self.preloaded_data[id_] = obj
        self._populate_info_panel(sids)

    def _get_data_location(self):
        self.settings["DATA_PATH"] = filedialog.askdirectory(title = "Select the parent folder containing the data")
        self._write_settings()

    def _get_matlab_location(self):
        self.settings["MATLAB_PATH"] = filedialog.askopenfilename(title = "Select the matlab executable")#, filetypes=(("exe", "*.exe")))
        self._write_settings()

    def get_selection_info(self):
        data = []
        for sid in self.file_treeview.selection():
            data.append(self.file_treeview.item(sid))
        return data

    def set_treeview_mode(self, mode):
        self.treeview_select_mode = mode

    def _quit(self):
        self.master.destroy()

class ProgressPopup(Toplevel):
    def __init__(self, master, progress_var):
        self.master = master
        Toplevel.__init__(self, self.master)

        self.progress_var = progress_var

        self._create_widgets()

    def _create_widgets(self):
        main_frame = Frame(self)
        Label(main_frame, text="Progress: ").grid(column=0, row=0)
        Label(main_frame, textvariable=self.progress_var).grid(column=1, row=0)
        main_frame.grid()
        #self.grid()
        print('woahh!!')

class RightClick():
    def __init__(self, parent):
        self.parent = parent

        # create a popup menu
        self.popup_menu = Menu(self.parent, tearoff=0, postcommand=self._determine_entries)

        self.prev_selection = ()
        self.curr_selection = ()

        self.progress = StringVar()
        self.progress.set('None')

    def set_current_selected(self):
        # keep track of the files selected each time a right-click occurs
        if self.prev_selection != self.curr_selection:
            # assign the previous set of selected files if they have changed
            self.prev_selection = self.curr_selection
        # now get the current set of selected files
        self.curr_selection = self.parent.file_treeview.selection()

    def _determine_entries(self):
        if "FOLDER" in self.parent.context:
            entry = self.parent.preloaded_data[self.curr_selection[0]]
            if isinstance(entry, InfoContainer):
                if entry.check_bids_ready():
                    self.popup_menu.add_command(label="Convert to BIDS", command=self._folder_to_bids_threaded)
                    self.popup_menu.add_command(label="See progress", command=self.check_progress)

    def _add_options(self):
        # a context dependent function to only add options that are applicable to the current situation
        # first, remove any currently visible entries in the menu so we can draw only the ones required by the current context
        self.popup_menu.delete(0, self.popup_menu.index("end"))
        # now, draw the manu elements required depending on context
        if self.parent.treeview_select_mode == "NORMAL":
            if "FOLDER" not in self.parent.context:
                self.popup_menu.add_command(label="Associate", command=self._associate_mrk)
                self.popup_menu.add_command(label="Create Folder", command=self._create_folder)
            else:
                pass
                #self.popup_menu.add_command(label="Convert to BIDS", command=self._folder_to_bids)
        elif self.parent.treeview_select_mode.startswith("ASSOCIATE"):
            self.popup_menu.add_command(label="Associate", command=self._associate_mrk)
    
    def check_progress(self):
        # we will have problems if this is called while it already exists... maybe??
        self.progress_popup = ProgressPopup(self.parent, self.progress)

    def _folder_to_bids_threaded(self):
        sid = self.parent.file_treeview.selection()[0]
        self.progress_popup = ProgressPopup(self.parent, self.progress)
        t = threading.Thread(target=self._folder_to_bids, args=[sid])
        t.start()

    def _folder_to_bids(self, sid):
        selected_IC = self.parent.preloaded_data[sid]
        print(selected_IC.extra_data, 'extra data')
        # put the entire process in a thread because it takes a little while...
        for acq, raw_kit in selected_IC.raw_files.items():
            self.progress.set("Working on acquisition {0}".format(acq))
            target_folder = self.parent.file_treeview.item(sid)['values'][1]+'_BIDS'
            folder_parent = self.parent.file_treeview.parent(sid)
            raw_to_bids(selected_IC.subject_ID[1].get(),
                        selected_IC.task_name[1].get(),
                        raw_kit,
                        target_folder,
                        session_id=selected_IC.session_ID[1].get(),
                        acquisition=acq,
                        extra_data=selected_IC.extra_data[acq])
            new_folder_sid = self.parent.file_treeview.ordered_insert(folder_parent, text=path.basename(target_folder), values=['', target_folder])
            self.parent._fill_file_tree(new_folder_sid, target_folder)
            # set the message to done, but also close the window if it hasn't already been closed
        self.progress.set("Done")
        try:
            self.progress_popup.destroy()
        except:
            pass


    def _create_folder(self):
        """
        Create a folder at the currently open level. Clicking on a folder and selecting
        create folder will create a sibling folder, not child folder (not sure which to do?)
        """
        # get the current root depth
        if self.parent.context is not None:
            dir_ = path.dirname(self.parent.file_treeview.item(self.parent.selected_files[0])['values'][1])
            print(self.parent.file_treeview.parent(self.parent.selected_files[0]))
        else:
            dir_ = self.parent.settings['DATA_PATH']
        # ask the user for the folder name:
        folder_name = simpledialog.askstring("Folder Name", "Enter a folder Name:",
                                             parent = self.parent)
        # we will need to make sure the folder doesn't already exist at the selected level
        if folder_name is not None:
            # create the folder
            full_path = path.join(dir_, folder_name)
            _, exists_already = create_folder(full_path)
            print(full_path, exists_already)
            if not exists_already:
                try:
                    parent = self.parent.file_treeview.parent(self.parent.selected_files[0])
                except IndexError:
                    # we have clicked outside the tree. Set the parent as the root
                    parent = ''
                self.parent.file_treeview.ordered_insert(parent, values=['', str(full_path)], text=folder_name, open=False)
                print('folder created!!')
            else:
                print('Folder already exists!')

    def _associate_mrk(self):
        # allow the user to select an .mrk file if a .con file has been selected
        # (or vice-versa) and associate the mrk file with the con file
        if self.parent.treeview_select_mode == "NORMAL":
            # initialise the association process
            if '.MRK' in self.parent.context:
                messagebox.showinfo("Select", "Please select the .con file(s) associated with this file.\nOnce you have selected all required files, right click and press 'associate' again")
                self.parent.set_treeview_mode("ASSOCIATE-CON")
            elif '.CON' in self.parent.context:
                messagebox.showinfo("Select", "Please select the .mrk file(s) associated with this file.\nOnce you have selected all required files, right click and press 'associate' again")
                self.parent.set_treeview_mode("ASSOCIATE-MRK")
            else:
                messagebox.showerror("Error", "Invalid file selection")
        elif self.parent.treeview_select_mode.startswith("ASSOCIATE"):
            # complete the association process
            cont = False
            if self.parent.treeview_select_mode == "ASSOCIATE-CON":
                # in this case expect the user to have selected one or more .mrk files
                if ".CON" in self.parent.context:
                    # the previously selected files will be .mrk files:
                    mrk_files = [self.parent.preloaded_data[sid] for sid in self.prev_selection]
                    con_files = [self.parent.preloaded_data[sid] for sid in self.curr_selection]
                else:
                    cont = messagebox.askretrycancel("Error", "The files you selected are not valid.\nWould you like to select the correct .con files, or cancel?")
            elif self.parent.treeview_select_mode == "ASSOCIATE-MRK":
                # in this case expect the user to have selected one or more .mrk files
                if ".MRK" in self.parent.context:
                    # the previously selected files will be .con files:
                    con_files = [self.parent.preloaded_data[sid] for sid in self.prev_selection]
                    mrk_files = [self.parent.preloaded_data[sid] for sid in self.curr_selection]
                else:
                    cont = messagebox.askretrycancel("Error", "The files you selected are not valid.\nWould you like to select the correct .mrk files, or cancel?")

            # now associate the mrk files with the con files:
            for con_file_ in con_files:
                con_file_.required_info['associated_mrks'] = mrk_files
            if not cont:
                self.parent.set_treeview_mode("NORMAL") 

    def popup(self, event):
        self._add_options()
        self.popup_menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    m = main(master = root)
    m.mainloop()
        