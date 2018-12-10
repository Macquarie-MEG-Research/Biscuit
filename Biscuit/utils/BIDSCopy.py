"""
Custom copying function for copying and tracking the progress of BIDS data
"""

import shutil
import os
import os.path as op
from hashlib import md5
import logging

from Biscuit.utils.copyutils import copy

BUFFER_SIZE = 1024 * 1024     # 1Mb


class BIDSCopy():
    """ combine two bids-compatible folders

    Parameters
    ----------
    overwrite : bool
        Whether or not to overwrite the currently existing data
        Defaults to False.
    file_name_tracker : Instance of StringVar
        An instance of a tkinter.StringVar which has the filename of the
        current file being transfer. This is for tracking purposes in the
        Windows.SendFilesWindow window.
    file_num_tracker : Instance of IntVar
        An instance of a tkinter.IntVar which is incremented after each file
        has been transferred. This is for tracking purposes in the
        Windows.SendFilesWindow window.
    file_prog_tracker : Instance of IntVar
        An instance of a tkinter.IntVar which is used to track the transfer
        progress on a file-by-file basis. This is passed to the modified copy
        function from shutil to track  the rate at whic the indiviual files
        themselves are being transferred. This is for tracking purposes in the
        Windows.SendFilesWindow window.)
    """
    def __init__(self, overwrite=False, file_name_tracker=None,
                 file_num_tracker=None, file_prog_tracker=None):
        self.overwrite = overwrite
        self.file_name_tracker = file_name_tracker
        self.file_num_tracker = file_num_tracker
        self.file_prog_tracker = file_prog_tracker

    def copy_files(self, src_files, dst_files):
        """Copy the src_files to the corresponding location in dst_files."""
        print(src_files)
        assert len(src_files) == len(dst_files)
        for fnum in range(len(src_files)):
            src = src_files[fnum]
            dst = dst_files[fnum]
            # Make any folders that don't exist
            if not op.exists(op.dirname(dst_files[fnum])):
                os.makedirs(op.dirname(dst_files[fnum]), exist_ok=True)
            # assign the name
            if self.file_name_tracker is not None:
                self.file_name_tracker.set(op.basename(src))
            _, file_hash = copy(src, dst, tracker=self.file_prog_tracker,
                                verify=True)
            if os.stat(src).st_size > BUFFER_SIZE:
                # change the file name to indiciate that it is being verified.
                # Only do for files bigger than 1Mb as it isn't worth it for
                # small files since they will be done instantly.
                self.file_name_tracker.set(self.file_name_tracker.get() +
                                           ' (verifying)')
            if file_hash.hexdigest() != md5hash(dst).hexdigest():
                # log a warning
                logging.warning(
                    "{0} was not copied correctly, "
                    "retrying...".format(src))
                _, file_hash = copy(
                    src, dst, tracker=self.file_prog_tracker, verify=True)
                if file_hash.hexdigest() != md5hash(dst).hexdigest():
                    # in this case it has failed *twice* which should be
                    # *very* unlikely. Raise an error.
                    raise ValueError("{0} wasn't copied over correctly. "
                                     "Please ensure there is no issue with "
                                     "the file".format(src))
            shutil.copy(src_files[fnum], dst_files[fnum])
            if self.file_num_tracker is not None:
                self.file_num_tracker.set(fnum + 1)

        self.file_name_tracker.set("Complete!")


def md5hash(src):
    """ Gets the md5 hash of a file in chunks """
    contents_hash = md5()
    with open(src, 'rb') as fsrc:
        while True:
            data = fsrc.read(BUFFER_SIZE)
            if not data:
                break
            contents_hash.update(data)
    return contents_hash
