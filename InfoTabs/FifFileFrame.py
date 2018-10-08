from tkinter import StringVar, BooleanVar, DISABLED, NORMAL
from tkinter.ttk import Frame, Label, Separator, Button, Combobox, Entry
from CustomWidgets.InfoEntries import (InfoEntry, InfoLabel, InfoCheck,
                                       InfoChoice)
from CustomWidgets import WidgetTable
from Management import OptionsVar, convert, ToolTipManager

# assign the tool tip manager
tt = ToolTipManager()


class FifFileFrame(Frame):
    def __init__(self, master, settings, *args, **kwargs):
        self.master = master
        self.settings = settings
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
        self.activeshield_info = InfoLabel(self, 'Has Active Shielding',
                                           "False")
        self.activeshield_info.label.grid(column=0, row=4)
        self.activeshield_info.value.grid(column=1, row=4)

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
        self.sub_age_entry = InfoEntry(self, "Subject DOB", StringVar())
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
        self.sess_id_entry = InfoEntry(self, "Session ID", StringVar(),
                                       bad_values=[''],
                                       validate_cmd=None)
        self.sess_id_entry.label.grid(column=0, row=9, sticky='ew', pady=2)
        self.sess_id_entry.value.grid(column=1, row=9, sticky='ew', pady=2)
        self.task_info = InfoEntry(self, 'Task', StringVar(),
                                   bad_values=[''],
                                   validate_cmd=None)
        self.require_verification.append(self.task_info)
        self.task_info.label.grid(column=0, row=10, sticky='ew', pady=2)
        self.task_info.value.grid(column=1, row=10, sticky='ew', pady=2)
        self.acq_info = InfoEntry(self, 'Acquisition', StringVar(),
                                  bad_values=[''],
                                  validate_cmd=None)
        self.require_verification.append(self.acq_info)
        self.acq_info.label.grid(column=0, row=11, sticky='ew', pady=2)
        self.acq_info.value.grid(column=1, row=11, sticky='ew', pady=2)

        Separator(self, orient='horizontal').grid(column=0, row=12,
                                                  columnspan=2, sticky='ew')

        # optional info
        Label(self, text="Optional Information:").grid(column=0, row=13,
                                                       columnspan=2)
        self.is_emptyroom_info = InfoCheck(self, 'Is empty room',
                                           BooleanVar(),
                                           validate_cmd=None)
        self.is_emptyroom_info.label.grid(column=0, row=14)
        self.is_emptyroom_info.value.grid(column=1, row=14)
        self.has_emptyroom_info = InfoCheck(self, 'Has empty room',
                                            BooleanVar())
        self.has_emptyroom_info.label.grid(column=0, row=15)
        self.has_emptyroom_info.value.grid(column=1, row=15)

        # channels area (just to rename/set BIO channels)
        self.channel_table = WidgetTable(
            self,
            headings=["Channel name", "Type"],
            pattern=[StringVar, OptionsVar],
            widgets_pattern=[Entry, Combobox],
            adder_script=DISABLED,
            remove_script=DISABLED)
        self.channel_table.grid(sticky='nsew', column=3, row=7,
                                columnspan=2, rowspan=9)

        # bottom matter (BIDS conversion button)
        self.bids_gen_btn = Button(self, text="Generate BIDS",
                                   command=self.convert_to_bids,
                                   state=DISABLED)
        self.bids_gen_btn.grid(column=0, row=16)
        tt.register(self.bids_gen_btn, ("Convert session data to BIDS format"))

        self.grid()

    # !REMOVE
    def _check_bids_ready(self):
        """
        Check to see whether all contained files required to produce a
        bids-compatible file system have all the necessary data
        """
        if self._file.update_treeview():
            self.bids_gen_btn.config(state=NORMAL)
        else:
            self.bids_gen_btn.config(state=DISABLED)

    def convert_to_bids(self):
        convert(self.file, self.settings, self)

    def update_widgets(self):
        # update info
        self.channel_info.value = self.file.info['Channels']
        self.meas_date_info.value = self.file.info['Measurement date']
        self.activeshield_info.value = self.file.info['Has Active Shielding']
        # update subject info
        self.sub_id_entry.value = self.file.subject_ID
        self.sub_id_entry.validate_cmd = self.file.validate
        self.sub_age_entry.value = self.file.subject_age
        self.sub_gender_entry.value = self.file.subject_gender
        self.sub_group_entry.value = self.file.subject_group
        # update required info
        self.proj_name_entry.value = self.file.proj_name
        self.proj_name_entry.validate_cmd = self.file.validate
        self.sess_id_entry.value = self.file.session_ID
        self.task_info.value = self.file.task
        self.task_info.validate_cmd = self.file.validate
        self.acq_info.value = self.file.acquisition
        self.acq_info.validate_cmd = self.file.validate
        self.is_emptyroom_info.value = self.file.is_empty_room
        self.is_emptyroom_info.validate_cmd = self.file.validate
        self.has_emptyroom_info.value = self.file.has_empty_room
        # update channel table
        channel_data = []
        for ch in self.file.channel_info.values():
            channel_data.append([ch['ch_name'], ch['ch_type']])
        self.channel_table.set(channel_data)

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
        for widget in self.require_verification:
            widget.check_valid()
        self.file.validate()
