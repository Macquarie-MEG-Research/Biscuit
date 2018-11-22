from .FileInfo import FileInfo


class json_file(FileInfo):
    """
    .json specific file container.
    """
    def __init__(self, id_=None, file=None, *args, **kwargs):
        super(json_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.json'
        self.display_raw = True
        self.requires_save = False
