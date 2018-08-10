from tkinter import Frame, StringVar, BooleanVar, Checkbutton
#from tkinter import Button as tkButton
from tkinter.ttk import Style, Label, Entry
from FileTypes import con_file
#from CustomWidgets import ScrollableFrame
from CustomWidgets.WidgetTable import WidgetTable
#from Management import OptionsVar


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

        from PIL import Image, ImageTk
        self.delete_icon = Image.open("assets/remove_row_trans.png")
        self.delete_icon = self.delete_icon.resize((20, 20), Image.LANCZOS)
        self.delete_icon = ImageTk.PhotoImage(self.delete_icon)

        self.t_style = Style()
        self.t_style.configure('Transp.TButton', borderwidth=0, relief='flat',
                               padding=0)

        # the con file object
        self._file = None
        self.is_loaded = False
        self.channel_widgets = {}
        # keep track of the separators so we can remove and redraw as needed

    def _create_widgets(self):
        self.channels_table = WidgetTable(
            self,
            headings=["Ch #", "Channel name", "Is bad?", "Is trigger?",
                      "Trigger Channel description"],
            row_vars=[StringVar, StringVar, BooleanVar, BooleanVar, StringVar],
            row_configs=[None, None, {'command': self._toggle_editable},
                         None, {'state': 'readonly'}],
            entry_types=[Label, Entry, Checkbutton, Checkbutton, Entry],
            add_options=['A', 'B'],
            data_array=[],
            adder_script=self.add_channel_from_selection)
        self.channels_table.grid()

    def _toggle_editable(self):
        # modify the state of the description entry depending on the state of
        # the Checkbutton
        print('hody')

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
        self._file.interesting_channels.append(i)

        next_ch_idx = self.channel_name_states['not shown'].index(
            selected_ch_name)
        # remove the entry that was selected and add it to the shown list:
        self.channel_name_states['shown'].append(
            self.channel_name_states['not shown'].pop(
                self.channel_name_states['not shown'].index(selected_ch_name)))
        self.channels_table.nameselection.configure(
            values=self.channel_name_states['not shown'])
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
        n = StringVar()
        n.set(str(i))
        self.add_channel_vars(i)
        return [n] + self._file.tab_info[i]

    def update(self):
        #print(self._file.tab_info)
        var_data = []
        config_data = []
        not_shown = []
        shown = []
        for i in range(self._file.info['Channels']):
            if i not in self._file.interesting_channels:
                not_shown.append(self._file.channel_names[i])
            else:
                shown.append(self._file.channel_names[i])
        self.channel_name_states['not shown'] = not_shown
        self.channel_name_states['shown'] = shown
        for key in self._file.interesting_channels:
            n = StringVar()
            n.set(str(key))
            ch_info = self._file.tab_info[key]
            row_vars = [n] + ch_info
            row_configs = [None, None, None,
                           {'command': self._toggle_editable},
                           {'state': 'readonly'}]
            var_data.append(row_vars)
            config_data.append(row_configs)
        self.channels_table.set(var_data, config_data)
        self.channels_table.options = self._file.channel_names
        self.channels_table.nameselection.set(
            self.channel_name_states['not shown'][0])
        #self.channels_table.nameselection.value = OptionsVar()  # dummy

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
        if isinstance(other, con_file):
            self._file = other
            self.update()
        else:
            self.is_loaded = False


""" maybe useful later?? Might want to make sure the actual channel list
 fits in the frame and get it to scroll if it doesn't??
# grid the frame to make it visible
self.scrollframe.frame.grid(row=0, column=0, sticky='nsew')
# then tell the frame to be re-attached
self.scrollframe.reattach()
# update the bounds
self.scrollframe.configure_view(None)"""
