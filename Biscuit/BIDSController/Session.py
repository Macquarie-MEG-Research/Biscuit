from os import listdir
import os.path as op

import pandas as pd

from Biscuit.BIDSController.utils import get_bids_params
from Biscuit.BIDSController.BIDSErrors import IDError, MappingError
from Biscuit.BIDSController.Scan import Scan


class Session():
    def __init__(self, fpath, subject):
        self.path = fpath
        self._id = self._get_id(fpath)
        self.subject = subject
        self._scans = []
        self.recording_types = []
        self.determine_content()

        self._check()

    @property
    def scans(self):
        return self._scans

    def _load_scans(self):
        pass

    def determine_content(self):
        """Parse the session folder to find what recordings are included."""
        for f in listdir(self.path):
            full_path = op.join(self.path, f)
            if op.isdir(full_path):
                self.recording_types.append(f)
            else:
                filename_data = get_bids_params(f)
                if filename_data.get('file', None) == 'scans':
                    scans = pd.read_csv(full_path, sep='\t')
                    for i in range(len(scans)):
                        row = scans.iloc[i]
                        self._scans.append(
                            Scan(op.join(self.path, row['filename']),
                                 row['acq_time'],
                                 self))

    def _check(self):
        if len(self._scans) == 0:
            raise MappingError

    def __repr__(self):
        output = []
        output.append('ses-{0}'.format(self._id))
        output.append('Number of scans: {0}'.format(len(self.scans)))
        return '\n'.join(output)

    def __iter__(self):
        return iter(self._scans)

    @staticmethod
    def _get_id(identifier):
        """Get the ID from the file path."""
        name = op.basename(identifier)
        split_name = name.split('-')
        if split_name[0] == 'ses':
            return split_name[1]
        else:
            raise IDError
