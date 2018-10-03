from tkinter import Frame, WORD, END
from tkinter.scrolledtext import ScrolledText


class ScrolledTextInfoFrame(Frame):

    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(ScrolledTextInfoFrame, self).__init__(self.master, *args,
                                                    **kwargs)

        self._create_widgets()

        # the associated file
        self._file = None

    def _create_widgets(self):
            # create a Text widget and read in the file
            self.textentry = ScrolledText(self, wrap=WORD)
            self.textentry.grid(column=0, row=0, sticky='nsew')
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

    def update(self):
        self.textentry.delete(1.0, END)
        with open(self.file.file, 'r') as file:
            self.textentry.insert(END, file.read())

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
            self._file = other
            self.update()
