from tkinter import Toplevel, StringVar, BooleanVar, IntVar, DISABLED, NORMAL
from tkinter import Button as tkButton
from tkinter.ttk import Frame, Label, Button, Checkbutton, Entry
import os.path as path
import pickle
from PIL import Image, ImageTk

from Biscuit.utils.constants import OSCONST
from Biscuit.CustomWidgets.InfoEntries import ValidatedEntry
from Biscuit.Management.wckToolTips import ToolTipManager

ttm = ToolTipManager()


class SettingsWindow(Toplevel):
    """
    The popup window that lists all the different project defaults.
    New defaults can be added for each project and are added to the
    WidgetTable
    """
    def __init__(self, master, settings):
        self.master = master
        Toplevel.__init__(self, self.master)
        self.withdraw()
        if master.winfo_viewable():
            self.transient(master)

        self.title('Biscuit Settings')

        self.settings_file = path.join(OSCONST.USRDIR,
                                       'settings.pkl')

        self.protocol('WM_DELETE_WINDOW', self.exit)

        self.lock_icon = Image.open(OSCONST.ICON_LOCK)
        self.lock_icon = ImageTk.PhotoImage(self.lock_icon)

        self.settings = settings

        self.show_assoc = BooleanVar(
            value=self.settings.get('SHOW_ASSOC_MESSAGE', True))
        self.proj_lines = IntVar(value=self.settings.get('PROJ_ROWS', 10))
        self.archive_path = StringVar(
            value=self.settings.get('ARCHIVE_PATH', None))
        self.chunk_freq = IntVar(value=self.settings.get('CHUNK_FREQ', 14))

        self._create_widgets()

        self.deiconify()
        self.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def _create_widgets(self):
        frame = Frame(self)
        frame.grid(sticky='nsew')

        # Option to show association message
        assoc_lbl = Label(frame, text='Show association message:')
        assoc_lbl.grid(column=0, row=0, sticky='ew')
        ttm.register(assoc_lbl,
                     'Whether or not to show a message with details on how '
                     'to associate .mrk and .con files.')
        assoc_chk = Checkbutton(frame, variable=self.show_assoc)
        assoc_chk.grid(column=1, row=0, columnspan=2, sticky='w', padx=2)

        # Option to set how many project settings are shown by default
        proj_lines_lbl = Label(frame,
                               text='Number of project settings to show:')
        proj_lines_lbl.grid(column=0, row=1, sticky='ew')
        ttm.register(proj_lines_lbl,
                     'The default number of projects to be shown in the '
                     '"Set defaults" window. To see the rest of the project '
                     'settings the window will have to be scrolled down.')
        self.proj_lines_entry = ValidatedEntry(frame,
                                               textvariable=self.proj_lines,
                                               force_dtype='int',
                                               highlightbackground=OSCONST.ENTRY_HLBG)
        self.proj_lines_entry.grid(column=1, row=1, columnspan=2, sticky='ew',
                                   padx=2)

        archive_lbl = Label(frame, text='Archive path:')
        archive_lbl.grid(column=0, row=2, sticky='ew')
        ttm.register(archive_lbl,
                     'Path to upload data for storage.')
        self.archive_entry = Entry(frame,
                                   textvariable=self.archive_path,
                                   state=DISABLED,
                                   width=50)
        self.archive_entry.grid(column=1, row=2, columnspan=2, sticky='ew',
                                padx=2)

        chunk_lbl = Label(frame, text='Chunking frequency:')
        chunk_lbl.grid(column=0, row=3, sticky='ew')
        ttm.register(chunk_lbl,
                     'How often to create a new BIDS folder locally.\n'
                     'For personal use this should be 0, indicating no '
                     'chunking.\nFor use in a lab this should be set the '
                     'frequency at which\nthe data is expected to be '
                     'backed up to an external archive if that occurs.\n'
                     'WARNING! This should be set up when first setting up '
                     'Biscuit.\nChanging wid-way through a year can have '
                     'unintended side-effects.')
        self.chunk_entry = ValidatedEntry(frame,
                                          textvariable=self.chunk_freq,
                                          state=DISABLED,
                                          force_dtype='int',
                                          highlightbackground=OSCONST.ENTRY_HLBG)
        self.chunk_entry.grid(column=1, row=3, padx=2, sticky='ew')
        week_lbl = Label(frame, text='(days)')
        week_lbl.grid(column=2, row=3, sticky='e')

        unlock_archive_btn = tkButton(frame, relief='flat', borderwidth=0,
                                      highlightthickness=0, takefocus=0,
                                      command=self._unlock_settings)
        unlock_archive_btn.config(image=self.lock_icon)
        unlock_archive_btn.grid(column=3, row=2, rowspan=2, padx=2,
                                sticky='nsew')

        exit_btn = Button(frame, text='Save and Exit',
                          command=self.save_and_exit)
        exit_btn.grid(column=0, row=4)

        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=0)
        frame.grid_columnconfigure(3, weight=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _unlock_settings(self):
        self.chunk_entry.config(state=NORMAL)
        self.archive_entry.config(state=NORMAL)

    def save_and_exit(self):
        self._write_settings()
        self.exit()

    def exit(self):
        # TODO: popup window notifying that any unsaved changes will be lost?
        self.withdraw()
        self.update_idletasks()
        self.master.focus_set()
        self.destroy()

    def _write_settings(self):
        self.settings['SHOW_ASSOC_MESSAGE'] = self.show_assoc.get()
        self.settings['ARCHIVE_PATH'] = self.archive_path.get()
        self.settings['CHUNK_FREQ'] = self.chunk_freq.get()
        self.settings['PROJ_ROWS'] = self.proj_lines.get()
        with open(self.settings_file, 'wb') as settings:
            pickle.dump(self.settings, settings)
