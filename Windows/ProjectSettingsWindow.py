from tkinter import Toplevel, StringVar, WORD, IntVar, END
from tkinter.ttk import Frame, Label, Entry, Button
from tkinter.scrolledtext import ScrolledText
from CustomWidgets import DateEntry
from CustomWidgets.InfoEntries import InfoEntry
from CustomWidgets.WidgetTable import WidgetTable


class ProjectSettingsWindow(Toplevel):
    """Window to add new project settings"""
    def __init__(self, master, settings=dict()):
        self.master = master
        Toplevel.__init__(self, self.master)
        self.withdraw()
        if master.winfo_viewable():
            self.transient(master)

        self.title('Add Project Settings')

        # do some more popup window management
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.settings = settings

        # declare all the variables required:
        self.project_title = StringVar()
        self.project_title.set(self.settings.get('ProjectTitle', ''))
        self.project_id = StringVar()
        self.project_id.set(self.settings.get('ProjectID', ''))

        self._create_widgets()

        self.deiconify()
        self.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def _create_widgets(self):
        # draw all the widgets
        self.frame = Frame(self)
        self.frame.grid(sticky='nsew')

        self.pt_entry = InfoEntry(self.frame, "Project Title",
                                  self.project_title)
        self.pt_entry.label.grid(column=0, row=0, pady=2, padx=2)
        self.pt_entry.value.grid(column=1, row=0, pady=2, padx=2)
        self.pid_entry = InfoEntry(self.frame, "Project ID",
                                   self.project_id)
        self.pid_entry.label.grid(column=2, row=0, pady=2, padx=2)
        self.pid_entry.value.grid(column=3, row=0, pady=2, padx=2)
        Label(self.frame, text="Start Date:").grid(
            column=0, row=1, pady=2, padx=2)
        self.sd_entry = DateEntry(
            self.frame, text=self.settings.get('StartDate', ['', '', '']))
        self.sd_entry.grid(column=1, row=1, pady=2, padx=2)
        Label(self.frame, text="End Date:").grid(
            column=2, row=1, pady=2, padx=2)
        self.ed_entry = DateEntry(
            self.frame, text=self.settings.get('EndDate', ['', '', '']))
        self.ed_entry.grid(column=3, row=1, pady=2, padx=2)
        Label(self.frame, text="Project description:").grid(
            column=0, row=2, padx=2, pady=2)
        self.desc_entry = ScrolledText(self.frame, wrap=WORD)
        self.desc_entry.grid(column=0, columnspan=4, row=3, rowspan=5,
                             sticky='nsew')
        self.desc_entry.insert(END, self.settings.get('Description', ''))
        self.channels_table = WidgetTable(
            self.frame, headings=["Trigger Channel", "Event Description"],
            pattern=[IntVar, StringVar],
            widgets_pattern=[Entry, Entry],
            add_options=None,
            data_array=self.settings.get('DefaultTriggers', []),
            sort_column=0)
        self.channels_table.grid(column=0, columnspan=2, row=8, sticky='nsew')
        self.groups_table = WidgetTable(
            self.frame, headings=["Group"],
            pattern=[StringVar],
            widgets_pattern=[Entry],
            add_options=None,
            data_array=self.settings.get('Groups', []))
        self.groups_table.grid(column=2, columnspan=2, row=8, sticky='nsew')

        self.save_btn = Button(self.frame, text="Save",
                               command=self._write_settings)
        self.save_btn.grid(column=4, row=9)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)
        self.frame.grid_columnconfigure(4, weight=0)
        self.frame.grid_rowconfigure(0, weight=0)
        self.frame.grid_rowconfigure(1, weight=0)
        self.frame.grid_rowconfigure(2, weight=0)
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_rowconfigure(8, weight=1)
        self.frame.grid_rowconfigure(9, weight=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def get_settings(self):
        """
        Retreive all the information from all the various fields and
        write to the settings dictionary
        """
        self.settings['ProjectID'] = self.project_id.get()
        self.settings['ProjectTitle'] = self.project_title.get()
        self.settings['StartDate'] = self.sd_entry.get()
        self.settings['EndDate'] = self.ed_entry.get()
        self.settings['Description'] = self.desc_entry.get("1.0", "end-1c")
        self.settings['DefaultTriggers'] = self.channels_table.get()
        self.settings['Groups'] = self.groups_table.get()

    def cancel(self):
        # set the settings as blank and leave
        self.settings = dict()
        #self.initial_focus = None
        Toplevel.destroy(self)

    def _write_settings(self):
        self.get_settings()
        self.withdraw()
        self.update_idletasks()
        self.master.focus_set()
        Toplevel.destroy(self)
