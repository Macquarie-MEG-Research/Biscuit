from .FileInfo import FileInfo


class elp_file(FileInfo):
    """
    .elp specific file container.
    """
    def __init__(self, id_=None, file=None, *args, **kwargs):
        super(elp_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.elp'
        self.display_raw = True
        self.requires_save = False
