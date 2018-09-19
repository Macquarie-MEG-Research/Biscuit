from tkinter import Entry, Frame, FLAT, Label, END, SUNKEN, LEFT

"""
Code c/o pydesigner from stackoverflow:
https://stackoverflow.com/a/13243973
(with a fair few personal modifications)
"""

DEFAULTVALUE = ['', '', '']


class DateEntry(Frame):
    def __init__(self, master, text=DEFAULTVALUE, frame_look={}, **look):
        args = dict(relief=SUNKEN, border=1)
        args.update(frame_look)
        Frame.__init__(self, master, **args)

        self.validate_cmd = self.register(self._check_new)

        args = {'relief': FLAT}
        args.update(look)

        # we can give the entries some default values if they are provided
        # if the text input is malformed (ie. not a list or doesn't have
        # 3 entires, just do an empty initial value)
        if not isinstance(text, list):
            text = DEFAULTVALUE
        else:
            if len(text) != 3:
                text = DEFAULTVALUE
        # otherwise text is fine as it is (well, not really,
        # but good enough for now...)
        self.entry_1 = Entry(self, width=5, justify='center', **args)
        self.entry_1.insert(0, text[0])
        self.entry_1.configure(
            validate='key',
            validatecommand=(self.validate_cmd, 0, 2, '%P', '%s'))
        self.label_1 = Label(self, text='/', bg="white", **args)
        self.entry_2 = Entry(self, width=5, justify='center', **args)
        self.entry_2.insert(0, text[1])
        self.entry_2.configure(
            validate='key',
            validatecommand=(self.validate_cmd, 1, 2, '%P', '%s'))
        self.label_2 = Label(self, text='/', bg="white", **args)
        self.entry_3 = Entry(self, width=7, justify='center', **args)
        self.entry_3.insert(0, text[2])
        self.entry_3.configure(
            validate='key',
            validatecommand=(self.validate_cmd, 2, 4, '%P', '%s'))

        self.entry_1.pack(side=LEFT, fill='x', expand=True)
        self.label_1.pack(side=LEFT)
        self.entry_2.pack(side=LEFT, fill='x', expand=True)
        self.label_2.pack(side=LEFT)
        self.entry_3.pack(side=LEFT, fill='x', expand=True)

        self.entries = [self.entry_1, self.entry_2, self.entry_3]

        #self.entry_1.bind('<KeyRelease>', lambda e: self._check(0, 2))
        #self.entry_2.bind('<KeyRelease>', lambda e: self._check(1, 2))
        #self.entry_3.bind('<KeyRelease>', lambda e: self._check(2, 4))
        #self.entry_3.bind('<Shift-Tab>', self._move_back)

    def _move_back(self, event):
        self.moved_back = True

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, END)
        entry.insert(0, cont[:-1])

    def _check_new(self, wid, max_length, new_val, old_val):
        wid, max_length = int(wid), int(max_length)
        if len(new_val) > max_length:
            return False
        elif new_val == '':
            return True
        else:
            if not new_val.isdigit():
                return False
            else:
                if len(new_val) == 2:
                    # In this case, move cursor to next widget if we aren't the
                    # last one.
                    if wid != 2:
                        self.entries[wid + 1].focus()
                return True

    def get(self):
        return [e.get() for e in self.entries]

    def set(self, value):
        """
        Sets the value of the DateEntry

        Parameters:
         - value : tuple
            The value to set the date to
        """
        self.entry_1.delete(0, END)
        self.entry_1.insert(0, str(value[0]))
        self.entry_2.delete(0, END)
        self.entry_2.insert(0, str(value[1]))
        self.entry_3.delete(0, END)
        self.entry_3.insert(0, str(value[2]))
