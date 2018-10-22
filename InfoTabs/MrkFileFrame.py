from tkinter import StringVar
from tkinter.ttk import Label, Frame, Radiobutton

from Management import ToolTipManager

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
                                   value="n/a")
        self.rb_none.grid(sticky='nw', column=1, row=0, padx=3)
        ttm.register(self.rb_none, ("Select this if there was only one marker "
                                    "coil recording for the associated .con "
                                    "file."))
        self.rb_pre = Radiobutton(self, text="Pre", variable=StringVar(),
                                  value="pre")
        self.rb_pre.grid(sticky='nw', column=2, row=0, padx=3)
        ttm.register(self.rb_pre, ("Select this if there were multiple marker "
                                   "coils recorded and this was the first."))
        self.rb_post = Radiobutton(self, text="Post", variable=StringVar(),
                                   value="post")
        self.rb_post.grid(sticky='nw', column=3, row=0, padx=3)
        ttm.register(self.rb_post, ("Select this if there were multiple "
                                    "marker coils recorded and this was the "
                                    "second."))

    def update_widgets(self):
        self.rb_none.config(variable=self.file.acquisition)
        self.rb_pre.config(variable=self.file.acquisition)
        self.rb_post.config(variable=self.file.acquisition)

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
