__author__ = "Matt Sanderson"

from tkinter import Tk, PhotoImage, Menu, TclError
from tkinter import HORIZONTAL, RIDGE, LEFT, BOTH
from tkinter import PanedWindow as tkPanedWindow
from tkinter import filedialog, messagebox
from tkinter.ttk import Frame, Style, Button, Label

from copy import deepcopy
import pickle
import os.path as path
from os import listdir, makedirs

import webbrowser
from webbrowser import open_new as open_hyperlink

from FileTypes import generic_file, Folder, KITData, BIDSFile, BIDSContainer

from CustomWidgets import FileTreeview

from Management import ClickContext
from Management.RightClickManager import RightClick
from Management.InfoManager import InfoManager
from Management.SaveManager import SaveManager
from Windows import SettingsWindow, ProgressPopup, CheckSavePopup, CreditsPopup

from utils.utils import threaded, get_object_class

from utils.constants import OSCONST

DEFAULTSETTINGS = {"DATA_PATH": "",
                   "SHOW_ASSOC_MESSAGE": True}

root = Tk()

style = Style()


class main(Frame):
    def __init__(self, master):
        self.master = master

        self.master.withdraw()
        if self.master.winfo_viewable():
            self.master.transient()

        self.master.protocol("WM_DELETE_WINDOW", self._check_exit)
        self.master.title("Biscuit")
        try:
            img = PhotoImage(file=OSCONST.ICON)
        except TclError:
            img = PhotoImage(file=OSCONST.ICON_GIF)
        self.master.tk.call('wm', 'iconphoto', self.master._w, img)
        self.treeview_text_size = OSCONST.TREEVIEW_TEXT_SIZE
        Frame.__init__(self, self.master)

        self.proj_settings_file = path.join(OSCONST.USRDIR,
                                            'proj_settings.pkl')
        self.settings_file = path.join(OSCONST.USRDIR, 'settings.pkl')

        # sort out some styling
        style.configure("Treeview", font=("TkTextFont",
                                          self.treeview_text_size))

        # this will be a dictionary containing any preloaded data from MNE
        # when we click on a folder to load its information, the object will be
        # placed in this dictionary so that we can then avoid reloading it
        # later as each load of data takes ~0.5s
        self.preloaded_data = dict()

        self._load_settings()

        self.save_handler = SaveManager(self)

        self.context = ClickContext()

        self.selected_files = None          # the current set of selected files
        # the previous set. Keep as a buffer in case it is needed
        # (it is for the file association!)
        self.prev_selected_files = None

        self.r_click_menu = RightClick(self, self.context)

        self._create_widgets()
        self._create_menus()

        self._drag_mode = None
        self.progress_popup = None

        self.file_treeview.generate('', self.settings["DATA_PATH"])

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
        self.file_treeview.tag_configure(
            'JUNK_FILE', font=("TkTextFont", self.treeview_text_size,
                               'overstrike'))

        self.save_handler.load()

        self.master.deiconify()
        self.focus_set()

        self.update_idletasks()

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        screen_dimensions = "{0}x{1}+20+20".format(screen_width - 200,
                                                   screen_height - 200)
        root.geometry(screen_dimensions)

    def _load_settings(self):
        """
        Load the various settings the program will use to automatically
        populate information such as default trigger channels and project
        readme data
        """

        # first, attempt to load the settings file:
        try:
            with open(self.settings_file, 'rb') as settings:
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
            with open(self.proj_settings_file, 'rb') as proj_settings:
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

        #if not path.exists(self.settings["MATLAB_PATH"]):
        #    self._get_matlab_location()

    def _write_settings(self):
        if not path.exists(path.dirname(self.settings_file)):
            makedirs(path.dirname(self.settings_file))
        with open(self.settings_file, 'wb') as settings:
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
        #self.options_menu.add_command(label="Matlab path",
        #                              command=self._get_matlab_location)
        self.options_menu.add_command(label="Set defaults",
                                      command=self._display_defaults_popup)

        # info menu
        self.info_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Info", menu=self.info_menu)

        self.info_menu.add_command(label="Credits",
                                   command=self._display_credits_popup)
        self.info_menu.add_command(label="Help",
                                   command=self._load_help_link)
        self.info_menu.add_command(label="Open Settings Folder",
                                   command=self._open_settings)

        # finally, tell the GUI to include the menu bar
        self.master.config(menu=self.menu_bar)

    def _create_widgets(self):
        """ create all the visual elements required """

        # middle frame section
        main_frame = Frame(self.master)
        self.pw = tkPanedWindow(main_frame, orient=HORIZONTAL,
                                sashrelief=RIDGE, sashpad=1, sashwidth=4)
        # frame for the treeview
        treeview_frame = Frame(self.pw)
        self.file_treeview = FileTreeview(treeview_frame,
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

        # frame at the bottom to place all the buttons in
        bottomFrame = Frame(main_frame)
        bottomFrame.grid(column=0, row=1, sticky='nsew')

        self.refreshButton = Button(bottomFrame, text="Refresh",
                                    command=self._refresh_filetree)
        self.refreshButton.grid(column=0, row=0, sticky='w', padx=50)

        buttonFrame = Frame(bottomFrame)
        buttonFrame.grid(column=1, row=0, sticky='w')

        self.save_label = Label(buttonFrame,
                                textvar=self.save_handler.saved_time)
        self.save_label.grid(column=0, row=0, padx=5)
        self.saveButton = Button(buttonFrame, text="Save",
                                 command=lambda: self.save_handler.save())
        self.saveButton.grid(column=1, row=0, padx=5)
        self.exitButton = Button(buttonFrame, text="Exit",
                                 command=self._check_exit)
        self.exitButton.grid(column=2, row=0, padx=5)

        # add resizing stuff:
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        bottomFrame.columnconfigure(0, weight=1)
        bottomFrame.columnconfigure(1, weight=1)

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

        sid = self.file_treeview.identify_row(event.y)
        if sid in self.file_treeview.selection():
            self.file_treeview.selection_remove(sid)
        else:
            self.file_treeview.selection_add(sid)
        self._select_treeview_entry(event)

    def _select_treeview_entry(self, *event):
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

    def _clear_tags(self, *event):
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
        self._clear_tags()
        if con_file is not None:
            # get the associated mrk files if any
            for mrk_file in con_file.hpi:
                # these are mrk_file objects, so their id will be the id of
                # their entry in the treeview
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
        elif len(self.selected_files) == 1:
            # only a single file is selected. Determine the data type if any
            dtype = self.file_treeview.item(
                self.selected_files[0])['values'][0]
            file_path = self.file_treeview.item(
                self.selected_files[0])['values'][1]
            if path.isdir(file_path):
                self.context.set('FOLDER')
            else:
                self.context.set(dtype.upper())
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
                    # create a Folderlike object (Folder or KITData)
                    is_KIT = KITData.generate_file_list(
                        id_, self.file_treeview, validate=True)
                    if is_KIT:
                        folder = KITData(id_, path_, self.proj_settings, self)
                    else:
                        folder = Folder(id_, path_, self)
                    folder.initial_processing()
                    # then add it to the list of preloaded data
                    self.preloaded_data[id_] = folder
                else:
                    # get the class for the extension
                    cls_ = get_object_class(ext)
                    # if we don't have a folder then instantiate the class
                    if not isinstance(cls_, str):
                        if issubclass(cls_, BIDSFile):
                            obj = cls_(id_=id_, file=path_,
                                       settings=self.proj_settings,
                                       parent=self)
                        else:
                            obj = cls_(id_=id_, file=path_, parent=self)
                        # if it is of generic type, give it it's data type and
                        # let it determine whether it is an unknown file type
                        # or not
                        if isinstance(obj, generic_file):
                            obj.dtype = ext
                        try:
                            obj.load_data()
                        except IOError:
                            pass
                    else:
                        obj = generic_file(id_=id_, file=path_,
                                           parent=self)
                        obj.dtype = ext
                    # finally, add the object to the preloaded data
                    self.preloaded_data[id_] = obj

        # set the info tab's data to be the list of selected data
        self.info_notebook.data = [
            self.preloaded_data.get(id_, None) for id_ in
            sids if self.preloaded_data.get(id_, None) is not None]
        return

    def _check_KIT_folder(self, id_):
        """ Determine whether the folder contains valid KIT data """
        files = {'.con': [],
                 '.mrk': [],
                 '.elp': [],
                 '.hsp': []}

        # go through the direct children of the folder via the treeview
        for sid in self.file_treeview.get_children(id_):
            item = self.file_treeview.item(sid)
            ext = item['values'][0]

            if ext in files:
                files[ext].append(id_)

        # validate the folder:
        for data in files.values():
            if len(data) == 0:
                return False
        return True

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
            self.file_treeview.generate('', self.settings["DATA_PATH"])

    def _get_matlab_location(self):
        self.settings["MATLAB_PATH"] = filedialog.askopenfilename(
            title="Select the matlab executable")
        self._write_settings()

    def _display_defaults_popup(self):
        proj_settings = deepcopy(self.proj_settings)
        self.options_popup = SettingsWindow(self, self.settings,
                                            self.proj_settings)
        if proj_settings != self.proj_settings:
            for obj in self.preloaded_data.values():
                if isinstance(obj, BIDSContainer):
                    obj.settings = self.proj_settings

    def _display_credits_popup(self):
        CreditsPopup(self)

    def _load_help_link(self):
        open_hyperlink("https://macquarie-meg-research.github.io/Biscuit/")

    def _open_settings(self):
        webbrowser.open('file://{0}'.format(OSCONST.USRDIR))

    def get_selection_info(self):
        data = []
        for sid in self.file_treeview.selection():
            data.append(self.file_treeview.item(sid))
        return data

    def set_treeview_mode(self, mode):
        self.treeview_select_mode = mode

    def check_progress(self, progress):
        if not self.progress_popup:
            # TODO: this is broken but we might not even want to call it from
            # here anyway...?
            self.progress_popup = ProgressPopup(self, progress, None)

    def _refresh_filetree(self):
        print('refresh')

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


if __name__ == "__main__":
    m = main(master=root)
    m.mainloop()
