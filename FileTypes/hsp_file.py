from struct import unpack

from .FileInfo import FileInfo

class hsp_file(FileInfo):
    """
    .hsp specific file container.
    """
    def __init__(self, id_, file, *args, **kwargs):
        super(hsp_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.hsp'
        self.display_raw = True

    def read_info(self):
        pass