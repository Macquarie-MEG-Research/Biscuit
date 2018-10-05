#from tkinter import Frame
from tkinter.ttk import Label, Frame


class GenericInfoFrame(Frame):

    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(GenericInfoFrame, self).__init__(self.master, *args, **kwargs)

        self._create_widgets()

        # the associated file
        self._file = None

    def _create_widgets(self):
        self.info_label = Label(self, text="Loading File...")
        self.info_label.grid(sticky='nw')

    def set_text(self, text):
        self.info_label.config(text=text)

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
