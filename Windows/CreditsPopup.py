from tkinter import Toplevel, Frame, Label, Button, PhotoImage
import webbrowser


# Credit to Steven Summers from StackExchange
# https://stackoverflow.com/a/32985240
def callback(event, hyperlink):
    webbrowser.open_new(hyperlink)


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

    def _create_widgets(self):
        main_frame = Frame(self)
        info_text = ("Biscuit created by Matt Sanderson for Macquarie "
                     "University.\n"
                     "To find the latest version head to:")
        link_text = "Biscuit GitHub Repository"
        info_lbl = Label(main_frame, text=info_text)
        info_lbl.grid(row=0, column=0)
        link_lbl = Label(main_frame, text=link_text, fg='blue')
        link_lbl.grid(row=1, column=0)
        link_lbl.bind("<Button-1>", lambda e: callback(e, self.git_link))
        Button(main_frame, text="Close",
               command=self._exit).grid(column=0, row=2, sticky='w')
        main_frame.grid()

    def _exit(self):
        self.destroy()
