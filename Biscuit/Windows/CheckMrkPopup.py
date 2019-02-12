from tkinter import simpledialog, ACTIVE
from tkinter.ttk import Label, Button, Frame

from Biscuit.utils.constants import MRK_PRE, MRK_POST

# need to fix the style issues here. Maybe just write this custom instead of
# subclassing from the simpledialog.Dialog class


class CheckMrkPopup(simpledialog.Dialog):
    def body(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.frame.grid(sticky='nsew')
        Label(self.frame,
              text=("Is the selected .mrk recorded before or after the "
                    "selected con file(s)?")).grid(row=0, columnspan=3)

    def buttonbox(self):
        w = Button(self.frame, text="Before", width=15,
                   command=self.before, default=ACTIVE)
        w.grid(column=0, row=1, padx=5, pady=5)
        w = Button(self.frame, text="After", width=15, command=self.after)
        w.grid(column=1, row=1, padx=5, pady=5)
        w = Button(self.frame, text="Cancel", width=15, command=self.exit)
        w.grid(column=2, row=1, padx=5, pady=5)

        self.bind("<Escape>", self.cancel)

    def before(self, event=None):
        self.result = MRK_PRE
        self.end()

    def after(self, event=None):
        self.result = MRK_POST
        self.end()

    def exit(self, event=None):
        self.result = None
        self.end()

    def end(self):
        # close the dialog
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()
