""" Slightly modified versions of shutil.copy to provide sub-file resolution
of file transfer
"""

import os
import stat
from hashlib import md5


class SameFileError(OSError):
    """Raised when source and destination are the same file."""


def _samefile(src, dst):
    # Macintosh, Unix.
    if hasattr(os.path, 'samefile'):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    # All other platforms: check for same pathname.
    return (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))


def copyfileobj(fsrc, fdst, length=1024 * 1024, tracker=None, verify=False):
    """ copy data from the file-like object fsrc to the file-like object fdst

    Parameters
    ----------
    fsrc : file-like object
        The source file
    fdst : file-like object
        The destination file
    length : int
        Size of the chunks to copy at a time.
    tracker : Instance of tkinter.IntVar
        A Variable which is used to track the transfer progress
    verify : bool
        Whether or not to verify the data is copied correctly.
        If True this returns the hash object (md5)

    """
    if tracker is not None:
        tracker.set(0)
        curr_block = 0
    if verify:
        contents_hash = md5()
    while 1:
        buf = fsrc.read(length)
        if not buf:
            if tracker is not None:
                tracker.set(tracker.max)
            break
        fdst.write(buf)
        if verify:
            contents_hash.update(buf)
        if tracker is not None:
            curr_block += 1
            tracker.set(length * curr_block)
    if verify:
        return contents_hash


def copyfile(src, dst, *, follow_symlinks=True, tracker=None, verify=False):
    # Copy data from src to dst.

    # If follow_symlinks is not set and src is a symbolic link, a new
    # symlink will be created instead of copying the file it points to.

    if _samefile(src, dst):
        raise SameFileError("{!r} and {!r} are the same file".format(src, dst))

    for fn in [src, dst]:
        try:
            os.stat(fn)
        except OSError:
            # File most likely does not exist
            pass

    if not follow_symlinks and os.path.islink(src):
        os.symlink(os.readlink(src), dst)
    else:
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                if tracker is not None:
                    tracker.max = os.stat(src).st_size
                file_hash = copyfileobj(fsrc, fdst, tracker=tracker,
                                        verify=verify)
    if verify:
        return dst, file_hash
    else:
        return dst


def copymode(src, dst, *, follow_symlinks=True):
    """Copy mode bits from src to dst.

    If follow_symlinks is not set, symlinks aren't followed if and only
    if both `src` and `dst` are symlinks.  If `lchmod` isn't available
    (e.g. Linux) this method does nothing.

    """
    if not follow_symlinks and os.path.islink(src) and os.path.islink(dst):
        if hasattr(os, 'lchmod'):
            stat_func, chmod_func = os.lstat, os.lchmod
        else:
            return
    elif hasattr(os, 'chmod'):
        stat_func, chmod_func = os.stat, os.chmod
    else:
        return

    st = stat_func(src)
    chmod_func(dst, stat.S_IMODE(st.st_mode))


def copy(src, dst, *, follow_symlinks=True, tracker=None, verify=False):
    """
    Copy data and mode bits ("cp src dst"). Return the file's destination.

    The destination may be a directory.

    If follow_symlinks is false, symlinks won't be followed. This
    resembles GNU's "cp -P src dst".

    If source and destination are the same file, a SameFileError will be
    raised.
    """

    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if verify:
        _, file_hash = copyfile(src, dst, follow_symlinks=follow_symlinks,
                                tracker=tracker, verify=verify)
    else:
        copyfile(src, dst, follow_symlinks=follow_symlinks, tracker=tracker)
    copymode(src, dst, follow_symlinks=follow_symlinks)
    if verify:
        return dst, file_hash
    else:
        return dst
