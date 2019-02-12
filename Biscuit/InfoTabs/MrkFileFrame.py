from tkinter import StringVar
from tkinter.ttk import Label, Frame, Radiobutton

from Biscuit.Management import ToolTipManager
from Biscuit.utils.constants import MRK_NA, MRK_PRE, MRK_POST, MRK_MULT

# assign the tool tip manager
ttm = ToolTipManager()


class MrkFileFrame(Frame):

    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(MrkFileFrame, self).__init__(self.master, *args, **kwargs)

        self._create_widgets()

        # the associated file
        self._file = None

    def _create_widgets(self):
        self.info_label = Label(self, text="Acquisition time:")
        self.info_label.grid(sticky='nw', column=0, row=0, padx=3)
        ttm.register(self.info_label, "When the marker coil was recorded")
        self.rb_none = Radiobutton(self, text="N/A", variable=StringVar(),
                                   value=MRK_NA)
        self.rb_none.grid(sticky='nw', column=1, row=0, padx=3)
        ttm.register(self.rb_none, ("Select this if there was only one marker "
                                    "coil recording for the associated .con "
                                    "file."))
        self.rb_pre = Radiobutton(self, text="Pre", variable=StringVar(),
                                  value=MRK_PRE)
        self.rb_pre.grid(sticky='nw', column=2, row=0, padx=3)
        ttm.register(self.rb_pre, ("Select this if there were multiple marker "
                                   "coils recorded and this was the first."))
        self.rb_post = Radiobutton(self, text="Post", variable=StringVar(),
                                   value=MRK_POST)
        self.rb_post.grid(sticky='nw', column=3, row=0, padx=3)
        ttm.register(self.rb_post, ("Select this if there were multiple "
                                    "marker coils recorded and this was the "
                                    "second."))
        self.rb_multiple = Radiobutton(self, text="Multiple",
                                       variable=StringVar(), value=MRK_MULT)
        self.rb_multiple.grid(sticky='nw', column=4, row=0, padx=3)
        ttm.register(self.rb_multiple, ("Select this if the marker was used "
                                        "as both a pre- and post- recording "
                                        "marker.\nThis will be used when the "
                                        "marker coil is recorded between two "
                                        "other recordings."))

    def update_widgets(self):
        self.rb_none.config(variable=self.file.acquisition)
        self.rb_pre.config(variable=self.file.acquisition)
        self.rb_post.config(variable=self.file.acquisition)
        self.rb_multiple.config(variable=self.file.acquisition)

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
            self.update_widgets()
