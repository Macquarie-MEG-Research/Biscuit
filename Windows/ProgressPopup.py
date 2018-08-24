from tkinter import Toplevel, Frame, Label, Button


class ProgressPopup(Toplevel):
    def __init__(self, master, progress_var):
        self.master = master
        Toplevel.__init__(self, self.master)

        self.progress_var = progress_var

        self._create_widgets()

    def _create_widgets(self):
        main_frame = Frame(self)
        Label(main_frame, text="Progress: ").grid(column=0, row=0)
        Label(main_frame, textvariable=self.progress_var).grid(column=1, row=0)
        Button(main_frame, text="Close",
               command=self._exit).grid(column=0, row=1)
        main_frame.grid()

    def _exit(self):
        self.destroy()