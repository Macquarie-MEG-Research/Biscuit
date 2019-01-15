from tkinter import StringVar, BooleanVar
from struct import unpack
from datetime import datetime

from .BIDSFile import BIDSFile
from mne.io.kit.constants import KIT
from .KITData import KITData

GAINS = [1, 2, 5, 10, 20, 50, 100, 200]


class con_file(BIDSFile):
    """
    .con specific file container.
    """
    def __init__(self, id_=None, file=None, settings=dict(), parent=None):
        super(con_file, self).__init__(id_, file, settings, parent)

        self._type = '.con'
        self.requires_save = True
        if 'emptyroom' not in file:
            # overwrite the default True value as this can actually be
            # False for con files
            self.is_good = False
        else:
            # an empty room file is good in it's default state
            self.is_good = True

    def _create_vars(self):
        """
        Create the required Variables
        """
        super(con_file, self)._create_vars()

        # a list of channel names that are 'interesting'
        # a channel is interesting if any of it's values are not the default
        # ones or the user has selected the channel from the list in the
        # channels tab to enter info
        # TODO: replace with self.event_data ??
        self.interesting_channels = set()
        self.channel_names = []

        self.tab_info = {}

        self.associated_channel_tab = None

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

            # determine whether the data has continuous head movement data
            file.seek(0x1D0)
            reTHM_offset, = unpack('i', file.read(0x4))
            self.extra_data['chm'] = (reTHM_offset != 0)

            # Get all the channel information here separately from mne.
            # This way the data is intrinsically linked to the con file
            # and we can generate the channels tab from the start
            file.seek(0x40)
            chan_offset, chan_size = unpack('2i', file.read(8))

            # check to see if any of the channels are designated as triggers
            # by default
            def_trigger_info = None
            if isinstance(self.container, KITData):
                if self.container.contains_required_files:
                    if isinstance(self.container.settings, dict):
                        def_trigger_info = self.container.settings.get(
                            'DefaultTriggers', None)
            default_triggers = []
            default_descriptions = []
            if def_trigger_info is not None:
                default_triggers = [int(row[0]) for row in
                                    def_trigger_info]
                default_descriptions = [row[1] for row in def_trigger_info]

            channels_from_load = list(self.interesting_channels)

            """ optimise to only load interesting channels """
            for i in range(nchans):
                file.seek(chan_offset + i * chan_size)
                channel_type, = unpack('i', file.read(4))
                if channel_type in KIT.CHANNELS_MEG:
                    name = "MEG {0:03d}".format(i)
                elif (channel_type in KIT.CHANNELS_MISC or
                        channel_type == KIT.CHANNEL_NULL):
                    ch_type_label = KIT.CH_LABEL[channel_type]
                    name = "{0} {1:03d}".format(ch_type_label, i)
                self.channel_names.append(name)

                # only add the default channels if the list of channels loaded
                # is empty. Otherwise default channels removed before save will
                # be re-added
                if channels_from_load == []:
                    if i in default_triggers:
                        is_trigger = True
                        self.interesting_channels.add(i)
                    else:
                        is_trigger = False
                    if (i in self.interesting_channels and
                            i not in self.tab_info.keys()):
                        name_var = StringVar()
                        name_var.set(name)
                        bad_var = BooleanVar()
                        bad_var.set(False)
                        trigger_var = BooleanVar()
                        trigger_var.set(is_trigger)
                        if is_trigger:
                            idx = default_triggers.index(i)
                            description = default_descriptions[idx]
                        else:
                            description = ''
                        desc_var = StringVar()
                        desc_var.set(description)
                        self.tab_info[i] = [name_var, bad_var, trigger_var,
                                            desc_var]

        self.loaded = True

    def _apply_settings(self):
        """ Check the current settings and add any new channels from them """
        default_triggers = None
        if self.container is not None:
            default_triggers = self.container.settings.get('DefaultTriggers')
        curr_triggers = self.tab_info.keys()
        if default_triggers is not None:
            for i, desc in default_triggers:
                if i not in curr_triggers:
                    # add the variables to self.tab_info[i]
                    name_var = StringVar()
                    try:
                        name_var.set(self.channel_names[i])
                    except IndexError:
                        break
                    bad_var = BooleanVar()
                    bad_var.set(False)
                    trigger_var = BooleanVar()
                    trigger_var.set(True)
                    desc_var = StringVar()
                    desc_var.set(desc)
                    self.tab_info[i] = [name_var, bad_var, trigger_var,
                                        desc_var]
                    self.interesting_channels.add(i)
                    # If the associated channel tab is currently associated,
                    # select the channel name and redraw the panel
                    if self.associated_channel_tab is not None:
                        self.associated_channel_tab.channels_table.nameselection.set(self.channel_names[i])  # noqa
                        self.associated_channel_tab.channels_table.add_row_from_selection(None)  # noqa

    # TODO: maybe not have this return two lists??
    def get_event_data(self):
        """ Returns the list of trigger channels associated with the data
            and the descriptions """
        trigger_channels = []
        descriptions = []
        for ch_num in self.interesting_channels:
            ch_data = self.tab_info[ch_num]
            if ch_data[2].get() == 1:
                # TODO: +1 for adult system I think...
                trigger_channels.append(str(ch_num))    # +1 for MNE
                descriptions.append(ch_data[3].get())

        return trigger_channels, descriptions

    def bad_channels(self):
        """
        Take the channel list and get any bad channels and set the channels in
        the associated raw as bad.
        Returns the list of bads channels
        """
        bads = []

        for ch_data in self.tab_info.values():
            if ch_data[1].get() == 1:
                bads.append(ch_data[0].get())

        return bads

    def __getstate__(self):
        # call the parent method
        data = super(con_file, self).__getstate__()

        # next sort out channel info
        data['cin'] = {}
        # let's only save the data that is specified as an
        # 'interesting channel'. The other channel info will be discarded as it
        # would have been deleted from the list anyway.
        for key in self.interesting_channels:
            data['cin'][key] = [i.get() for i in self.tab_info[key]]

        return data

    def __setstate__(self, state):
        super(con_file, self).__setstate__(state)

        # then populate them
        for key in state.get('cin', []):
            self.tab_info[key] = [StringVar(value=state['cin'][key][0]),
                                  BooleanVar(value=state['cin'][key][1]),
                                  BooleanVar(value=state['cin'][key][2]),
                                  StringVar(value=state['cin'][key][3])]

        self.interesting_channels = set(self.tab_info.keys())
