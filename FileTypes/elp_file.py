from struct import unpack

from .FileInfo import FileInfo

class elp_file(FileInfo):
    """
    .elp specific file container.
    """
    def __init__(self, id_, file, *args, **kwargs):
        super(elp_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.elp'
        self.display_raw = True

    def read_info(self):
        pass