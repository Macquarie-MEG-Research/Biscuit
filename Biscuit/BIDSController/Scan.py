"""
Data each scan object needs:
 - Raw file path(s) - how to handle marker?
 - channels.tsv path
 - events.tsv path
 - sidecar.json path
 - coordsystem.json path
 - modality (MEG, EEG etc.)
 - manufacturer
+ lots of info that can be extracted from the sidecar file.

"""

import os.path as op
from os import listdir

from Biscuit.BIDSController.utils import (get_bids_params,
                                          bids_params_are_subsets)


class Scan():
    def __init__(self, fpath, acq_time, session):
        self.raw_file = fpath
        self.acq_time = acq_time
        self.session = session
        self._get_params()
        self.path = self._get_folder()
        self.sidecar = None
        self.associated_files = dict()
        self._assign_metadata()

    def _get_params(self):
        """Find the scan parameters from the file name."""
        filename_data = get_bids_params(op.basename(self.raw_file))
        self.task = filename_data.get('task', None)
        self.run = filename_data.get('run', None)
        self.acq = filename_data.get('acq', None)
        self.type = filename_data.get('file', None)

    def _get_folder(self):
        """Determine the path to the folder containing metadata files."""
        rel_path = op.dirname(op.relpath(self.raw_file, self.session.path))
        # This relative path may be an extra folder down (eg for KIT data)
        # Check whether this is the case
        split_path = op.split(rel_path)
        if split_path[0] == '':
            return op.join(self.session.path, split_path[1])
        else:
            return op.join(self.session.path, split_path[0])

    def _assign_metadata(self):
        """Scan folder for associated metadata files."""
        filename_data = get_bids_params(op.basename(self.raw_file))
        for f in listdir(self.path):
            bids_params = get_bids_params(f)
            if bids_params_are_subsets(filename_data, bids_params):
                self.associated_files[bids_params['file']] = op.join(self.path,
                                                                     f)
        if self.type in self.associated_files:
            self.sidecar = self.associated_files.pop(self.type)

    @property
    def subject(self):
        return self.session.subject

    @property
    def project(self):
        return self.session.subject.project

    def __repr__(self):
        return self.path
