from tkinter import (Toplevel, Frame, Button, Text, END, FLAT, DISABLED)
from webbrowser import open_new as open_hyperlink

from constants import OSCONST

from Management.tkHyperlinkManager import HyperlinkManager


# TODO: change to using a Text widget so have the hyperlink within the text
# TODO: add big biscuit logo.
# TODO: make this look good...


class CreditsPopup(Toplevel):
    def __init__(self, master):
        self.master = master
        Toplevel.__init__(self, self.master)

        self.git_link = "https://github.com/Macquarie-MEG-Research/Biscuit"

        self.title('Credits')

        #img = PhotoImage(file='assets/bisc.png')

        self._create_widgets()

    def _open_link(self):
        open_hyperlink(self.git_link)

    def _create_widgets(self):
        main_frame = Frame(self)
        self.textbox = Text(main_frame, relief=FLAT, undo=False, takefocus=0,
                            bg=OSCONST.TEXT_BG, height=4)
        self.hyperlink = HyperlinkManager(self.textbox)
        info_text = ("Biscuit created by Matt Sanderson for Macquarie "
                     "University.\n"
                     "To find the latest version head to the ")
        link_text = "Biscuit GitHub Repository"
        self.textbox.insert(END, info_text)
        self.textbox.insert(END, link_text,
                            self.hyperlink.add(self._open_link))
        self.textbox.grid(column=0, row=0)
        self.textbox.config(state=DISABLED)
        Button(main_frame, text="Close",
               command=self._exit).grid(column=0, row=1, sticky='w')
        main_frame.grid()

    def _exit(self):
        self.destroy()
