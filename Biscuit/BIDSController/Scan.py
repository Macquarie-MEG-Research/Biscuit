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
import json

from Biscuit.BIDSController.utils import (get_bids_params, realize_paths,
                                          bids_params_are_subsets, splitall)


class Scan():
    def __init__(self, fpath, acq_time, session):
        self._path = splitall(fpath)[0]
        self._raw_file = '\\'.join(splitall(fpath)[1:])
        self.acq_time = acq_time
        self.session = session
        self._get_params()
        self.sidecar = None
        self.associated_files = dict()
        self._assign_metadata()
        # load information from the sidecar
        self.info = dict()
        self.read_info()
        # finally we do any manufacturer specific loading
        self._load_extras()

#region public methods

    def copy(self, session):
        """Return a new instance of this Scan with the new session."""
        # should be able to drop this and simply do copy.copy(other)
        return Scan(self.raw_file_relative, self.acq_time, session)

    def contained_files(self):
        """Get the list of contained files."""
        file_list = set()
        file_list.add(realize_paths(self, self.sidecar))
        file_list.update(realize_paths(self,
                                       list(self.associated_files.values())))
        return file_list

    def read_info(self):
        """Read the sidecar.json and load the information into self.info"""
        with open(realize_paths(self, self.sidecar), 'r') as sidecar:
            self.info = json.load(sidecar)

#region private methods

    def _get_params(self):
        """Find the scan parameters from the file name."""
        filename_data = get_bids_params(op.basename(self._raw_file))
        self.task = filename_data.get('task', None)
        self.run = filename_data.get('run', None)
        self.acq = filename_data.get('acq', None)

    def _assign_metadata(self):
        """Scan folder for associated metadata files."""
        filename_data = get_bids_params(op.basename(self._raw_file))
        for fname in listdir(self.path):
            bids_params = get_bids_params(fname)
            if bids_params_are_subsets(filename_data, bids_params):
                if (bids_params['file'] == self._path and
                        bids_params['ext'] == '.json'):
                    self.sidecar = fname
                else:
                    if not op.isdir(op.join(self.path, fname)):
                        self.associated_files[bids_params['file']] = fname
        """
        # TODO: check if this is how all sidecar files work? maybe just MEG?
        # May need to modify how this works for other modalities
        if self._path in self.associated_files:
            self.sidecar = self.associated_files.pop(self._path)
        """

    def _load_extras(self):
        """Load any extra files on a manufacturer-by-manufacturer basis."""
        if self.info['Manufacturer'] == 'KIT/Yokogawa':
            # need to load the marker files
            # these will be in the same folder as the raw data
            filename_data = get_bids_params(op.basename(self._raw_file))
            raw_folder = op.dirname(self._raw_file)
            for fname in listdir(op.join(self.path, raw_folder)):
                bids_params = get_bids_params(fname)
                if bids_params_are_subsets(filename_data, bids_params):
                    if bids_params['file'] == 'markers':
                        self.associated_files['markers'] = op.join(raw_folder,
                                                                   fname)

#region properties

    @property
    def subject(self):
        return self.session.subject

    @property
    def project(self):
        return self.session.subject.project

    @property
    def raw_file(self):
        return op.join(self.path, self._raw_file)

    @property
    def raw_file_relative(self):
        return op.join(self._path, self._raw_file)

    @property
    def path(self):
        """Determine path location based on parent paths."""
        return op.join(self.session.path, self._path)

#region class methods

    def __repr__(self):
        return self.path
