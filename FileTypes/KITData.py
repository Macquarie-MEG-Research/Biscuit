from .BIDSContainer import BIDSContainer
from Management import OptionsVar
from utils import get_object_class
from FileTypes.generic_file import generic_file
from FileTypes.BIDSFile import BIDSFile
from FileTypes.FileInfo import FileInfo
from mne.io import read_raw_kit
from mne.io.constants import FIFF


class KITData(BIDSContainer):
    def __init__(self, id_, file, settings=None, parent=None):
        super(KITData, self).__init__(id_, file, settings, parent)

    def _create_vars(self):
        super(KITData, self)._create_vars()

        # KIT specific variables
        self.dewar_position = OptionsVar(value='supine',
                                         options=["supine", "upright"])
        self.con_map = dict()
        self.is_valid = False

    def initial_processing(self):
        self.load_data()

        # This function needs to be modified to take in the parent id from the
        # treeview instead.
        # This way it can get the ids of the children files to associate with
        # the FileInfo objects.
        if self.is_valid:
            self._set_required_inputs()

        self.extra_data = dict()

    def load_data(self):
        # this will automatically preload the data of any contained files
        files = {'.con': [],
                 '.mrk': [],
                 '.elp': [],
                 '.hsp': [],
                 '.mri': []}

        # go through the direct children of the folder via the treeview
        for sid in self.parent.file_treeview.get_children(self._id):
            item = self.parent.file_treeview.item(sid)
            # check the extension of the file. If it is in the files dict, add
            # the file to the list
            ext = item['values'][0]

            # Check to see if the file has already been preloaded.
            # If so, simply associate it and continue.
            if sid in self.parent.preloaded_data:
                if ext in files:
                    files[item['values'][0]].append(
                        self.parent.preloaded_data[sid])
            else:
                # generate the FileInfo subclass object
                cls_ = get_object_class(ext)
                if not isinstance(cls_, str):
                    # and only call it if it can be. str types are ignored
                    # (only other return type)
                    if issubclass(cls_, BIDSFile):
                        obj = cls_(sid, item['values'][1],
                                   settings=self.parent.proj_settings,
                                   parent=self.parent)
                    elif issubclass(cls_, FileInfo):
                        obj = cls_(sid, item['values'][1],
                                   parent=self.parent)
                    if isinstance(obj, generic_file):
                        obj.dtype = ext
                    if isinstance(obj, BIDSFile):
                        obj.container = self
                        self.jobs.append(obj)
                    # add the data to the preload data
                    self.parent.preloaded_data[sid] = obj
                    if ext in files:
                        files[item['values'][0]].append(obj)

        valid = True
        # validate the folder:
        for dtype, data in files.items():
            if dtype != '.mri':
                if len(data) == 0:
                    valid = False
                    break

        # we'll only check whether the folder is ready to be exported to bids
        # format if it is valid
        if valid:
            # first run the verification on each of the jobs to ensure they
            # have been checked
            for job in self.jobs:
                # this is slightly inefficient, but because _check_bids_ready
                # for BIDSContainers is very efficient it won't matter
                job.validate()
            self.validate()     # do I need to do this??

        self.contained_files = files
        self.is_valid = valid

    def prepare(self):
        self._create_raws()

    # TODO: reformat and REMOVE:
    def _set_required_inputs(self):
        # we have a number of basic properties that we need:
        # this should maybe be moved??

        """ Project settings """
        try:
            proj_name = self.parent.file_treeview.item(
                self._id)['text'].split('_')[2]
        except IndexError:
            proj_name = ''
        self.proj_name.set(proj_name)
        # set the settings via the setter.
        try:
            self.settings = self.proj_settings
        except AttributeError:
            # in this case the settings have probably already been set.
            pass

        """ Subject settings """
        try:
            sub_name = self.parent.file_treeview.item(
                self._id)['text'].split('_')[0]
        except IndexError:
            sub_name = ''
        self.subject_ID.set(sub_name)

    # TODO: fix up 'jobs' stuff
    def _create_raws(self):
        print('creating raws')
        # refresh to avoid adding the con files each time
        self.jobs = []
        for con_file in self.contained_files['.con']:
            # first ensure the data is loaded:
            if con_file.loaded is False:
                con_file.load_data()

            if con_file.is_junk.get() is False:
                if con_file.is_empty_room.get():
                    con_file.acquisition.set('emptyroom')
                    con_file.task.set('noise')
                trigger_channels, descriptions = con_file.trigger_channels()
                con_file.event_info = dict(
                    zip(descriptions, [int(i) for i in trigger_channels]))
                if trigger_channels == []:
                    trigger_channels = '>'
                    stim_code = 'binary'
                    slope = '-'
                else:
                    stim_code = 'channel'
                    slope = '+'
                print('trigger channels:', trigger_channels)
                raw = read_raw_kit(
                    con_file.file,
                    # construct a list of the file paths
                    mrk=[mrk_file.file for mrk_file in
                         con_file.hpi],
                    elp=self.contained_files['.elp'][0].file,
                    hsp=self.contained_files['.hsp'][0].file,
                    stim=trigger_channels, stim_code=stim_code,
                    slope=slope)
                bads = con_file.bad_channels()
                # set the bads
                raw.info['bads'] = bads
                """ Might be needed???
                # assign any participant info we have:
                # first we need to process what we have:
                his_id = self.subject_ID.get()
                age = self.subject_age.get()
                sex = self.subject_gender.get()
                # map the sex to the data used by the raw info
                sex = {U': 0, 'M': 1, 'F': 2}.get(sex, 0)
                subject_info = self.raw_files[acq].info['subject_info']
                subject_info['his_id'] = his_id
                subject_info['birthday'] = his_id
                subject_info['sex'] = sex
                """
                # change the channel type of any channels that are triggers
                for ch in trigger_channels:
                    i = int(ch) - 1
                    raw.info['chs'][i]['kind'] = FIFF.FIFFV_STIM_CH
                # assign the raw to the con_file
                con_file.raw = raw

                con_file.extra_data = {
                    'InstitutionName': con_file.info['Institution name'],
                    'ManufacturersModelName': 'KIT-160',
                    'DewarPosition': self.dewar_position.get(),
                    'Name': self.proj_name.get(),
                    'DeviceSerialNumber': con_file.info['Serial Number']}

            self.jobs.append(con_file)

        return True
