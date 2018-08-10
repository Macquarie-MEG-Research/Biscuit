from tkinter import (Frame, Label, NORMAL, PhotoImage, Entry,
                     StringVar, BooleanVar, DoubleVar)
from tkinter import Button as tkButton
from tkinter.ttk import Style, Combobox, Separator, Checkbutton
from FileTypes import con_file
from CustomWidgets import ScrollableFrame


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
        namesframe = Frame(self)
        Label(namesframe, text="Add a channel: ").grid(column=0,
                                                       row=0, sticky='w')
        self.nameselection = Combobox(namesframe, values=("None",),
                                      state='readonly', exportselection=0)
        self.nameselection.grid(column=1, row=0, sticky='w')
        self.nameselection.bind("<<ComboboxSelected>>",
                                self.add_channel_from_selection)
        namesframe.grid(row=0, sticky='ew')

        self.scrollframe = ScrollableFrame(self)

        Label(self.scrollframe.frame, text="Ch #").grid(column=0, row=0,
                                                        sticky='w', padx=5)
        Label(self.scrollframe.frame, text="Channel name").grid(column=2,
                                                                row=0,
                                                                sticky='w',
                                                                padx=5)
        Label(self.scrollframe.frame, text="Is bad?").grid(column=4, row=0,
                                                           sticky='w', padx=5)
        Label(self.scrollframe.frame, text="Is trigger?").grid(column=6, row=0,
                                                               sticky='w',
                                                               padx=5)
        Label(self.scrollframe.frame,
              text="Trigger Channel description").grid(column=8, row=0,
                                                       sticky='w', padx=5)
        Label(self.scrollframe.frame, text="Delete").grid(column=10, row=0,
                                                          sticky='w',
                                                          padx=5)

        for i in (1, 3, 5, 7, 9):
            sep = Separator(self.scrollframe.frame,
                            orient='vertical')
            sep.grid(column=i, row=0, rowspan=1, sticky='ns')
            self.separators.append(sep)

        self.scrollframe.grid(row=1, sticky='nsew')

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)  # ?

    def redraw_channel_list(self):
        """ Redraw the channel list """
        frame = self.scrollframe.frame
        curr_channels = self._file.interesting_channels.copy()
        self._file.interesting_channels.sort()
        if curr_channels != self._file.interesting_channels:
            # if the indexes weren't in the correct order then they now will
            # be, and we want to redraw all visible rows
            # for now we will just redraw all the widgets
            for _, widgets in self.channel_widgets.items():
                for widget in widgets:
                    widget.grid_forget()
            for sep in self.separators:
                sep.grid_forget()
            # hopefully now we will only have the title so now we add them all
            # back with the new one in the right order
            for idx in self._file.interesting_channels:
                rows = frame.grid_size()[1]
                for column, widget in enumerate(self.channel_widgets[idx]):
                    if column in (2, 3):
                        widget.grid(row=rows, column=2 * column, padx=5)
                    else:
                        widget.grid(row=rows, column=2 * column, sticky='w',
                                    padx=5)
            #now draw all the separators again:
            for i, sep in enumerate(self.separators):
                sep.grid(row=0, rowspan=rows + 1, column=2 * i + 1,
                         sticky='ns')

        else:
            # this is assuming we are adding a row. When removing one
            # this is still called which causes the final channel removal
            # function to break. This shouldn't be an issue once I change
            # the drawing methods to be static and the variables to be the
            # thing that changes when we add or remove channels
            if len(self._file.interesting_channels) != 0:
                idx = self._file.interesting_channels[-1]
                rows = frame.grid_size()[1]
                for column, widget in enumerate(self.channel_widgets[idx]):
                    if column in (2, 3):
                        widget.grid(row=rows, column=2 * column, padx=5)
                    else:
                        widget.grid(row=rows, column=2 * column, sticky='w',
                                    padx=5)
                # now update the separators to have a higher rowspawn
                for i, sep in enumerate(self.separators):
                    sep.grid_forget()
                    sep.grid(row=0, rowspan=rows + 1, column=2 * i + 1,
                             sticky='ns')

    def add_channel_from_selection(self, event):
        """ call the add_channel command with the channel index selected from
            the selection box """
        selected_ch_name = self.nameselection.get()
        i = self._file.channel_names.index(selected_ch_name)
        print('adding {0}'.format(i))
        self._file.interesting_channels.append(i)
        # next index will just be the current one as it will be removed...
        next_ch_idx = self.channel_name_states['not shown'].index(
            selected_ch_name)
        # remove the entry that was selected and add it to the shown list:
        self.channel_name_states['shown'].append(
            self.channel_name_states['not shown'].pop(
                self.channel_name_states['not shown'].index(selected_ch_name)))
        self.nameselection.configure(
            values=self.channel_name_states['not shown'])
        try:
            self.nameselection.set(
                self.channel_name_states['not shown'][next_ch_idx])
        except IndexError:
            # we have probably removed the last entry in the list
            # we can subtract 1 from the index to display that one instead,
            # but we need to make sure that we haven't exhausted the list also
            next_ch_idx -= 1
            if next_ch_idx >= 0:
                self.nameselection.set(
                    self.channel_name_states['not shown'][next_ch_idx])
            # otherwise do nothing as there are no more values...

        self.add_channel(i)
        self.redraw_channel_list()

    def add_channel(self, i):
        """
        Add all the channel information required.
        This will be called from either the combobox call back or when the file
        changes via the update method
        """
        frame = self.scrollframe.frame

        if i not in self._file.tab_info.keys():
            name_var = StringVar()
            name_var.set(self._file.channel_names[i])
            bad_var = BooleanVar()
            bad_var.set(False)
            trigger_var = BooleanVar()
            trigger_var.set(False)
            desc_var = StringVar()
            desc_var.set("")
            threshold_var = DoubleVar()
            self._file.tab_info[i] = [name_var, bad_var, trigger_var,
                                      desc_var, threshold_var]

        entry_state = ("readonly" if self._file.tab_info[i][2].get() is False
                       else NORMAL)

        # now create the entries/checkbuttons
        number = Label(frame, text=str(i))
        name_entry = Entry(frame)
        name_entry.config(textvariable=self._file.tab_info[i][0],
                          state="readonly")
        bad_check = Checkbutton(frame)
        bad_check.config(variable=self._file.tab_info[i][1])
        trigger_check = Checkbutton(frame, command=self.toggle_entry)
        trigger_check.config(variable=self._file.tab_info[i][2])
        desc_entry = Entry(frame)
        desc_entry.config(textvariable=self._file.tab_info[i][3],
                          state=entry_state)
        #threshold_entry = Entry(frame)
        #threshold_entry.config(textvariable=self._file.tab_info[i][4],
        #                       state=entry_state)
        delete_button = tkButton(
            frame, command=self.delete_row,
            relief='flat', borderwidth=0, highlightthickness=0)
        delete_button.config(image=self.delete_icon)

        # add all widgets so we can reuse them later if need-be
        self.channel_widgets[i] = [number, name_entry, bad_check,
                                   trigger_check, desc_entry,
                                   delete_button]

    def remove_channel(self, i):
        """ remove the channel indicated by i
        i can also be 'all' which indicates that all channels are to be removed
        """
        if i != 'all':
            if i in self.channel_widgets:
                for widget in self.channel_widgets[i]:
                    widget.grid_forget()
                del self.channel_widgets[i]
        else:
            for _, widgets in self.channel_widgets.items():
                for widget in widgets:
                    widget.grid_forget()
            self.channel_widgets = {}
        # also sort out separators
        """
        rows = self.scrollframe.frame.grid_size()[1]
        for i, sep in enumerate(self.separators):
            sep.grid_forget()
            sep.grid(row=0, rowspan=rows + 1, column=2 * i + 1,
                     sticky='ns')
        """

    def update(self):
        # fill the channel choice box
        not_shown = []
        shown = []
        print(self._file.interesting_channels, 'interesting')
        for i in range(self._file.info['Channels']):
            if i not in self._file.interesting_channels:
                not_shown.append(self._file.channel_names[i])
            else:
                shown.append(self._file.channel_names[i])
        self.channel_name_states['not shown'] = not_shown
        self.channel_name_states['shown'] = shown
        self.nameselection.configure(
            values=self.channel_name_states['not shown'])
        self.nameselection.set(self.channel_name_states['not shown'][0])

        # next, draw any channels that are already shown
        # first, we need to remove any that are currently visible
        self.remove_channel('all')
        # now add all the channels that we need
        for i in self._file.interesting_channels:
            self.add_channel(i)
        # to avoid having to add an extra argument to the redraw_channel_list
        # function, we'll sort the interesting channels list in reverse,
        # that way the redraw channel list will be forced to draw any channels
        # that are in the intersting channels list
        self._file.interesting_channels.sort(reverse=True)
        self.redraw_channel_list()

    def toggle_entry(self):
        index = self._file.interesting_channels[
            self.scrollframe.frame.focus_get().grid_info().get('row') - 1]
        # this will only work for a ttk Checkbox
        state = self.channel_widgets[index][3].state()
        entry = self.channel_widgets[index][4]  #:5]
        if 'selected' in state:
            entry.config(state=NORMAL)
        else:
            entry.config(state='readonly')

    def delete_row(self):
        index = self._file.interesting_channels[
            self.scrollframe.frame.focus_get().grid_info().get('row') - 1]
        ch_name = self._file.channel_names[index]
        print('removing {0} ({1})'.format(index, ch_name))
        self.remove_channel(index)
        self._file.interesting_channels.remove(index)
        self.channel_name_states['shown'].remove(ch_name)
        self.channel_name_states['not shown'].append(ch_name)
        self.channel_name_states['not shown'].sort()
        self.redraw_channel_list()
        self.nameselection.configure(
            values=self.channel_name_states['not shown'])

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
