from .FileInfo import FileInfo
from os.path import normpath


class mrk_file(FileInfo):
    """
    .mrk specific file container.
    """
    def __init__(self, id_=None, file=None, *args, **kwargs):
        super(mrk_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.mrk'

    def __repr__(self):
        # Have a separate representation for .mrk files as this is shown in the
        # info for each con file under the list of associated mrk's.
        return str(normpath(self._file))
