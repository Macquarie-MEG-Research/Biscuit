from tkinter import Toplevel, IntVar, StringVar
from tkinter.ttk import Frame, Label, Button, Progressbar
import os
import os.path as path
from Windows.AuthPopup import AuthPopup
from Management import RangeVar

from utils.BIDSMerge import get_projects, merge_proj

from subprocess import check_call, CalledProcessError

MEG_RAW_PATH = "\\\\file.cogsci.mq.edu.au\\MEG_RAW"
SVR_PATH = "\\\\file.cogsci.mq.edu.au\\Homes\\mq20184158"

ACCESS_CMD = 'NET USE "{unc_path}" "{pword}" /USER:"MQAUTH\\{uname}"'


class SendFilesWindow(Toplevel):
    """
    A popup window to show the progress of the transfer to the server
    """
    def __init__(self, master, fpath):
        self.master = master
        self.fpath = fpath
        print(self.fpath)
        Toplevel.__init__(self, self.master)
        self.withdraw()
        if master.winfo_viewable():
            self.transient(master)

        self.title('Transfer file to MEG_RAW')

        # define some variables we need
        self.has_access = False
        # total number of files to transfer
        self.file_count = IntVar()
        file_count = sum([len(files) for _, _, files in os.walk(self.fpath)])
        self.file_count.set(file_count)
        # current name of file being transferred
        self.curr_file = StringVar(value="None")
        # number of files that have been transferred
        self.transferred_count = IntVar()
        # internal progress variable
        self.curr_file_progress = RangeVar(
            max_val=0, max_val_callback=self._update_file_progress)

        self.protocol("WM_DELETE_WINDOW", self._exit)

        self._create_widgets()
        # make sure that it is possible to write to MEG_RAW
        self._check_write_access()

        self.deiconify()
        self.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def _create_widgets(self):
        frame = Frame(self)
        frame.grid(sticky='nsew')

        # number of files being transferred
        label1 = Label(frame, text="Number of files to transfer: ")
        label1.grid(column=0, row=0)
        lbl_file_count = Label(frame, textvariable=self.file_count)
        lbl_file_count.grid(column=1, row=0)
        # info about current file being transferred
        label2 = Label(frame, text="Current file being transferred:")
        label2.grid(column=0, row=1, columnspan=2)
        lbl_curr_file = Label(frame, textvariable=self.curr_file, width=50)
        lbl_curr_file.grid(column=0, row=2)
        self.file_prog = Progressbar(frame, variable=self.curr_file_progress)
        self.file_prog.grid(column=1, row=2)
        # info about total progress
        label3 = Label(frame, text="Overall progress:")
        label3.grid(column=0, row=3)
        total_prog = Progressbar(frame, variable=self.transferred_count,
                                 maximum=self.file_count.get())
        total_prog.grid(column=1, row=3)

        # bottom button frame
        btn_frame = Frame(frame)
        btn_frame.grid(sticky='nsew', column=0, row=4, columnspan=2)
        btn_start = Button(btn_frame, text="Begin", command=self._transfer)
        btn_start.grid(column=0, row=0)
        btn_cancel = Button(btn_frame, text="Cancel", command=None)
        btn_cancel.grid(column=1, row=0)
        btn_exit = Button(btn_frame, text="Exit", command=self._exit)
        btn_exit.grid(column=2, row=0)

    def _check_write_access(self):
        """ Check whether or not the user is authenicated to write to the
        archive
        """
        # TODO: fix up more
        auth = dict()
        if not os.access(MEG_RAW_PATH, os.W_OK):
            # create a popup to get the username and password
            AuthPopup(self, auth)

            if auth.get('uname', None) and auth.get('pword', None):
                auth_cmd = ACCESS_CMD.format(unc_path=MEG_RAW_PATH,
                                             uname=auth.get('uname', ''),
                                             pword=auth.get('pword', ''))
                del auth
                print(auth_cmd)
                try:
                    check_call(auth_cmd)
                    self.has_access = True
                    del auth_cmd
                except CalledProcessError:
                    # authentication didn't work...
                    # raise a popup saying the password may have been wrong...?
                    pass
            else:
                # the user entered either no password, username or both.
                # see if they want to enter a new one...
                pass
        else:
            print('you have write access!')
            self.has_access = True

    def _transfer(self):
        """ Transfer all the files in self.fpath to the server """
        right = path.join(SVR_PATH, 'BIDS')

        proj_list = get_projects(self.fpath)
        for proj_path in proj_list:
            merge_proj(path.join(self.fpath, proj_path),
                       path.join(right, proj_path),
                       file_name_tracker=self.curr_file,
                       file_num_tracker=self.transferred_count,
                       file_prog_tracker=self.curr_file_progress)

    def _update_file_progress(self):
        #print(self.curr_file_progress.max)
        self.file_prog.config(maximum=self.curr_file_progress.max)

    def _exit(self):
        # TODO: popup window notifying that any unsaved changes will be lost?
        self.withdraw()
        self.update_idletasks()
        self.master.focus_set()
        self.destroy()
