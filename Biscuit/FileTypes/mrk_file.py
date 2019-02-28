from os.path import basename

from .FileInfo import FileInfo
from Biscuit.utils.utils import get_mrk_meas_date


class mrk_file(FileInfo):
    """
    .mrk specific file container.
    """
    def __init__(self, id_=None, file=None, parent=None):
        super(mrk_file, self).__init__(id_, file, parent)
        self._type = '.mrk'

#region class methods

    def __getstate__(self):
        data = super(mrk_file, self).__getstate__()

        return data

    def __setstate__(self, state):
        super(mrk_file, self).__setstate__(state)

    def __repr__(self):
        # Have a separate representation for .mrk files as this is shown in the
        # info for each con file under the list of associated mrk's.
        return str(basename(self.file))
