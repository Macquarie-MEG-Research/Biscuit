from tkinter import Toplevel, Frame, Label, Button


class ProgressPopup(Toplevel):
    """
    TODO: completely overhaul
    - add a tab system (Basic/Advanced output tabs)
    Basic tab:
        - maybe a condensed version of the output? Just the 'writeline' parts
    Advanced tab:
        - full output directly from mne-bids
    """
    def __init__(self, master, progress_var, job_name_var):
        self.master = master
        Toplevel.__init__(self, self.master)

        self.title('Conversion Progress')

        self.job_name_var = job_name_var
        self.streamedvar = progress_var
        self.progress_var = self.streamedvar.curr_value

        self._create_widgets()

    def _create_widgets(self):
        main_frame = Frame(self)
        Label(main_frame,
              text="Converting, please wait.").grid(row=0, column=0,
                                                    columnspan=2)
        Label(main_frame, text="Processing job:").grid(column=0, row=1)
        Label(main_frame, textvariable=self.job_name_var).grid(column=1, row=1)
        Label(main_frame, text="Progress:").grid(column=0, row=2)
        Label(main_frame, textvariable=self.progress_var).grid(column=1, row=2)
        Button(main_frame, text="Close",
               command=self._exit).grid(column=0, row=3)
        main_frame.grid()

    def _exit(self):
        self.destroy()
