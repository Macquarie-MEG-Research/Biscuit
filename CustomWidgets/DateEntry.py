from tkinter import Entry, Frame, FLAT, Label, END, SUNKEN, LEFT
from datetime import datetime

"""
Code c/o pydesigner from stackoverflow:
https://stackoverflow.com/a/13243973
(with a heavy personal modifications)
"""

DEFAULTVALUE = ['', '', '']


class DateEntry(Frame):
    """ 3-part entry box for entering dates """
    def __init__(self, master, text=DEFAULTVALUE):
        """
        Parameters
        ----------
        master : instance of Widget
            master widget this one is a child of
        text : list of strings, length 3
            The values to initialise the DateEntry with

        """
        Frame.__init__(self, master, relief=SUNKEN, border=1)

        self.validate_cmd = self.register(self._check_new)

        args = {'relief': FLAT, 'border': 0}

        # we can give the entries some default values if they are provided
        # if the text input is malformed (ie. not a list or doesn't have
        # 3 entires, just do an empty initial value)
        if not isinstance(text, list):
            text = DEFAULTVALUE
        else:
            if len(text) != 3:
                text = DEFAULTVALUE
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

    def _check_new(self, wid, max_length, new_val, old_val):
        """ Determine whether the value entered is valid

        Parameters
        ----------
        wid : str
            Widget ID
        max_length : int
            maximum number of characters in the sub-entries
        new_val : str
            Intended new value to check
        old_val : str
            Current value in the entry
        """
        wid, max_length = int(wid), int(max_length)
        if len(new_val) > max_length:
            return False
        elif new_val == '':
            return True
        else:
            if not new_val.isdigit():
                return False
            else:
                if len(new_val) == max_length:
                    # In this case, move cursor to next widget if we aren't the
                    # last one.
                    if wid != 2:
                        self.entries[wid + 1].focus()
                return True

    def get(self):
        """ Returns a list of strings corresponding to the value of the date"""
        return [e.get() for e in self.entries]

    @property
    def valid(self):
        """ Whether or not the date entered is a valid date """
        date = self.get()
        try:
            datetime(int(date[2]), int(date[1]), int(date[0]))
            return True
        except ValueError:
            return False

    def set(self, value):
        """
        Sets the value of the DateEntry

        Parameters:
        -----------
        value : tuple of string or int's
            The value to set the date to
        """
        self.entry_1.delete(0, END)
        self.entry_1.insert(0, str(value[0]))
        self.entry_2.delete(0, END)
        self.entry_2.insert(0, str(value[1]))
        self.entry_3.delete(0, END)
        self.entry_3.insert(0, str(value[2]))

    def setvar(self, value):
        """
        Sets the value of the DateEntry using Variable's

        Parameters:
        -----------
        value : tuple of StringVar's
            The value to set the date to
        """
        self.entry_1.config(textvariable=value[0])
        self.entry_2.config(textvariable=value[1])
        self.entry_3.config(textvariable=value[2])
