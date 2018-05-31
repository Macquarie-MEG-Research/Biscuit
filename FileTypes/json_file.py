from struct import unpack

from .FileInfo import FileInfo

class json_file(FileInfo):
    """
    .json specific file container.
    """
    def __init__(self, id_, file, *args, **kwargs):
        super(json_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.json'
        self.display_raw = True

    def read_info(self):
        pass