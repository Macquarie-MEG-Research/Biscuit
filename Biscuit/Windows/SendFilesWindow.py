from tkinter import Toplevel, IntVar, StringVar, BooleanVar
from tkinter.ttk import Frame, Label, Button, Progressbar, Checkbutton
import os
import os.path as path
from subprocess import check_call, CalledProcessError

from bidshandler import BIDSTree

from Biscuit.Windows.AuthPopup import AuthPopup
from Biscuit.Management import RangeVar, ToolTipManager
from Biscuit.utils.utils import get_fsize, threaded
from Biscuit.utils.constants import OSCONST
from Biscuit.utils.BIDSCopy import BIDSCopy

ttm = ToolTipManager()


class SendFilesWindow(Toplevel):
    """
    A popup window to show the progress of the transfer to the server

    Parameters
    ----------
    master : instance of tkinter.Widget
        Parent widget for this Toplevel widget
    src : Instance of bidshandler.[BIDSTree, Project, Subject, Session]
        Source object to copy over
    dst : string
        Destination folder or location on server.
    set_copied : bool
        Change the name of the source directory to have `_copied` appended
        to indicate that the data has been transferred successfully.
    opt_verify : bool
        Whether to provide the option to verify data or not.
        If the option is provided then it will be off by default.

    """
    def __init__(self, master, src, dst, set_copied=False, opt_verify=False):
        self.master = master
        self.src = src
        self.dst = dst
        self.set_copied = set_copied
        self.opt_verify = opt_verify
        Toplevel.__init__(self, self.master)
        self.withdraw()
        if master.winfo_viewable():
            self.transient(master)

        self.title('Transfer files')

        # define some variables we need
        self.has_access = False
        self.force_override = BooleanVar(value=False)
        if opt_verify:
            self.verify = BooleanVar(value=False)
        else:
            self.verify = BooleanVar(value=True)
        # total number of files to transfer
        self.file_count_var = StringVar(value="Number of files: {0}")
        self.total_file_size = StringVar(value="Total file size: {0}")
        self.file_count = 0
        total_file_size = 0
        for root, _, files in os.walk(self.src.path):
            self.file_count += len(files)
            for file in files:
                fpath = path.join(root, file)
                fsize = os.stat(fpath).st_size
                total_file_size += fsize
        fsize = get_fsize(total_file_size)
        self.file_count_var.set(
            self.file_count_var.get().format(self.file_count))
        self.total_file_size.set(self.total_file_size.get().format(fsize))
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

        # TODO: add line to show destination for data? maybe source too...

        # number of files being transferred and total size
        lbl_file_count = Label(frame, textvariable=self.file_count_var)
        lbl_file_count.grid(column=0, row=0)
        lbl_total_size = Label(frame, textvariable=self.total_file_size)
        lbl_total_size.grid(column=1, row=0)
        # info about current file being transferred
        label2 = Label(frame, text="Current file being transferred:")
        label2.grid(column=0, row=1, columnspan=2, sticky='w')
        lbl_curr_file = Label(frame, textvariable=self.curr_file, width=60)
        lbl_curr_file.grid(column=0, row=2)
        self.file_prog = Progressbar(frame, variable=self.curr_file_progress)
        self.file_prog.grid(column=1, row=2, pady=2)
        # info about total progress
        label3 = Label(frame, text="Overall progress:")
        label3.grid(column=0, row=3, sticky='w')
        total_prog = Progressbar(frame, variable=self.transferred_count,
                                 maximum=self.file_count)
        total_prog.grid(column=1, row=3)

        # buttons
        btn_frame = Frame(frame)
        force_check = Checkbutton(btn_frame, text="Force",
                                  variable=self.force_override)
        force_check.grid(column=0, row=0, sticky='e')
        verify_check = Checkbutton(btn_frame, text="Verify",
                                   variable=self.verify)
        if self.opt_verify:
            verify_check.grid(column=1, row=0, sticky='e')
        ttm.register(force_check,
                     ("Whether to force the overwriting of current data.\n"
                      "This should only be done if there was an error and the "
                      "data needs to be re-sent."))
        btn_start = Button(btn_frame, text="Begin", command=self._transfer)
        btn_start.grid(column=2, row=0, sticky='e')
        btn_exit = Button(btn_frame, text="Exit", command=self._exit)
        btn_exit.grid(column=3, row=0, sticky='w')
        btn_frame.grid(column=0, row=4, columnspan=2)

    def _check_write_access(self):
        """Check whether or not the user is authenicated to write to the
        archive.
        """
        # TODO: make more generic? (and check if this even works???)
        auth = dict()
        if not os.access(OSCONST.MEG_RAW_PATH, os.W_OK):
            # create a popup to get the username and password
            AuthPopup(self, auth)

            if auth.get('uname', None) and auth.get('pword', None):
                auth_cmd = OSCONST.ACCESS_CMD.format(
                    unc_path=OSCONST.MEG_RAW_PATH,
                    uname=auth.get('uname', ''),
                    pword=auth.get('pword', ''))
                del auth
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
            self.has_access = True

    @threaded
    def _transfer(self):
        """Transfer all the files in self.src to the server."""
        copy_func = BIDSCopy(overwrite=self.force_override.get(),
                             verify=self.verify.get(),
                             file_name_tracker=self.curr_file,
                             file_num_tracker=self.transferred_count,
                             file_prog_tracker=self.curr_file_progress)
        self.curr_file.set('Mapping destination BIDS structure...')
        dst_folder = BIDSTree(self.dst)
        dst_folder.add(self.src, copier=copy_func.copy_files)
        self.transferred_count.set(self.file_count)
        if self.set_copied:
            self._rename_complete()
        self.curr_file.set('Complete!')

    def _rename_complete(self):
        """Rename the folder to have `_copied` appended to the name."""
        if not self.src.path.endswith('_copied'):
            fname = path.basename(self.src.path)
            new_path = "{0}_copied".format(self.src.path)
            os.rename(self.src.path, new_path)
            # fix the path in the BIDSTree object also
            if isinstance(self.src, BIDSTree):
                self.src.path = new_path
            # also rename the branch in the filetree
            sid = self.master.file_treeview.sid_from_text(fname)
            self.master.file_treeview.item(sid[0],
                                           text="{0}_copied".format(fname))
            # the hidden filepath value also needs to be updated
            new_vals = list(self.master.file_treeview.item(sid[0])['values'])
            new_vals[1] = new_path
            self.master.file_treeview.item(sid[0], values=new_vals)

    def _update_file_progress(self):
        self.file_prog.config(maximum=self.curr_file_progress.max)

    def _exit(self):
        self.withdraw()
        self.update_idletasks()
        self.master.focus_set()
        self.destroy()
