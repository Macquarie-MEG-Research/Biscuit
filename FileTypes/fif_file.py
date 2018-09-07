from .FileInfo import FileInfo


class fif_file(FileInfo):
    """
    .fif specific file container.
    """
    def __init__(self, id_=None, file=None, *args, **kwargs):
        super(fif_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.fif'
        self.display_raw = False
        self.requires_save = False
