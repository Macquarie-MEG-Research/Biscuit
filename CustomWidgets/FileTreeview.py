import os.path as path
import os

from CustomWidgets import EnhancedTreeview


class FileTreeview(EnhancedTreeview):
    def __init__(self, master, directory, *args, **kwargs):
        self.master = master
        super(FileTreeview, self).__init__(self.master, *args, **kwargs)

        self.root_path = directory

        self.index_cache = dict()

    def generate(self, parent, directory=""):
        """
        Iterate over the folder structure and list all the files in the
        treeview

        Parameters
        ----------
        parent : str
            The sid of the parent in the treeview ('' if the root)
        directory : str | path-like object
            The path which is to have all the files listed from.

        """
        dir_ = directory

        # If not directory is specified exit this function. Elsewhere we will
        # set the panel on the right hand side to have a message that no folder
        # has been selected as the base one and give details on how to set it.
        if dir_ == "":
            return

        # create a mapping of full paths to id's
        curr_children = self.get_children(parent)
        file_list = dict(
            zip([self.item(child)['values'][1] for child in
                 curr_children], curr_children))

        # we want to put folders above files (it looks nicer!!)
        try:
            for file in os.listdir(dir_):
                fullpath = path.join(dir_, file)

                # need to check to see whether or not the file/folder already
                # exists in the tree:
                exists_id = file_list.get(fullpath, None)
                if path.isdir(fullpath):
                    if exists_id is None:
                        exists_id = self.ordered_insert(parent,
                                                        values=['', fullpath],
                                                        text=file,
                                                        open=False)
                    self.generate(exists_id, directory=fullpath)
                else:
                    fname, ext = path.splitext(file)
                    if exists_id is None:
                        self.insert(parent, 'end',
                                    values=[ext, fullpath],
                                    text=fname, open=False,
                                    tags=(ext))
        except PermissionError:
            # user doesn't have sufficient permissions to open folder so it
            # won't be included
            pass

    def refresh(self):
        """ Refresh the treeview to include any newly found files """
        new_files = self._find_new_files()
        # sort by length to ensure that any new folders are generated first
        new_files.sort(key=lambda x: len(x))
        for fullpath in new_files:
            base, file = path.split(fullpath)
            parent = self.sid_from_filepath(base)
            fname, ext = path.splitext(file)
            sid = self.ordered_insert(parent,
                                      values=[ext, fullpath],
                                      text=fname, open=False,
                                      tags=(ext))
            self.index_cache[fullpath] = sid

    def index(self):
        """ Create a cache of the file information in a flattened way to allow
        fast comparison of existing and new data """
        for sid in self.all_children():
            if sid != '':
                self.index_cache[self.item(sid)['values'][1]] = sid
            else:
                self.index_cache[self.root_path] = ''

    def _find_new_files(self):
        """ Return a list of all files paths in the folder that don't currently
        exist in the current file treeview
        """
        new_files = []
        for root, dirs, files in os.walk(self.root_path):
            # add all the new files
            for file in files:
                fpath = path.join(root, file)
                if self.index_cache.get(fpath, None) is None:
                    new_files.append(fpath)
            # add all the new folders
            for dir_ in dirs:
                fpath = path.join(root, dir_)
                if self.index_cache.get(fpath, None) is None:
                    new_files.append(fpath)
        return new_files

    def get_text(self, sid):
        """ Return the text corresponding to the provided sid """
        return self.item(sid)['text']

    def get_filepath(self, sid):
        """ Return the file path corresponding to the provided sid """
        return self.item(sid)['values'][1]

    # TODO: rename to `sid_from_text` once merged into MQ_master
    def get_sid_from_text(self, text, _all=False):
        """ Return the sid(s) in the treeview with the given text

        Parameters
        ----------
        text : str
            text value to match.
        _all : bool
            Whether or not to return all the results or just the first

        """
        rtn_list = []
        for sid in self.all_children():
            if self.item(sid)['text'] == text:
                if _all:
                    rtn_list.append(sid)
                else:
                    return [sid]
        return rtn_list

    def sid_from_filepath(self, fpath):
        """ Return the sid in the treeview with the given filepath

        Parameters
        ----------
        fpath : str
            Filepath to match

        """
        return self.index_cache[fpath]
