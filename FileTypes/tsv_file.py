from .FileInfo import FileInfo


class tsv_file(FileInfo):
    """
    .tsv specific file container.
    """
    def __init__(self, id_=None, file=None, *args, **kwargs):
        super(tsv_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.tsv'
        self.display_raw = True
        self.requires_save = False
