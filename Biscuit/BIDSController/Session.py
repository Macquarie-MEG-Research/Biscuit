from os import listdir
import os.path as op

import pandas as pd

from Biscuit.BIDSController.utils import get_bids_params, merge_tsv, copyfiles
from Biscuit.BIDSController.BIDSErrors import MappingError
from Biscuit.BIDSController.Scan import Scan


class Session():
    def __init__(self, id_, subject):
        self.ID = id_
        self.subject = subject
        self.scans_tsv = None
        self._scans = []
        self.recording_types = []
        self.determine_content()

        self._check()

#region public methods

    # TODO: Rename?
    def determine_content(self):
        """Parse the session folder to find what recordings are included."""
        for fname in listdir(self.path):
            full_path = op.join(self.path, fname)
            # Each sub-directory is considered a separate type of recording.
            if op.isdir(full_path):
                self.recording_types.append(fname)
            # The only other non-folder should be the scans tsv.
            else:
                filename_data = get_bids_params(fname)
                if filename_data.get('file', None) == 'scans':
                    # Store the path and extract the paths of the scans.
                    self.scans_path = full_path
                    scans = pd.read_csv(self.scans_path, sep='\t')
                    for i in range(len(scans)):
                        row = scans.iloc[i]
                        self._scans.append(
                            Scan(op.join(self.path, row['filename']),
                                 row['acq_time'],
                                 self))

    def add(self, other, mode='copy', copier=copyfiles):
        """Add another Scan to this object.

        Parameters
        ----------
        other : Instance of Scan
            Scan object to be added to this session.
            The scan must previously exist in the same project, subject and
            session as this current session.
        mode : str | One of ('copy', 'move')
            TODO: maybe change to 'remove_after_copy' : bool
            Whether to copy or move the files
        copier : function
            A function to facilitate the copying of any applicable data.
            This function must have the call signature
            `function(src_files: list, dst: string)`
            Where src_files is the list of files to be moved and dst is the
            destination folder.
            This will default to using utils.copyfiles which simply implements
            shutil.copy.
        """
        # !IMPORTANT! file copying MUST occur before instantiation of the
        # new object
        if isinstance(other, Scan):
            # TODO-LT: handle other modalities
            # we need to make sure that the scan is of the same person/session:
            if (self.ID == other.session.ID and
                    self.subject.ID == other.subject.ID and
                    self.project.ID == other.project.ID):
                # add the scan object to our scans list
                if mode == 'copy':
                    scan = other.copy(self)
                else:
                    other.session = self
                    scan = other
                self._scans.append(scan)
                # also need to add the scan to the scans.tsv file
                merge_tsv(self.scans_tsv, other.scans_file)
                # TODO: move files
                copier(list(scan.associated_files.values()) +
                       [scan.sidecar],
                       op.join(self.path, scan.type))
            else:
                # TODO: raise custom error?
                raise ValueError("Scan doesn't exist within this branch")
        else:
            raise TypeError("Cannot add a {0} object to a Scan".format(
                other.__name__))

    def copy(self, subject):
        """Return a new instance of this Session with the new subject."""
        return Session(self.ID, subject)


#region private methods

    def _check(self):
        if len(self._scans) == 0:
            raise MappingError

#region properties

    @property
    def project(self):
        return self.subject.project

    @property
    def bids_folder(self):
        return self.project.bids_folder

    @property
    def path(self):
        """Determine path location based on parent paths."""
        return op.join(self.subject.path, 'ses-{0}'.format(self.ID))

    @property
    def scans(self):
        return self._scans

    @scans.setter
    def scans(self, other):
        self.add(other)

#region class methods

    def __repr__(self):
        output = []
        output.append('ses-{0}'.format(self.ID))
        output.append('Number of scans: {0}'.format(len(self.scans)))
        return '\n'.join(output)

    def __iter__(self):
        return iter(self._scans)
