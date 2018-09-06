from tkinter import Frame, StringVar, BooleanVar, Checkbutton, BOTH
#from tkinter import Button as tkButton
from tkinter.ttk import Label, Entry
from FileTypes import con_file
from CustomWidgets.WidgetTable import WidgetTable


class ChannelInfoFrame(Frame):
    def __init__(self, master, default_settings, *args, **kwargs):
        self.master = master
        self.default_settings = default_settings
        super(ChannelInfoFrame, self).__init__(self.master, *args, **kwargs)

        # track the separators to modify them when number of rows changes
        self.separators = []

        self._create_widgets()

        # two lists to keep track of which values are shown and which aren't
        self.channel_name_states = {'not shown': [], 'shown': []}

        # the con file object
        self._file = None
        self.is_loaded = False
        self.channel_widgets = {}
        # keep track of the separators so we can remove and redraw as needed

    def _create_widgets(self):
        self.channels_table = WidgetTable(
            self,
            headings=["Channel name", "Is bad?", "Is trigger?",
                      "Trigger Channel description"],
            pattern=[
                StringVar,
                BooleanVar,
                {'var': BooleanVar, 'func': self._toggle_editable,
                 'func_has_row_ctx': True},
                {'var': StringVar, 'configs': {'state': 'readonly'}}],
            widgets_pattern=[Label, Checkbutton, Checkbutton, Entry],
            add_options=['A', 'B'],
            adder_script=self.add_channel_from_selection,
            remove_script=self.remove_channel,
            sort_column=0)
        self.channels_table.grid(sticky='nsew')
        #self.channels_table.pack(fill=BOTH, expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        #self.grid(sticky='nsew')

    def _toggle_editable(self, idx):
        # modify the state of the description entry depending on the state of
        # the Checkbutton
        state = self.channels_table.data[idx][-2]['var'].get()
        if state:
            self.channels_table.widgets[idx][-2].config(state='normal')
        else:
            self.channels_table.widgets[idx][-2].config(state='readonly')

    def add_channel_vars(self, i):
        if i not in self._file.tab_info.keys():
            name_var = StringVar()
            name_var.set(self._file.channel_names[i])
            bad_var = BooleanVar()
            bad_var.set(False)
            trigger_var = BooleanVar()
            trigger_var.set(False)
            desc_var = StringVar()
            desc_var.set("")
            self._file.tab_info[i] = [name_var, bad_var, trigger_var,
                                      desc_var]

    def add_channel_from_selection(self):
        # this will look up to see if the con file has any saved info for the
        # channel. If so return it. Otherwise return an empty list.
        selected_ch_name = self.channels_table.nameselection.get()
        i = self._file.channel_names.index(selected_ch_name)
        self._file.interesting_channels.add(i)

        next_ch_idx = self.channel_name_states['not shown'].index(
            selected_ch_name)
        # remove the entry that was selected and add it to the shown list:
        self.channel_name_states['shown'].append(
            self.channel_name_states['not shown'].pop(
                self.channel_name_states['not shown'].index(selected_ch_name)))
        self.channels_table.nameselection.configure(
            values=self.channel_name_states['not shown'])
        # sort the shown channels too to ensure we have no issues with removal
        # later.
        self.channel_name_states['shown'].sort()
        try:
            self.channels_table.nameselection.set(
                self.channel_name_states['not shown'][next_ch_idx])
        except IndexError:
            # we have probably removed the last entry in the list
            # we can subtract 1 from the index to display that one instead,
            # but we need to make sure that we haven't exhausted the list also
            next_ch_idx -= 1
            if next_ch_idx >= 0:
                self.channels_table.nameselection.set(
                    self.channel_name_states['not shown'][next_ch_idx])
            # otherwise do nothing as there are no more values...

        # finally, return the required data:
        self.add_channel_vars(i)
        if self._file.tab_info[i][-2].get():
            return [*self._file.tab_info[i][:-1],
                    {'var': self._file.tab_info[i][-1],
                     'configs': {'state': 'normal'}}]
        else:
            return self._file.tab_info[i]

    def remove_channel(self, idx):
        # Simply adds the channel number that was removed back into the list of
        # channels to select from.

        # first, remove the channel from the interesting channels set.
        ch_num = self._file.channel_names.index(
            self.channel_name_states['shown'][idx])
        if ch_num in self._file.interesting_channels:
            self._file.interesting_channels.remove(ch_num)

        self.channel_name_states['not shown'].append(
            self.channel_name_states['shown'].pop(idx))
        # sort the names to ensure it appears again in the right place
        self.channel_name_states['not shown'].sort()
        self.channels_table.nameselection.configure(
            values=self.channel_name_states['not shown'])

    def update(self):
        var_data = []
        not_shown = []
        shown = []
        for i in range(self._file.info['Channels']):
            if i not in self._file.interesting_channels:
                not_shown.append(self._file.channel_names[i])
            else:
                shown.append(self._file.channel_names[i])
                # also append the tab info data into a list
                if self._file.tab_info[i][-2].get():
                    data = [*self._file.tab_info[i][:-1],
                            {'var': self._file.tab_info[i][-1],
                            'configs': {'state': 'normal'}}]
                else:
                    data = self._file.tab_info[i]
                var_data.append(data)
        self.channel_name_states['not shown'] = not_shown
        self.channel_name_states['shown'] = shown
        self.channels_table.set(var_data)
        self.channels_table.options = self.channel_name_states['not shown']

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, other):
        """
        Set the file property to whatever the new file is.
        When this happens the update command will be called which will redraw
        the channel info list
        """
        # if the file is being set as a con_file continue
        if other != self._file:
            if isinstance(other, con_file):
                self._file = other
                self.update()
            else:
                self.is_loaded = False
