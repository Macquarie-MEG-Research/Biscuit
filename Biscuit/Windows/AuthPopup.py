from tkinter import Toplevel
from tkinter.ttk import Frame, Button, Label, Entry


#TODO: REMOVE

class AuthPopup(Toplevel):
    def __init__(self, master, auth=dict()):
        self.master = master
        Toplevel.__init__(self, self.master)

        self.auth = auth

        self.title('Enter details')

        self._create_widgets()

        self.deiconify()
        self.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

        self.bind('<Return>', self._proceed)

    def _create_widgets(self):
        frame = Frame(self)
        Label(frame, text="Username: ").grid(column=0, row=0)
        self.uname_box = Entry(frame)
        self.uname_box.grid(column=1, row=0)
        Label(frame, text="Password: ").grid(column=0, row=1)
        self.pword_box = Entry(frame, show="*")
        self.pword_box.grid(column=1, row=1)
        btn = Button(frame, text="Cancel", command=self._exit)
        btn.grid(column=0, row=2, sticky='w')
        btn = Button(frame, text="Confirm", command=self._proceed)
        btn.grid(column=1, row=2, sticky='w')
        frame.grid()

    def _exit(self):
        self.auth['uname'] = self.uname_box.get()
        self.auth['pword'] = self.pword_box.get()
        self.withdraw()
        self.update_idletasks()
        self.master.focus_set()
        self.destroy()

    def _proceed(self):
        self.auth['uname'] = self.uname_box.get()
        self.auth['pword'] = self.pword_box.get()
        self.withdraw()
        self.update_idletasks()
        self.master.focus_set()
        self.destroy()
