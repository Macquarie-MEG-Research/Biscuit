from tkinter import Frame, StringVar, BooleanVar
from tkinter.ttk import Label, Separator
from CustomWidgets.InfoEntries import InfoEntry, InfoLabel, InfoCheck, InfoList


class FileInfoFrame(Frame):
    def __init__(self, master, default_settings, *args, **kwargs):
        self.master = master
        self.default_settings = default_settings
        super(FileInfoFrame, self).__init__(self.master, *args, **kwargs)

        self._file = None
        self.widgets_created = False

        self._create_widgets()

    def _create_widgets(self):
        Label(self, text="Recording Information:").grid(column=0, row=0,
                                                        columnspan=2)
        Separator(self, orient='horizontal').grid(column=0, row=1,
                                                  columnspan=2, sticky='ew')
        self.institution_info = InfoLabel(self, 'Institution', "None")
        self.institution_info.label.grid(column=0, row=2)
        self.institution_info.value.grid(column=1, row=2)
        self.serial_num_info = InfoLabel(self, 'Serial Number', "None")
        self.serial_num_info.label.grid(column=0, row=3)
        self.serial_num_info.value.grid(column=1, row=3)
        self.channel_info = InfoLabel(self, 'Channels', "None")
        self.channel_info.label.grid(column=0, row=4)
        self.channel_info.value.grid(column=1, row=4)
        self.meas_date_info = InfoLabel(self, 'Measurement date', "None")
        self.meas_date_info.label.grid(column=0, row=5)
        self.meas_date_info.value.grid(column=1, row=5)
        self.gains_info = InfoLabel(self, 'Gains', "None")
        self.gains_info.label.grid(column=0, row=6)
        self.gains_info.value.grid(column=1, row=6)

        Separator(self, orient='horizontal').grid(column=0, row=7,
                                                  columnspan=2, sticky='ew')
        Label(self, text="Required Information:").grid(column=0, row=8,
                                                       columnspan=2)

        self.acq_info = InfoEntry(self, 'Acquisition', StringVar(),
                                  bad_values=[''],
                                  validate_cmd=None)
        self.acq_info.label.grid(column=0, row=9)
        self.acq_info.value.grid(column=1, row=9)
        self.mrks_info = InfoList(self, "Associated .mrk's", [],
                                  validate_cmd=None)
        self.mrks_info.label.grid(column=0, row=10)
        self.mrks_info.value.grid(column=1, row=10)

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
        self.grid()

    def update_widgets(self):
        self.institution_info.value = self._file.info['Institution name']
        self.serial_num_info.value = self._file.info['Serial Number']
        self.channel_info.value = self._file.info['Channels']
        self.meas_date_info.value = self._file.info['Measurement date']
        self.gains_info.value = self._file.info['gains']

        self.acq_info.value = self._file.acquisition
        self.acq_info.validate_cmd = self._file.check_complete
        self.mrks_info.value = self._file.associated_mrks
        self.mrks_info.validate_cmd = self._file.check_complete
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
        self._file = value
        self.update_widgets()
        if not self._file.is_good:
            self.acq_info.check_valid()
