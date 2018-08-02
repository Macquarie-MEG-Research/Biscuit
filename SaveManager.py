import pickle
from FileTypes import FileInfo, con_file, mrk_file
import os.path as path


class SaveManager():
    """
    A class to organise the saving of all the data produced while interacting with the GUI
    This will take any file that has had any changes made to it and store them to the HDD
    so that the next time a user runs the program they can be retreived and applied to avoid
    data having to be entered multiple times
    """
    def __init__(self, parent=None, save_path=""):
        """
        parent is the main GUI object
        savepath is the location of the save data
        We will mainly just be getting the preloaded data from it so we can
        read any data we need when we are saving
        """
        self.parent = parent
        self.save_path = save_path

        self.treeview_ids = []

    def load(self):
        """
        This needs some error handling!!
        """
        _data = dict()

        # get the list of all children to the treeview:
        self.treeview_ids = list(self.parent.file_treeview.all_children())
        self.treeview_ids.remove('')        # remove root

        # first retrieve all the data from the save file
        if path.exists(self.save_path):
            for file in self._load_gen():
                print('loaded file: {0}'.format(file.file))
                # set the file's id from the treeview
                sid = self.get_file_id(file.file)
                file.ID = sid
                # *then* associate the treeview with the file
                file.treeview = self.parent.file_treeview
                # then add the file to the preloaded data
                _data[file.ID] = file
            self.parent.preloaded_data = _data

            # now fix up any associated_mrk's that need to be actual
            # mrk_file objects
            for _, obj in self.parent.preloaded_data.items():
                if isinstance(obj, con_file):
                    mrk_paths = obj.associated_mrks
                    for i, mrk_path in enumerate(mrk_paths):
                        sid = self.get_file_id(mrk_path)
                        try:
                            mrk_paths[i] = self.parent.preloaded_data[sid]
                        except KeyError:
                            mrk_paths[i] = mrk_file(id_=sid, file=mrk_path)
            if len(_data) != 0:
                print(_data, 'data something')
            else:
                print("all loaded fine!!")

    def get_file_id(self, path_):
        """
        Returns the id of the entry in the treeview that has the specified
        path.
        """
        for sid in self.treeview_ids:
            if self.parent.file_treeview.item(sid)['values'][1] == path_:
                return sid
        else:
            raise FileNotFoundError

    def _load_gen(self):
        """
        This is a generator to iterate over the specified file and
        return the values as required

        script c/o Lutz Prechelt (cf. https://stackoverflow.com/questions/20716812/saving-and-loading-multiple-objects-in-pickle-file)
        """
        with open(self.save_path, "rb") as f:
            while True:
                try:
                    yield pickle.load(f)
                except EOFError:
                    break

    def save(self):
        """
        Saves all the entered user data.
        """
        with open(self.save_path, 'wb') as f:
            for _, file in self.parent.preloaded_data.items():
                if isinstance(file, FileInfo):
                    if file.requires_save:
                        try:
                            print('dumping {0}'.format(file.file))
                            pickle.dump(file, f)
                        except TypeError:
                            print('error opening file: {0}'.format(file))
