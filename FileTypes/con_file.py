from tkinter import StringVar, BooleanVar, DoubleVar
from struct import unpack
from .FileInfo import FileInfo
from mne.io.kit.constants import KIT
from datetime import datetime
from utils import unpickle_var

GAINS = [1, 2, 5, 10, 20, 50, 100, 200]


class con_file(FileInfo):
    """
    .con specific file container.
    """
    def __init__(self, id_=None, file=None, *args, **kwargs):
        super(con_file, self).__init__(id_, file, *args, **kwargs)

        self._type = '.con'
        self.associated_raw = None
        if 'emptyroom' not in file:
            # overwrite the default True value as this can actually be
            # False for con files
            self.is_good = False
        else:
            # an empty room file is good in it's default state
            self.is_good = True

        # set any optional info
        self.is_junk = BooleanVar()
        self.is_empty_room = BooleanVar()
        if 'emptyroom' in self.file:
            self.is_empty_room.set(True)
        self.has_empty_room = BooleanVar()

        # set any required info
        self.acquisition = StringVar()
        # these will be mrk_file objects
        self.associated_mrks = []

        # set any particular bad values
        # The keys of this dictionary must match the keys in the required info
        self.bad_values = {'acquisition': [''],
                           'associated_mrks': [[]]}

        # a list of channel names that are 'interesting'
        # a channel is interesting if any of it's values are not the default
        # ones or the user has selected the channel from the list in the
        # channels tab to enter info
        self.interesting_channels = []
        self.channel_names = []

        self.tab_info = {}

    def load_data(self):
        # reads in various other pieces of information required
        with open(self.file, 'rb') as file:
            # let's get the gain:
            file.seek(0x70)
            offset = unpack('i', file.read(4))[0]
            file.seek(offset)
            amp_data = unpack('i', file.read(4))[0]
            gain1 = (amp_data & 0x00007000) >> 12
            gain2 = (amp_data & 0x70000000) >> 28
            gain3 = (amp_data & 0x07000000) >> 24
            self.info['gains'] = '{0}, {1}, {2}'.format(GAINS[gain1],
                                                        GAINS[gain2],
                                                        GAINS[gain3])

            # get the InsitutionName and ManufacturersModelName:
            # code taken pretty much directly from the kit.py script in mne
            file.seek(0x20C)
            system_name = unpack('128s', file.read(0x80))[0].decode()
            model_name = unpack('128s', file.read(0x80))[0].decode()
            nchans = unpack('i', file.read(4))[0]
            file.seek(0x100, 1)     # ignore any comments
            create_time, = unpack('i', file.read(0x4))
            system_name = system_name.replace('\x00', '')
            # system_name = system_name.strip().replace('\n', '/')
            model_name = model_name.replace('\x00', '')
            # model_name = model_name.strip().replace('\n', '/')
            self.info['Institution name'] = system_name
            self.info['Serial Number'] = model_name
            self.info['Channels'] = nchans
            self.info['Measurement date'] = datetime.fromtimestamp(
                create_time).strftime('%d/%m/%Y')

            # Get all the channel information here separately from mne.
            # This way the data is intrinsically linked to the con file
            # and we can generate the channels tab from the start
            file.seek(0x40)
            chan_offset, chan_size = unpack('2i', file.read(8))

            # check to see if any of the channels are designated as triggers
            # by default
            if self.parent is not None:
                proj_settings = self.parent.proj_settings
                def_trigger_info = proj_settings.get('DefaultTriggers',
                                                     [[]])
                default_triggers = [int(row[0]) for row in def_trigger_info]
                default_descriptions = [row[1] for row in def_trigger_info]
            else:
                default_triggers = []
                default_descriptions = []

            """ optimise to only load interesting channels """
            for i in range(nchans):
                file.seek(chan_offset + i * chan_size)
                channel_type, = unpack('i', file.read(4))
                if channel_type in KIT.CHANNELS_MEG:
                    name = "MEG {0:03d}".format(i + 1)
                elif (channel_type in KIT.CHANNELS_MISC or
                        channel_type == KIT.CHANNEL_NULL):
                    #channel_no, = unpack('i', file.read(KIT.INT))
                    #name, = unpack('64s', file.read(64))
                    ch_type_label = KIT.CH_LABEL[channel_type]
                    name = "{0} {1:03d}".format(ch_type_label, i + 1)
                self.channel_names.append(name)

                # we need to be careful about the indexing...
                #print(default_triggers, i+1)
                if i + 1 in default_triggers:
                    is_trigger = True
                    self.interesting_channels.append(i)
                else:
                    is_trigger = False

                curr_channel_data = list(self.tab_info.keys())
                curr_channel_data.sort()
                for ch_id in curr_channel_data:
                    if ch_id not in self.interesting_channels:
                        self.interesting_channels.append(ch_id)

                """
                Might need to standardise the format of this for (un)pickling
                """
                if (i in self.interesting_channels and
                        i not in self.tab_info.keys()):
                    name_var = StringVar()
                    name_var.set(name)
                    bad_var = BooleanVar()
                    bad_var.set(False)
                    trigger_var = BooleanVar()
                    trigger_var.set(is_trigger)
                    if is_trigger:
                        idx = default_triggers.index(i + 1)
                        description = default_descriptions[idx]
                    else:
                        description = ''
                    desc_var = StringVar()
                    desc_var.set(description)
                    threshold_var = DoubleVar()
                    self.tab_info[i] = [name_var, bad_var, trigger_var,
                                        desc_var, threshold_var]

        self.loaded = True

    def check_complete(self):
        """
        Check there are no bad values
        """
        print('verifying con file...')
        if self.is_junk.get() is True:
            self.treeview.add_tags(self.ID, ['JUNK_FILE'])
            self.treeview.remove_tags(self.ID, ['BAD_FILE'])
        else:
            self.treeview.remove_tags(self.ID, ['JUNK_FILE'])
            self.treeview.add_tags(self.ID, ['BAD_FILE'])

        # if the con file is junk or the empty room file then we consider it ok
        if (self.is_junk.get() is True or
                self.is_empty_room.get() is True):
            print('con file is good')
            self.is_good = True
            return
        print('con file might be bad...')
        super(con_file, self).check_complete()

    def get_trigger_channels(self):
        """ Returns the list of trigger channels associated with the data
            and the descriptions """
        trigger_channels = []
        descriptions = []
        for i, ch_data in self.tab_info.items():
            if ch_data[2].get() == 1:
                trigger_channels.append(str(i + 1))
                descriptions.append(ch_data[3].get())

        return trigger_channels, descriptions

    def __getstate__(self):
        data = super(con_file, self).__getstate__()

        # for the tab_info we currently have a list of Variables
        # we only need to serialise variables in the self.interesting_channels
        # variable.
        # we also are not allowing names to change right now.
        for idx in self.interesting_channels:
            ch = self.tab_info[idx]
            info = {}
            info['name'] = ch[0].get()
            if ch[1].get() is True:
                info['bad'] = True
            if ch[2].get() is True:
                info['trigger'] = True
            if ch[3].get() != "":
                info['description'] = ch[3].get()
            if ch[4].get() != 0:
                info['threshold'] = ch[4].get()
            data['tab_info'][idx] = info

        print(data, 'data')

        return data

    def __setstate__(self, state):
        print(state, 'pickled state')
        super(con_file, self).__setstate__(state)

        for idx, ch in state['tab_info'].items():
            # each channel has it's info stored as a dictionary
            self.tab_info[idx] = [unpickle_var(('string', ch['name'])),
                                  unpickle_var(('bool', ch.get('bad',
                                                               False))),
                                  unpickle_var(('bool', ch.get('trigger',
                                                               False))),
                                  unpickle_var(('string', ch.get('description',
                                                                 ''))),
                                  unpickle_var(('double', ch.get('threshold',
                                                                 0)))]
        print(self.tab_info, 'blahaha')
