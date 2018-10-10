from tkinter import DISABLED, StringVar
from tkinter.ttk import Label, Separator, Button, Frame
from CustomWidgets.InfoEntries import InfoEntry, InfoChoice
from CustomWidgets import DateEntry
from Management import OptionsVar, convert, ToolTipManager

# assign the tool tip manager
ttm = ToolTipManager()


class SessionInfoFrame(Frame):
    def __init__(self, master, settings, parent=None, *args, **kwargs):
        self.master = master
        self.settings = settings
        self.parent = parent
        super(SessionInfoFrame, self).__init__(self.master, *args, **kwargs)

        self._file = None

        # a list of widgets that will require verification
        self.require_verification = []

        self._create_widgets()

    def _create_widgets(self):
        # first let's draw the headings:
        Label(self, text="Recording Session Info:").grid(column=0, row=0,
                                                         columnspan=2, pady=3)
        Separator(self, orient='vertical').grid(column=2, row=0, rowspan=7,
                                                sticky='ns', padx=5)
        Label(self, text="Participant Info:").grid(column=3, row=0,
                                                   columnspan=2, pady=3)
        Separator(self, orient='horizontal').grid(column=0, row=1,
                                                  columnspan=5, sticky='ew')

        # now draw the session info
        self.proj_name_entry = InfoEntry(self, "Project name", StringVar(),
                                         bad_values=[''],
                                         validate_cmd=None)
        self.require_verification.append(self.proj_name_entry)
        self.proj_name_entry.label.grid(column=0, row=2, sticky='ew', pady=2)
        self.proj_name_entry.value.grid(column=1, row=2, sticky='ew', pady=2)
        self.proj_name_entry.tooltip(
            "Name of project this collection of file belongs to.\n"
            "If you enter the name of a project listed in the project "
            "settings\n"
            "(Options > 'Set Defaults'), a number of values can be set by "
            "default.")
        self.sess_id_entry = InfoEntry(self, "Session ID", StringVar(),
                                       bad_values=[''],
                                       validate_cmd=None)
        self.sess_id_entry.label.grid(column=0, row=3, sticky='ew', pady=2)
        self.sess_id_entry.value.grid(column=1, row=3, sticky='ew', pady=2)
        self.require_verification.append(self.sess_id_entry)

        # now the subject info
        self.sub_id_entry = InfoEntry(self, "Subject ID", StringVar(),
                                      bad_values=[''],
                                      validate_cmd=None)
        self.sub_id_entry.label.grid(column=3, row=2, sticky='ew', pady=2)
        self.sub_id_entry.value.grid(column=4, row=2, sticky='ew', pady=2)
        self.require_verification.append(self.sub_id_entry)
        Label(self, text="Subject DOB").grid(column=3, row=3, sticky='ew',
                                             pady=2)
        self.sub_age_entry = DateEntry(self, ["", "", ""])
        self.sub_age_entry.grid(column=4, row=3, sticky='ew', pady=2)
        self.sub_gender_entry = InfoChoice(self, "Subject gender",
                                           OptionsVar())
        self.sub_gender_entry.label.grid(column=3, row=4, sticky='ew', pady=2)
        self.sub_gender_entry.value.grid(column=4, row=4, sticky='ew', pady=2)
        self.sub_group_entry = InfoChoice(self, "Subject group",
                                          OptionsVar())
        self.sub_group_entry.label.grid(column=3, row=5, sticky='ew', pady=2)
        self.sub_group_entry.value.grid(column=4, row=5, sticky='ew', pady=2)

        Separator(self, orient='horizontal').grid(column=0, row=6,
                                                  columnspan=5, sticky='ew')

        # finally any additional info that needs to be specified
        self.dewar_position_entry = InfoChoice(self, "Dewar Position",
                                               OptionsVar())
        self.dewar_position_entry.label.grid(column=0, row=7, sticky='ew',
                                             pady=2)
        self.dewar_position_entry.value.grid(column=1, row=7, sticky='ew',
                                             pady=2)
        self.bids_gen_btn = Button(self, text="Generate BIDS",
                                   command=self.convert_to_bids,
                                   state=DISABLED)
        self.bids_gen_btn.grid(column=3, row=7)
        ttm.register(self.bids_gen_btn,
                     ("Convert session data to BIDS format"))
        self.grid()

    def update_widgets(self):
        self.proj_name_entry.value = self.file.proj_name
        self.proj_name_entry.validate_cmd = self.file.check_valid
        self.sess_id_entry.value = self.file.session_ID
        self.sess_id_entry.validate_cmd = self.file.check_valid
        self.sub_id_entry.value = self.file.subject_ID
        self.sub_id_entry.validate_cmd = self.file.check_valid
        self.sub_age_entry.setvar(self.file.subject_age)
        self.sub_gender_entry.value = self.file.subject_gender
        self.sub_group_entry.value = self.file.subject_group
        self.dewar_position_entry.value = self.file.dewar_position

    def convert_to_bids(self):
        convert(self.file, self.settings, self.parent)

    """
    def _folder_to_bids(self):
        if self.file._create_raws():
            self.file._folder_to_bids()
        else:
            print("Error creating raw data required for BIDS conversion")
    """

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, value):
        if self.file is not None:
            self._file.associated_tab = None
        self._file = value
        self.file.associated_tab = self
        self.update_widgets()
        for widget in self.require_verification:
            widget.check_valid()
        if not self.file.validation_initialised:
            self.file.init_validation()
        #else:
        #    self.file.validate()
