from .FileInfo import FileInfo


class hsp_file(FileInfo):
    """
    .hsp specific file container.
    """
    def __init__(self, id_=None, file=None, *args, **kwargs):
        super(hsp_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.hsp'
        self.display_raw = True
        self.requires_save = False
