from .FileInfo import FileInfo


class elp_file(FileInfo):
    """
    .elp specific file container.
    """
    def __init__(self, id_=None, file=None, parent=None):
        super(elp_file, self).__init__(id_, file, parent=None)
        self._type = '.elp'
        self.display_raw = True
        self.requires_save = False
