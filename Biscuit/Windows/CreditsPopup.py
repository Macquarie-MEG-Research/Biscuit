from tkinter import Toplevel, Text, END, FLAT, DISABLED, messagebox
from tkinter.ttk import Frame, Button, Label
from webbrowser import open_new as open_hyperlink
import shutil

from Biscuit.utils.constants import OSCONST
from Biscuit.utils.Update import get_latest_release, do_update, update_mne_bids
from Biscuit.utils.version import Version
from Biscuit.Management.tkHyperlinkManager import HyperlinkManager


# TODO: add big biscuit logo.
# TODO: make this look good...


class CreditsPopup(Toplevel):
    def __init__(self, master):
        self.master = master
        Toplevel.__init__(self, self.master)

        self.git_link = "https://github.com/Macquarie-MEG-Research/Biscuit"

        self.title('Credits')

        self.temp_dir = None

        # img = PhotoImage(file='assets/bisc.png')

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
                     "To find out more head to the ")
        link_text = "Biscuit GitHub Repository"
        self.textbox.insert(END, info_text)
        self.textbox.insert(END, link_text,
                            self.hyperlink.add(self._open_link))
        self.textbox.grid(column=0, row=0, columnspan=3)
        self.textbox.config(state=DISABLED)
        Button(main_frame, text="Close",
               command=self._exit).grid(column=0, row=1, sticky='w')
        update_btn = Button(main_frame, text="Check for Updates",
                            command=self._check_for_updates)
        update_btn.grid(column=1, row=1, sticky='w', padx=2)
        version_lbl = Label(
            main_frame, text="Current version: {0}".format(OSCONST.VERSION))
        version_lbl.grid(column=2, row=1, sticky='w', padx=2)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.columnconfigure(2, weight=0)

        main_frame.grid(sticky='nsew')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def _check_for_updates(self):
        latest_release = get_latest_release()
        latest_version = latest_release.get('tag_name', 'v0.0.0.0')
        latest_version = Version.from_repr(latest_version)
        if latest_version > Version.from_repr(OSCONST.VERSION):
            if messagebox.askyesno("Update Biscuit",
                                   "Would you like to update Biscuit to the "
                                   "most recent version? "
                                   "({0})".format(str(latest_version)),
                                   parent=self):
                do_update(latest_release)
        else:
            messagebox.showinfo("Up to date!", "Biscuit is up to date.",
                                parent=self)
        # check if we want mne-bids to be updated also:
        if messagebox.askyesno("Update MNE-BIDS",
                               "Would you like to update MNE-BIDS to the "
                               "most recent version of the master branch?"
                               "This may be less stable than the release "
                               "version but may be required for certain "
                               "functionality. DO NOT press 'yes' unless you "
                               "know what you are doing and how to revert to "
                               "a previous mne-bids version!",
                               parent=self):
            self.temp_dir = update_mne_bids()

    def _exit(self):
        if self.temp_dir is not None:
            shutil.rmtree(self.temp_dir)
        self.destroy()
