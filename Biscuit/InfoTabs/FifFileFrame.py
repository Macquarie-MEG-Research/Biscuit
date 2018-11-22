from tkinter import (StringVar, BooleanVar, DISABLED, NORMAL, Entry,
                     messagebox, IntVar)
from tkinter.ttk import Frame, Label, Separator, Button, Combobox

from Biscuit.CustomWidgets.InfoEntries import (InfoEntry, InfoLabel, InfoCheck,
                                               InfoChoice)
from Biscuit.CustomWidgets import WidgetTable, DateEntry
from Biscuit.Management import OptionsVar, convert, ToolTipManager

# assign the tool tip manager
ttm = ToolTipManager()


class FifFileFrame(Frame):
    def __init__(self, master, settings, parent=None, *args, **kwargs):
        self.master = master
        self.settings = settings
        self.parent = parent
        super(FifFileFrame, self).__init__(self.master, *args, **kwargs)

        self._file = None
        self.widgets_created = False

        self.require_verification = []

        self._create_widgets()

        self.current_job_thread = None

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
                                                rowspan=16, sticky='ns')

        # subject info
        Label(self, text="Subject Information:").grid(column=3, row=0,
                                                      columnspan=2)
        self.sub_id_entry = InfoEntry(self, "Subject ID", StringVar(),
                                      bad_values=[''],
                                      validate_cmd=None)
        self.sub_id_entry.label.grid(column=3, row=2, sticky='ew', pady=2,
                                     padx=2)
        self.sub_id_entry.value.grid(column=4, row=2, sticky='ew', pady=2,
                                     padx=2)
        self.require_verification.append(self.sub_id_entry)
        Label(self, text="Subject DOB").grid(column=3, row=3, sticky='ew',
                                             pady=2, padx=2)
        self.sub_age_entry = DateEntry(self, ["", "", ""])
        self.sub_age_entry.grid(column=4, row=3, sticky='ew', pady=2, padx=2)
        self.sub_gender_entry = InfoChoice(self, "Subject gender",
                                           OptionsVar())
        self.sub_gender_entry.label.grid(column=3, row=4, sticky='ew', pady=2,
                                         padx=2)
        self.sub_gender_entry.value.grid(column=4, row=4, sticky='ew', pady=2,
                                         padx=2)
        self.sub_group_entry = InfoChoice(self, "Subject group",
                                          OptionsVar())
        self.sub_group_entry.label.grid(column=3, row=5, sticky='ew', pady=2,
                                        padx=2)
        self.sub_group_entry.value.grid(column=4, row=5, sticky='ew', pady=2,
                                        padx=2)

        Separator(self, orient='horizontal').grid(column=0, row=6,
                                                  columnspan=5, sticky='ew')

        # required information
        Label(self, text="Required Information:").grid(column=0, row=7,
                                                       columnspan=2)
        self.proj_id_entry = InfoEntry(self, "Project ID", StringVar(),
                                       bad_values=[''],
                                       validate_cmd=None)
        self.require_verification.append(self.proj_id_entry)
        self.proj_id_entry.label.grid(column=0, row=8, sticky='ew', pady=2,
                                      padx=2)
        self.proj_id_entry.value.grid(column=1, row=8, sticky='ew', pady=2,
                                      padx=2)
        self.proj_id_entry.tooltip(
            "ID of project this file belongs to.\n"
            "If you enter the ID of a project listed in the project "
            "settings\n"
            "(Options > 'Set Defaults'), a number of values can be set by "
            "default.")
        self.sess_id_entry = InfoEntry(self, "Session ID", StringVar(),
                                       bad_values=[''], force_dtype='alnum')
        self.sess_id_entry.label.grid(column=0, row=9, sticky='ew', pady=2,
                                      padx=2)
        self.sess_id_entry.value.grid(column=1, row=9, sticky='ew', pady=2,
                                      padx=2)
        self.sess_id_entry.tooltip(
            "ID of the session for the participant. Generally this will just "
            "be a number,\neg. 1, however a string may be used to be more "
            "descriptive.")
        self.require_verification.append(self.sess_id_entry)
        self.task_info = InfoChoice(self, 'Task', OptionsVar())
        self.task_info.label.grid(column=0, row=10, sticky='ew', pady=2,
                                  padx=2)
        self.task_info.value.grid(column=1, row=10, sticky='ew', pady=2,
                                  padx=2)
        self.run_info = InfoEntry(self, 'Run number', IntVar(),
                                  bad_values=['0', ''], force_dtype='int')
        self.require_verification.append(self.run_info)
        self.run_info.label.grid(column=0, row=11, sticky='ew', pady=2, padx=2)
        self.run_info.value.grid(column=1, row=11, sticky='ew', pady=2, padx=2)

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
        self.is_emptyroom_info.tooltip(
            "Indicates whether this file contains empty room data")
        self.has_emptyroom_info = InfoCheck(self, 'Has empty room',
                                            BooleanVar())
        self.has_emptyroom_info.label.grid(column=0, row=15)
        self.has_emptyroom_info.value.grid(column=1, row=15)
        self.has_emptyroom_info.tooltip(
            "Whether or not this file has an associated empty room file.\n"
            "Only check this if there actually exists a file with 'Is empty "
            "room' marked as True from the same day,\notherwise this will "
            "produce erroneous results.")

        # channels area (just to rename/set BIO channels)
        Label(self, text="Channel Data:").grid(column=3, row=7,
                                               columnspan=2)
        self.channel_table = WidgetTable(
            self,
            headings=["Channel name", "Type"],
            pattern=[StringVar, OptionsVar],
            widgets_pattern=[Entry, Combobox],
            adder_script=DISABLED,
            remove_script=DISABLED)
        self.channel_table.grid(sticky='nsew', column=3, row=8,
                                columnspan=2, rowspan=8)

        # bottom matter (BIDS conversion button)
        self.bids_gen_btn = Button(self, text="Generate BIDS",
                                   command=self.convert_to_bids,
                                   state=DISABLED)
        self.bids_gen_btn.grid(column=0, row=16)
        ttm.register(self.bids_gen_btn, "Convert session data to BIDS format")

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
        if self.current_job_thread is None:
            self.current_job_thread = convert(self.file, self.settings,
                                              self.parent)
        else:
            if self.current_job_thread.is_alive():      # pylint: disable=E1101
                messagebox.showerror("Job Already Running",
                                     "You already have one job running.\n"
                                     "Please wait until it has finished before"
                                     " starting a new one.")
            else:
                # in this case the job has ended so we nullify the current
                # job thread then re-run this function
                self.current_job_thread = None
                self.convert_to_bids()

    def update_widgets(self):
        # update info
        self.channel_info.value = self.file.info['Channels']
        self.meas_date_info.value = self.file.info['Measurement date']
        self.activeshield_info.value = self.file.info['Has Active Shielding']
        # update subject info
        self.sub_id_entry.value = self.file.subject_ID
        self.sub_age_entry.setvar(self.file.subject_age)
        self.sub_gender_entry.value = self.file.subject_gender
        self.sub_group_entry.value = self.file.subject_group
        # update required info
        self.proj_id_entry.value = self.file.proj_name
        self.sess_id_entry.value = self.file.session_ID
        self.task_info.value = self.file.task
        self.run_info.value = self.file.run
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
        if not self.file.has_error:
            self.update_widgets()
            for widget in self.require_verification:
                widget.check_valid()
            self.file.validate()
