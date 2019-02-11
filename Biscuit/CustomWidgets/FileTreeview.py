import os.path as op
import os

from .EnhancedTreeview import EnhancedTreeview


class FileTreeview(EnhancedTreeview):
    def __init__(self, master, directory, *args, **kwargs):
        self.master = master
        super(FileTreeview, self).__init__(self.master, *args, **kwargs)

        self.root_path = op.normpath(directory)

        self.index_cache = dict()

#region public methods

    def generate(self, parent, directory=""):
        """
        Iterate over the folder structure and add all found files to the
        treeview.

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
        for file in os.listdir(dir_):
            try:
                fullpath = op.normpath(op.join(dir_, file))

                # need to check to see whether or not the file/folder already
                # exists in the tree:
                exists_id = file_list.get(fullpath, None)
                if op.isdir(fullpath):
                    if exists_id is None:
                        exists_id = self.ordered_insert(parent,
                                                        values=['', fullpath],
                                                        text=file,
                                                        open=False)
                    self.generate(exists_id, directory=fullpath)
                else:
                    fname, ext = op.splitext(file)
                    if exists_id is None:
                        self.insert(parent, 'end',
                                    values=[ext, fullpath],
                                    text=fname, open=False,
                                    tags=(ext))
            except PermissionError:
                # user doesn't have sufficient permissions to open folder so it
                # won't be included
                pass

    def get_filepath(self, sid):
        """ Return the file path corresponding to the provided sid """
        return self.item(sid)['values'][1]

    def get_text(self, sid):
        """ Return the text corresponding to the provided sid """
        return self.item(sid)['text']

    def index(self):
        """ Create a cache of the file information in a flattened way to allow
        fast comparison of existing and new data """
        for sid in self.all_children():
            if sid != '':
                self.index_cache[self.item(sid)['values'][1]] = sid
            else:
                self.index_cache[self.root_path] = ''

    def ordered_insert(self, parent, *args, **kwargs):
        """
        Allows for objects to be inserted in the correct location
        alphabetically. They will be sorted by their text fields.
        This should be extended so that it is sorted by text > then any values
        in order.

        Returns the id of the object that has been inserted
        """
        sort_text = kwargs.get('text', None).lower()
        if sort_text is not None:
            child_folders = [i for i in self.get_children(parent) if
                             op.isdir(self.item(i)['values'][1])]
            child_files = [i for i in self.get_children(parent) if
                           not op.isdir(self.item(i)['values'][1])]
            if op.isdir(kwargs['values'][1]):
                # first iterate over the children that are folders
                if len(child_folders) != 0:
                    for i, child in enumerate(child_folders):
                        if sort_text < self.item(child)['text'].lower():
                            index = i
                            break
                    else:
                        index = i + 1
                else:
                    index = 0
            else:
                folder_num = len(child_folders)
                if len(child_files) != 0:
                    for i, child in enumerate(child_files):
                        if sort_text < self.item(child)['text'].lower():
                            index = i + folder_num
                            break
                    else:
                        index = i + folder_num + 1
                else:
                    index = folder_num

            return self.insert(parent, index, *args, **kwargs)
        raise ValueError("No 'text' argument provided.")

    def refresh(self):
        """
        Refresh the treeview to include any newly added or removed files.
        Returns a list of any added sid's.
        """
        curr_selection = self.focus()
        added_sids = []
        added_files, removed_files = self._find_folder_diff()
        # sort by length to ensure that any new folders are generated first
        added_files.sort(key=lambda x: len(x))
        # reverse sort the removed files to go from the ends of the branches
        removed_files.sort(key=lambda x: len(x), reverse=True)
        # add any new files to the file tree
        # TODO: check any file to see if it has a parent that is a BIDSObject
        # (ie. BIDSTree, Project, Subject, Session), and if so then
        # instantiate the folder as the child object and add it.
        for fullpath in added_files:
            base, file = op.split(fullpath)
            parent = self.sid_from_filepath(base)
            fname, ext = op.splitext(file)

            #if op.isdir(fullpath):
            sid = self.ordered_insert(parent,
                                      values=[ext, fullpath],
                                      text=fname,
                                      open=False)
            self.index_cache[fullpath] = sid
            added_sids.append(sid)
        # remove any removed files from the filetree
        for fpath in removed_files:
            sid = self.index_cache[fpath]
            self.delete(sid)
            del self.index_cache[fpath]
            # TODO: remove from main.preloaded_data somehow??
        if curr_selection not in self.index_cache.values():
            self.selection_set([''])
        return added_sids

    def sid_from_filepath(self, fpath):
        """ Return the sid in the treeview with the given filepath

        Parameters
        ----------
        fpath : str
            Filepath to match

        """
        # Normalise the path just to ensure there are no issues.
        fpath = op.normpath(fpath)
        try:
            return self.index_cache[fpath]
        except KeyError:
            # In this case the file isn't in the cache, however it may still
            # be in the tree. Recurse up the base paths until an object is
            # found then follow it back down.
            temp_fpath = op.dirname(fpath)
            while True:
                if temp_fpath in self.index_cache:
                    sid = self.index_cache[temp_fpath]
                    for child in self.all_children(item=sid):
                        if child['values'][1] == fpath:
                            return child
                _temp_fpath = op.dirname(temp_fpath)
                # ensure we cannot get stuck in an infinte loop
                if _temp_fpath != temp_fpath:
                    temp_fpath = _temp_fpath
                else:
                    break

    def sid_from_text(self, text, _all=False):
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

#region private methods

    def _find_added_files(self):
        """ Return a list of all files paths in the folder that don't currently
        exist in the current file treeview
        """
        new_files = []
        for root, dirs, files in os.walk(self.root_path):
            # add all the new files
            for file in files:
                fpath = op.normpath(op.join(root, file))
                if self.index_cache.get(fpath, None) is None:
                    new_files.append(fpath)
            # add all the new folders
            for dir_ in dirs:
                fpath = op.normpath(op.join(root, dir_))
                if self.index_cache.get(fpath, None) is None:
                    new_files.append(fpath)
        return new_files

    def _find_folder_diff(self):
        """ Create a list of all the files and folders contained within
        self.root_path

        Returns:
        (List of added files/folders, List of removed files/folders)
        """
        contained_files = set()
        for root, dirs, files in os.walk(self.root_path):
            # add all the new files
            for file in files:
                fpath = op.normpath(op.join(root, file))
                contained_files.add(fpath)
            # add all the new folders
            for dir_ in dirs:
                fpath = op.normpath(op.join(root, dir_))
                contained_files.add(fpath)
        prev_files = set(self.index_cache.keys())
        removed_files = (prev_files - contained_files) - set([self.root_path])
        added_files = contained_files - prev_files
        return (list(added_files), list(removed_files))
