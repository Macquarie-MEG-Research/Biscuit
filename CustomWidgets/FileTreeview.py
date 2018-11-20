import os.path as path
from os import listdir

from CustomWidgets import EnhancedTreeview


class FileTreeview(EnhancedTreeview):
    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(FileTreeview, self).__init__(self.master, *args, **kwargs)

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
            for file in listdir(dir_):
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
        pass