from FileTypes.FileInfo import FileInfo


class Folder(FileInfo):
    def __init__(self, id_=None, file=None, parent=None):
        super(Folder, self).__init__(id_, file, parent)
        self.is_valid = False
        self.contains_required_files = False

    def initial_processing(self):
        # go over the children and call the validate command?
        for sid in self.parent.file_treeview.get_children(self._id):
            file = self.parent.preloaded_data.get(sid, None)
            if file is not None:
                file.validate()

    def load_data(self):
        # we want nothing to be loaded
        pass
