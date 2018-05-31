from struct import unpack

from .FileInfo import FileInfo

class mrk_file(FileInfo):
    """
    .mrk specific file container.
    """
    def __init__(self, id_, file, *args, **kwargs):
        super(mrk_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.mrk'

    def read_info(self):
        pass