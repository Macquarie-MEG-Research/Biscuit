from tkinter import Frame, StringVar, BooleanVar, IntVar, DISABLED
from tkinter.ttk import Label, Separator, Button
from CustomWidgets.InfoEntries import (InfoEntry, InfoLabel, InfoCheck,
                                       InfoChoice)
from Management import OptionsVar
from Management import ToolTipManager

# assign the tool tip manager
tt = ToolTipManager()


class FifFileFrame(Frame):
    def __init__(self, master, default_settings, *args, **kwargs):
        self.master = master
        self.default_settings = default_settings
        super(FifFileFrame, self).__init__(self.master, *args, **kwargs)

        self._file = None
        self.widgets_created = False

        self.require_verification = []

        self._create_widgets()

    def _create_widgets(self):
        # recording information
        Label(self, text="Recording Information:").grid(column=0, row=0,
                                                        columnspan=2)
        Separator(self, orient='horizontal').grid(column=0, row=1,
                                                  columnspan=5, sticky='ew')
        self.channel_info = InfoLabel(self, 'Channels', "None")
        self.channel_info.label.grid(column=0, row=2)
        self.channel_info.value.grid(column=1, row=2)
        self.meas_date_info = InfoLabel(self, 'Measurement date', "None")
        self.meas_date_info.label.grid(column=0, row=3)
        self.meas_date_info.value.grid(column=1, row=3)

        Separator(self, orient='vertical').grid(column=2, row=0,
                                                rowspan=7, sticky='ns')

        # subject info
        Label(self, text="Subject Information:").grid(column=3, row=0,
                                                      columnspan=2)
        self.sub_id_entry = InfoEntry(self, "Subject ID", StringVar(),
                                      bad_values=[''],
                                      validate_cmd=None)
        self.sub_id_entry.label.grid(column=3, row=2, sticky='ew', pady=2)
        self.sub_id_entry.value.grid(column=4, row=2, sticky='ew', pady=2)
        self.require_verification.append(self.sub_id_entry)
        self.sub_age_entry = InfoEntry(self, "Subject age", IntVar())
        self.sub_age_entry.label.grid(column=3, row=3, sticky='ew', pady=2)
        self.sub_age_entry.value.grid(column=4, row=3, sticky='ew', pady=2)
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

        # required information
        Label(self, text="Required Information:").grid(column=0, row=7,
                                                       columnspan=2)
        self.proj_name_entry = InfoEntry(self, "Project name", StringVar(),
                                         bad_values=[''],
                                         validate_cmd=None)
        self.require_verification.append(self.proj_name_entry)
        self.proj_name_entry.label.grid(column=0, row=8, sticky='ew', pady=2)
        self.proj_name_entry.value.grid(column=1, row=8, sticky='ew', pady=2)
        self.task_info = InfoEntry(self, 'Task', StringVar(),
                                   bad_values=[''],
                                   validate_cmd=None)
        self.task_info.label.grid(column=0, row=9)
        self.task_info.value.grid(column=1, row=9)
        self.acq_info = InfoEntry(self, 'Acquisition', StringVar(),
                                  bad_values=[''],
                                  validate_cmd=None)
        self.acq_info.label.grid(column=0, row=10)
        self.acq_info.value.grid(column=1, row=10)

        Separator(self, orient='horizontal').grid(column=0, row=11,
                                                  columnspan=2, sticky='ew')
        Label(self, text="Optional Information:").grid(column=0, row=12,
                                                       columnspan=2)
        self.is_junk_info = InfoCheck(self, 'Is junk', BooleanVar(),
                                      validate_cmd=None)
        self.is_junk_info.label.grid(column=0, row=13)
        self.is_junk_info.value.grid(column=1, row=13)
        self.is_emptyroom_info = InfoCheck(self, 'Is empty room',
                                           BooleanVar(),
                                           validate_cmd=None)
        self.is_emptyroom_info.label.grid(column=0, row=14)
        self.is_emptyroom_info.value.grid(column=1, row=14)
        self.has_emptyroom_info = InfoCheck(self, 'Has empty room',
                                            BooleanVar())
        self.has_emptyroom_info.label.grid(column=0, row=15)
        self.has_emptyroom_info.value.grid(column=1, row=15)

        self.bids_gen_btn = Button(self, text="Generate BIDS",
                                   command=self._file_to_bids,
                                   state=DISABLED)
        self.bids_gen_btn.grid(column=0, row=16)
        tt.register(self.bids_gen_btn, ("Convert session data to BIDS format"))

        self.grid()

    def _file_to_bids(self):
        pass

    def update_widgets(self):
        # update info
        self.channel_info.value = self._file.info['Channels']
        self.meas_date_info.value = self._file.info['Measurement date']
        # update subject info
        self.sub_id_entry.value = self._file.subject_ID
        self.sub_id_entry.validate_cmd = self._file.check_bids_ready
        self.sub_age_entry.value = self._file.subject_age
        self.sub_gender_entry.value = self._file.subject_gender
        self.sub_group_entry.value = self._file.subject_group
        # update required info
        self.proj_name_entry.value = self._file.proj_name
        self.proj_name_entry.validate_cmd = self._file.check_bids_ready
        self.task_info.value = self._file.task
        self.task_info.validate_cmd = self._file.check_complete
        self.acq_info.value = self._file.acquisition
        self.acq_info.validate_cmd = self._file.check_complete
        self.is_junk_info.value = self._file.is_junk
        self.is_junk_info.validate_cmd = self._file.check_complete
        self.is_emptyroom_info.value = self._file.is_empty_room
        self.is_emptyroom_info.validate_cmd = self._file.check_complete
        self.has_emptyroom_info.value = self._file.has_empty_room

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, value):
        # de-associate the tab of the out-going file (if any)
        if self._file is not None:
            self._file.associated_tab = None
        self._file = value
        # and then associate the incoming file
        self.file.associated_tab = self
        # re-assign the settings in case they have changed
        self.file.settings = self.file.settings
        self.update_widgets()
        if not self._file.is_good:
            self.acq_info.check_valid()
            self.task_info.check_valid()
