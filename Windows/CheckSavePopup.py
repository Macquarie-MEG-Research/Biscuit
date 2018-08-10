from tkinter import simpledialog, ACTIVE
from tkinter.ttk import Label, Button, Frame


## need to fix the style issues here. Maybe just write this cusotm instead of
# subclassing from the simpledialog.Dialog class

class CheckSavePopup(simpledialog.Dialog):
    def body(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.frame.grid(sticky='nsew')
        Label(self.frame, text=("Are you sure you want to exit? You may have "
                            "unsaved data...")).grid(row=0, columnspan=3)

    def buttonbox(self):


        w = Button(self.frame, text="Save and Exit", width=15,
                   command=self.save, default=ACTIVE)
        w.grid(column=0, row=1, padx=5, pady=5)
        w = Button(self.frame, text="Go back!", width=15, command=self.cancel)
        w.grid(column=1, row=1, padx=5, pady=5)
        w = Button(self.frame, text="Exit", width=15, command=self.exit)
        w.grid(column=2, row=1, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

    def save(self, event=None):
        self.result = "save"
        self.end()

    def cancel(self, event=None):
        self.result = "cancel"
        self.end()

    def exit(self, event=None):
        self.result = "exit"
        self.end()

    def end(self):
        # close the dialog
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()
