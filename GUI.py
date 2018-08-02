__author__ = "Matt Sanderson"

from tkinter import *
from tkinter import PanedWindow as tkPanedWindow
from tkinter import filedialog, simpledialog, messagebox
from tkinter.ttk import *

import pickle
import os.path as path
from os import listdir, makedirs

from platform import system as os_name

from mne_bids import raw_to_bids

from FileTypes import generic_file, con_file

from FileIO import create_folder
from CustomWidgets.EnhancedTreeview import EnhancedTreeview

from InfoContainer import InfoContainer
from InfoManager import InfoManager
from SaveManager import SaveManager
from Windows.SettingsWindow import SettingsWindow
from ClickContext import ClickContext

from utils import *

DEFAULTSETTINGS = {"DATA_PATH": "",
                   "MATLAB_PATH": "",
                   "SAVEFILE_PATH": "savedata.save",
                   "SHOW_ASSOC_MESSAGE": True}

root = Tk()
root.geometry("1080x600")


class main(Frame):
    def __init__(self, master):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self._check_exit)
        self.master.title("Biscuit")
        # this directory is weird because the cwd is the parent folder, not
        # the Biscuit folder. Maybe because vscode?
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
        # placed in this dictionary so that we can then avoid reloading it 
        # later as each load of data takes ~0.5s
        self.preloaded_data = dict()

        self._load_settings()

        self.save_handler = SaveManager(self, self.settings['SAVEFILE_PATH'])

        self.context = ClickContext()

        self.selected_files = None          # the current set of selected files
        # the previous set. Keep as a buffer in case it is needed
        # (it is for the file association!)
        self.prev_selected_files = None

        self.r_click_menu = RightClick(self, self.context)

        self._create_widgets()
        self._create_menus()

        self._drag_mode = None

        self._fill_file_tree('')

        #self.save_handler.load()

        # This dictionary will consist of keys which are the file paths to the
        # .con files, and the values will be a list of associated .mrk files.
        # All other files (.hsp, .elp) are automatically associated by name.
        self.file_groups = dict()

        # the different operating modes of the treeview.
        self.treeview_select_mode = "NORMAL"
        # This will allow us to put the treeview in different modes
        # (eg. select a file when prompted etc)
        # options: "ASSOCIATING", "NORMAL"

        # set some tag configurations
        self.file_treeview.tag_configure('ASSOC_FILES', foreground="Blue")
        self.file_treeview.tag_configure('BAD_FILE', foreground="Red")
        self.file_treeview.tag_configure('GOOD_FILE', foreground="Green")
        self.file_treeview.tag_configure('JUNK_FILE',
                                         font=(None, 8, 'overstrike'))

    def _fill_file_tree(self, parent, directory=None):
        """
        Iterate over the folder structure and list all the files in the
        treeview

        parent is the parent entry in the treeview ('' if the root)

        This function will need to be improved so that when multiple
        acquisitions are in a single folder it doesn't create multiple folders
        """
        if directory is None:
            # in this case we are at the root
            dir_ = self.settings["DATA_PATH"]
        else:
            dir_ = directory

        # create a mapping of full paths to id's
        curr_children = self.file_treeview.get_children(parent)
        file_list = dict(
            zip([self.file_treeview.item(child)['values'][1] for child in
                 curr_children], curr_children))

        # we want to put folders above files (it looks nicer!!)
        try:
            for file in listdir(dir_):
                fname, ext = path.splitext(file)
                fullpath = path.join(dir_, file)

                # need to check to see whether or not the file/folder already
                # exists in the tree:
                exists_id = file_list.get(fullpath, None)
                if path.isdir(fullpath):
                    if exists_id is None:
                        exists_id = self.file_treeview.ordered_insert(
                            parent, values=['', fullpath], text=fname,
                            open=False)
                    self._fill_file_tree(exists_id, directory=fullpath)
                else:
                    if exists_id is None:
                        self.file_treeview.insert(parent, 'end',
                                                  values=[ext, fullpath],
                                                  text=fname, open=False,
                                                  tags=(ext))
        except PermissionError:
            # user doesn't have sufficient permissions to open folder so it
            # won't be included
            pass

    def _load_settings(self):
        """
        Load the various settings the program will use to automatically
        populate information such as default trigger channels and project
        readme data
        """

        # first, attempt to load the settings file:
        try:
            with open('settings.pkl', 'rb') as settings:
                self.settings = pickle.load(settings)
            # we can compare the read settings and default ones to allow for
            # the settings file to automatically update itself if required.
            if self.settings.keys() != DEFAULTSETTINGS.keys():
                for setting in DEFAULTSETTINGS:
                    if self.settings.get(setting, None) is None:
                        self.settings[setting] = DEFAULTSETTINGS[setting]
        except FileNotFoundError:
            # in this case we have no settings file so we need to create a new
            # one
            self.settings = DEFAULTSETTINGS

        # also load the project settings which are the default settings to be
        # applied to various projects. These are identified by the project ID.
        try:
            with open('proj_settings.pkl', 'rb') as proj_settings:
                self.proj_settings = pickle.load(proj_settings)
        except FileNotFoundError:
            self.proj_settings = []

        # now we want to validate the settings tp ensure that the path
        # specified actually exists etc
        if not path.exists(self.settings["DATA_PATH"]):
            # the specified path for the data doesn't exist.
            # this is probably due to changing computer or something...
            # get the user to enter a new path
            self._get_data_location_initial()
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
        self.options_menu.add_command(label="Set data directory",
                                      command=self._get_data_location)
        self.options_menu.add_command(label="Matlab path",
                                      command=self._get_matlab_location)
        self.options_menu.add_command(label="Set defaults",
                                      command=self._display_defaults_popup)

        # finally, tell the GUI to include the menu bar
        self.master.config(menu=self.menu_bar)

    def _create_widgets(self):
        # create all the visual elements required

        # middle frame section
        main_frame = Frame(self.master)
        self.pw = tkPanedWindow(main_frame, orient=HORIZONTAL,
                                sashrelief=RIDGE, sashpad=1, sashwidth=4)
        # frame for the treeview
        treeview_frame = Frame(self.pw)
        self.file_treeview = EnhancedTreeview(treeview_frame,
                                              columns=["dtype", "filepath"],
                                              selectmode='extended',
                                              displaycolumns=["dtype"])
        self.file_treeview.enhance(allow_dnd=False,
                                   scrollbars=['y', 'x'],
                                   sortable=True,
                                   editable=False,
                                   leftclick=self._select_treeview_entry,
                                   rightclick=self._right_click_treeview_entry,
                                   multiclick=self._select_multiple)
        self.file_treeview.heading("#0", text="Directory Structure")
        self.file_treeview.heading("dtype", text="Type")
        self.file_treeview.column("dtype", width=50, minwidth=35,
                                  stretch=False)

        #self.file_treeview.bind('<ButtonPress-1>', self.column_check)
        #self.file_treeview.bind("<B1-Motion>", self.column_drag, add='+')

        self.file_treeview.pack(side=LEFT, fill=BOTH, expand=1)
        treeview_frame.grid(column=0, row=0, sticky="nsew")
        self.pw.add(treeview_frame)

        self.file_treeview.root_path = self.settings["DATA_PATH"]

        # frame for the notebook panel
        notebook_frame = Frame(self.pw)
        self.info_notebook = InfoManager(notebook_frame, self, self.context)
        self.info_notebook.determine_tabs()     # maybe wrap??
        self.info_notebook.pack(side=LEFT, fill=BOTH, expand=1)
        notebook_frame.grid(row=0, column=1, sticky="nsew")

        self.pw.add(notebook_frame)
        self.pw.grid(column=0, row=0, sticky="nsew")
        main_frame.grid(column=0, row=0, sticky="nsew")

        self.exitButton = Button(main_frame, text="Exit",
                                 command=self._check_exit)
        self.exitButton.grid(column=0, row=1, columnspan=2)

        # add resizing stuff:
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

    # not gonna worry about this for now...
    def column_check(self, event):
        print(self.file_treeview.identify_region(event.x, event.y), 'reg')
        if self.file_treeview.identify_region(event.x, event.y) == 'separator':
            self._drag_mode = 'separator'
            left_col = self.file_treeview.identify_column(event.x)
            right_col = '#{}'.format(int(left_col.lstrip('#')) + 1)
            print(left_col, right_col)
            print(self.file_treeview.column(left_col, 'width'))
            print(self.file_treeview.column(right_col, 'width'))

    # this either...
    def column_drag(self, event):
        if self._drag_mode == 'separator':
            print('hi')

    def _populate_info_panel(self, sids):
        """
        This will receive the list of all selected tree entries

        I *think* this can be removed by using the data property of the
        InfoManager
        """
        self.info_notebook.check_context()
        self.info_notebook.data = [
            self.preloaded_data.get(id_, None) for id_ in
            sids if self.preloaded_data.get(id_, None) is not None]
        # if the info panel needs to be redrawn, redraw it
        if self.info_notebook.requires_update:
            #self.info_notebook.populate()
            self.info_notebook.determine_tabs()

    def _right_click_treeview_entry(self, event):
        # have a separate function to wrap the call to the RightClick .popup
        # method.
        # This will allow us to do some logic to allow for nicer right-clicking
        # Ie. if you right click on an entry that is not the focus, we want it
        # to become the focus.
        # Otherwise if we right click on an entry that has focus we want to get
        # all objects that have focus.
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
        # Currently needs to have the folder name and prefix the same
        # (need to change!!!)                                   ###############
        # We also need to put some of this stuff in a separate thread as the
        # function to change to selecting a folder currently takes longer than
        # the reasonable amount of time someone would wait to do a drag and
        # drop event, so the function is being triggered
        sids = self.file_treeview.selection()
        self.set_context()
        self._clear_tags(event)
        self._preload_data(sids)

        # we won't have a problem with this yet since the data *has* to be
        # preloaded before we can do assignment of mrk's to con's
        if self.context == '.CON':
            self._highlight_associated_mrks(event)

    def _clear_tags(self, event):
        tag_list = ['ASSOC_FILES']
        for tag in tag_list:
            for sid in self.file_treeview.tag_has(tag):
                #tags = self.file_treeview.item(sid)['tags']
                #tags.remove(tag)
                self.file_treeview.item(sid, tags=[])

    # might want to make this function a bit more general to apply and remove
    # generic modifcations
    def _highlight_associated_mrks(self, event):
        """
        Give any .mrk items that are associated with the selected .con file the
        'ASSOC_FILES' tag.
        This will case them to be automatically drawn in a different colour
        """

        id_ = self.selected_files[0]
        con_file = self.preloaded_data.get(id_, None)
        # we will have None if the preloading of the data isn't complete
        # if this is so, return, and this function will be called again on
        # completion of the preloading
        if con_file is not None:
            # get the associated mrk files if any
            for mrk_file in con_file.associated_mrks:
                # these are mrk_file objects, so their id will be the id of
                # their entry in the treeview
                print(mrk_file.ID)
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
            dtypes = []
            for sid in self.selected_files:
                dtypes.append(
                    self.file_treeview.item(sid)['values'][0].upper())
            self.context.set(dtypes)
            """
            if len(dtypes) == 1:
                # get the only data type selected to indicate all are the same
                self.context.add(dtypes.pop().upper())
            else:
                # this indicates we have a mixed set of data types
                self.context = {"GROUP", "MIXED"}
            """
        elif len(self.selected_files) == 1:
            # only a single file is selected. Determine the data type if any
            dtype = self.file_treeview.item(
                self.selected_files[0])['values'][0]
            if dtype != '':
                self.context.set(dtype.upper())
            else:
                self.context.set('FOLDER')
        else:
            # set it as no context
            self.context.set()

    @threaded
    def _preload_data(self, sids):
        # this function will load the file information
        # This takes a list of sids (should be the files that are selected, but
        # doesn't have to) and loads any that aren't already in the preloaded
        # data

        for id_ in sids:
            data = self.preloaded_data.get(id_, None)
            if data is not None:
                if not data.loaded:
                    data.load_data()
                else:
                    # data is already preloaded. Move onto the next id
                    continue
            else:
                ext, path_ = self.file_treeview.item(id_)['values']
                if path.isdir(path_):
                    # create the info container
                    IC = InfoContainer(id_=id_, file_path=path_, parent=self,
                                       settings=self.proj_settings)
                    # then add it to the list of preloaded data
                    self.preloaded_data[id_] = IC
                else:
                    # get the class for the extension
                    cls_ = get_object_class(ext)
                    # if we don't have a folder then instantiate the class
                    if not isinstance(cls_, str):
                        obj = cls_(id_=id_, file=path_, parent=None,
                                   treeview=self.file_treeview)
                        # check to see if the parent is in the preloaded data
                        # and if so, set this as the parent:
                        if (self.file_treeview.parent(id_) in
                                self.preloaded_data):
                            obj.parent = self.preloaded_data[id_]
                        # if it is of generic type, give it it's data type and
                        # let it determine whether it is an unknown file type
                        # or not
                        if isinstance(obj, generic_file):
                            obj.dtype = ext
                        # finally, add the object to the preloaded data
                        self.preloaded_data[id_] = obj
        self._populate_info_panel(sids)
        return      # try to get thread to end??

    def _get_data_location_initial(self):
        self.settings["DATA_PATH"] = filedialog.askdirectory(
            title="Select the parent folder containing the data")
        self._write_settings()

    def _get_data_location(self):
        # get the path
        if messagebox.askokcancel(
            "Warning", ("Warning! Continuing will cause any save data to be "
                        "erased. This will  hopefully be fixed at some later "
                        "date, but for now, only continue if you are sure.")):
            self._get_data_location_initial()
            # but now we want to re-draw the treeview after clearing it
            self.file_treeview.delete(*self.file_treeview.get_children())
            self._fill_file_tree('')

    def _get_matlab_location(self):
        self.settings["MATLAB_PATH"] = filedialog.askopenfilename(
            title="Select the matlab executable")
        self._write_settings()

    def _display_defaults_popup(self):
        proj_settings = self.proj_settings.copy()
        self.options_popup = SettingsWindow(self, self.settings,
                                            self.proj_settings)
        if proj_settings != self.settings:
            for obj in self.preloaded_data.values():
                if isinstance(obj, InfoContainer):
                    obj.settings = self.proj_settings

    def get_selection_info(self):
        data = []
        for sid in self.file_treeview.selection():
            data.append(self.file_treeview.item(sid))
        return data

    def set_treeview_mode(self, mode):
        self.treeview_select_mode = mode

    def _check_exit(self):
        """
        This will check whether the user wants to exit without saving
        """
        check = CheckSavePopup(self.master)
        if check.result == "save":
            self.save_handler.save()
            self.master.destroy()
        elif check.result == "cancel":
            pass
        elif check.result == "exit":
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


class RightClick():
    def __init__(self, parent, context):
        self.parent = parent

        # create a popup menu
        self.popup_menu = Menu(self.parent, tearoff=0,
                               postcommand=self._determine_entries)

        self.prev_selection = ()
        self.curr_selection = ()

        self.progress = StringVar()
        self.progress.set('None')

        self.context = context

    def set_current_selected(self):
        # keep track of the files selected each time a right-click occurs
        if self.prev_selection != self.curr_selection:
            # assign the previous set of selected files if they have changed
            self.prev_selection = self.curr_selection
        # now get the current set of selected files
        self.curr_selection = self.parent.file_treeview.selection()

    """ Need to consolidate the _determine_entries and _add_options functions
    at some point """

    def _determine_entries(self):
        if "FOLDER" in self.context:
            entry = self.parent.preloaded_data[self.curr_selection[0]]
            if isinstance(entry, InfoContainer):
                if entry.check_bids_ready():
                    self.popup_menu.add_command(label="Convert to BIDS",
                                                command=self._folder_to_bids)
                    self.popup_menu.add_command(label="See progress",
                                                command=self.check_progress)
        # give the option to associate one or more mrk files with all con files
        if (".MRK" in self.context and
                not self.parent.treeview_select_mode.startswith("ASSOCIATE")):
            self.popup_menu.add_command(
                label="Associate with all",
                command=lambda: self._associate_mrk(all_=True))
        # Add an option mark all selected .con files as junk
        if ".CON" in self.context and not self.context.is_mixed:
            self.popup_menu.add_command(label="Ignore files",
                                        command=self._ignore_cons)
            self.popup_menu.add_command(label="Include files",
                                        command=self._include_cons)

    def _add_options(self):
        # a context dependent function to only add options that are applicable
        # to the current situation.
        # first, remove any currently visible entries in the menu so we can
        # draw only the ones required by the current context
        self.popup_menu.delete(0, self.popup_menu.index("end"))
        # now, draw the manu elements required depending on context
        if self.parent.treeview_select_mode == "NORMAL":
            if ("FOLDER" not in self.context and
                    self.context != set()):
                self.popup_menu.add_command(label="Create Folder",
                                            command=self._create_folder)
            if ('.CON' in self.context or '.MRK' in self.context):
                self.popup_menu.add_command(label="Associate",
                                            command=self._associate_mrk)
            else:
                pass
                #self.popup_menu.add_command(label="Convert to BIDS",
                # command=self._folder_to_bids)
        elif self.parent.treeview_select_mode.startswith("ASSOCIATE"):
            self.popup_menu.add_command(label="Associate",
                                        command=self._associate_mrk)

    def check_progress(self):
        # we will have problems if this is called while it already exists...
        # maybe??
        self.progress_popup = ProgressPopup(self.parent, self.progress)

    def _folder_to_bids(self):
        sid = self.parent.file_treeview.selection()[0]
        self.progress_popup = ProgressPopup(self.parent, self.progress)
        self._make_bids_folders(sid)

    @threaded
    def _make_bids_folders(self, sid):
        selected_IC = self.parent.preloaded_data[sid]
        #new_folder_sid = None
        bids_folder_sid = None
        bids_folder_path = path.join(self.parent.settings['DATA_PATH'], 'BIDS')
        for sid in self.parent.file_treeview.get_children():
            if self.parent.file_treeview.item(sid)['text'] == 'BIDS':
                bids_folder_sid = sid
                break
        if bids_folder_sid is None:
            # in this case it doesn't exist so make a new folder
            makedirs(bids_folder_path)
            bids_folder_sid = self.parent.file_treeview.ordered_insert(
                '', text='BIDS', values=('', bids_folder_path))

        for acq, raw_kit in selected_IC.raw_files.items():
            self.progress.set("Working on acquisition {0}".format(acq))
            target_folder = path.join(bids_folder_path,
                                      selected_IC.proj_name.get())

            # get the variables for the raw_to_bids conversion function:
            subject_id = selected_IC.subject_ID.get()
            task_name = selected_IC.task_name.get()
            sess_id = selected_IC.session_ID.get()

            extra_data = selected_IC.extra_data[acq]

            participant_data = {'age': selected_IC.subject_age.get(),
                                'gender': selected_IC.subject_gender.get(),
                                'group': selected_IC.subject_group.get()}

            if sess_id == '':
                sess_id = None
            emptyroom_path = ''

            # get the event data from the associated con files:
            for con in selected_IC.acq_con_map[acq]:
                trigger_channels, descriptions = con.get_trigger_channels()
                # assume there is only one for now??
                event_ids = dict(zip(descriptions,
                                     [int(i) for i in trigger_channels]))

                # also check to see if the file is meant to have an associated
                # empty room file
                if con.has_empty_room.get() is True:
                    # we will auto-construct a file path based on the date of
                    # creation of the con file
                    date_vals = con.info['Measurement date'].split('/')
                    date_vals.reverse()
                    date = ''.join(date_vals)
                    emptyroom_path = ('sub-emptyroom/ses-{0}/meg/'
                                      'sub-emptyroom_ses-{0}_task-'
                                      'noise_meg.con'.format(date))

            if acq == 'emptyroom':
                emptyroom = True
            else:
                if emptyroom_path != '':
                    emptyroom = emptyroom_path
                else:
                    emptyroom = False

            con = selected_IC.acq_con_map[acq][0]
            mrks = [mrk.file for mrk in con.associated_mrks]

            # finally, run the actual conversion
            raw_to_bids(subject_id, task_name, raw_kit, target_folder,
                        electrode=selected_IC.contained_files['.elp'][0].file,
                        hsp=selected_IC.contained_files['.hsp'][0].file,
                        hpi=mrks, session_id=sess_id, acquisition=acq,
                        emptyroom=emptyroom, extra_data=extra_data,
                        event_id=event_ids, participant_data=participant_data)
        # fill the tree all at once??
        self.parent._fill_file_tree(bids_folder_sid, bids_folder_path)
        # set the message to done, but also close the window if it hasn't
        # already been closed
        self.progress.set("Done")
        try:
            self.progress_popup.destroy()
        except:
            pass

    def _ignore_cons(self):
        """
        Set all selected con files to have 'Is Junk' as True
        """
        for sid in self.curr_selection:
            con = self.parent.preloaded_data.get(sid, None)
            if con is not None:
                if isinstance(con, con_file):
                    con.is_junk.set(True)
                    con.check_complete()

    def _include_cons(self):
        """
        Set all selected con files to have 'Is Junk' as False
        """
        for sid in self.curr_selection:
            con = self.parent.preloaded_data.get(sid, None)
            if con is not None:
                if isinstance(con, con_file):
                    con.is_junk.set(False)
                    con.check_complete()

    def _create_folder(self):
        """
        Create a folder at the currently open level. Clicking on a folder and
        selecting "create folder" will create a sibling folder, not child
        folder (not sure which to do?)
        """
        # get the current root depth
        if self.context != set():        # maybe??
            dir_ = path.dirname(
                self.parent.file_treeview.item(
                    self.parent.selected_files[0])['values'][1])
        else:
            dir_ = self.parent.settings['DATA_PATH']
        # ask the user for the folder name:
        folder_name = simpledialog.askstring("Folder Name",
                                             "Enter a folder Name:",
                                             parent=self.parent)
        # we will need to make sure the folder doesn't already exist at the
        # selected level
        if folder_name is not None:
            # create the folder
            full_path = path.join(dir_, folder_name)
            _, exists_already = create_folder(full_path)
            if not exists_already:
                try:
                    parent = self.parent.file_treeview.parent(
                        self.parent.selected_files[0])
                except IndexError:
                    # we have clicked outside the tree. Set the parent as the
                    # root
                    parent = ''
                self.parent.file_treeview.ordered_insert(
                    parent, values=['', str(full_path)], text=folder_name,
                    open=False)
                print('folder created!!')
            else:
                print('Folder already exists!')

    def _associate_mrk(self, all_=False):
        # allow the user to select an .mrk file if a .con file has been
        # selected (or vice-versa) and associate the mrk file with the con file
        con_files = []
        if all_ and self.parent.treeview_select_mode == "NORMAL":
            mrk_files = [self.parent.preloaded_data[sid] for sid in
                         self.curr_selection]
            # get the parent folder and then find all .con file children
            parent = self.parent.file_treeview.parent(mrk_files[0].ID)
            IC = self.parent.preloaded_data[parent]
            for con in IC.contained_files['.con']:
                con.associated_mrks = mrk_files
                con.check_complete()
        else:
            if self.parent.treeview_select_mode == "NORMAL":
                # initialise the association process
                if '.MRK' in self.context and not self.context.is_mixed:
                    messagebox.showinfo(
                        "Select", ("Please select the .con file(s) associated "
                                   "with this file.\nOnce you have selected "
                                   "all required files, right click and press "
                                   "'associate' again"))
                    self.parent.set_treeview_mode("ASSOCIATE-CON")
                elif '.CON' in self.context and not self.context.is_mixed:
                    messagebox.showinfo(
                        "Select", ("Please select the .mrk file(s) associated "
                                   "with this file.\nOnce you have selected "
                                   "all required files, right click and press "
                                   "'associate' again"))
                    self.parent.set_treeview_mode("ASSOCIATE-MRK")
                else:
                    messagebox.showerror("Error", "Invalid file selection")
            elif self.parent.treeview_select_mode.startswith("ASSOCIATE"):
                # complete the association process
                cont = None
                if self.parent.treeview_select_mode == "ASSOCIATE-CON":
                    # in this case expect the user to have selected one or
                    # more .mrk files
                    if ".CON" in self.context and not self.context.is_mixed:
                        # the previously selected files will be .mrk files:
                        mrk_files = [self.parent.preloaded_data[sid] for sid in
                                     self.prev_selection]
                        con_files = [self.parent.preloaded_data[sid] for sid in
                                     self.curr_selection]
                    else:
                        cont = messagebox.askretrycancel(
                            "Error", ("The files you selected are not valid.\n"
                                      "Would you like to select the correct "
                                      ".con files, or cancel?"))
                elif self.parent.treeview_select_mode == "ASSOCIATE-MRK":
                    # in this case expect the user to have selected one or more
                    #  .mrk files
                    if ".MRK" in self.context and not self.context.is_mixed:
                        # the previously selected files will be .con files:
                        con_files = [self.parent.preloaded_data[sid] for sid in
                                     self.prev_selection]
                        mrk_files = [self.parent.preloaded_data[sid] for sid in
                                     self.curr_selection]
                    else:
                        cont = messagebox.askretrycancel(
                            "Error", ("The files you selected are not valid.\n"
                                      "Would you like to select the correct "
                                      ".mrk files, or cancel?"))

                # now associate the mrk files with the con files:
                if cont is None:
                    for cf in con_files:
                        cf.associated_mrks = mrk_files
                    # check if the con file is the currently selected file
                    if self.parent.treeview_select_mode == "ASSOCIATE-CON":
                        # if so, redraw the info panel and call the mrk
                        # association function so GUI is updated
                        self.parent.info_notebook.determine_tabs()
                        self.parent._highlight_associated_mrks(None)
                    self.parent.set_treeview_mode("NORMAL")
                if cont is False:
                    self.parent.set_treeview_mode("NORMAL")

    def popup(self, event):
        self._add_options()
        self.popup_menu.post(event.x_root, event.y_root)


class CheckSavePopup(simpledialog.Dialog):
    def body(self, master):
        Label(master, text=("Are you sure you want to exit? You may have "
                            "unsaved data...")).grid(row=0)

    def buttonbox(self):

        box = Frame(self)

        w = Button(box, text="Save and Exit", width=15, command=self.save,
                   default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Go back!", width=15, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Exit", width=15, command=self.exit)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def save(self, event=None):
        self.result = "save"
        self.end()

    def cancel(self, event=None):
        self.result = "cancel"
        self.end()

    def exit(self, event=None):
        self.result = "exit"
        self.end()

    def end(self):
        # close the dialog
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()


if __name__ == "__main__":
    m = main(master=root)
    m.mainloop()
