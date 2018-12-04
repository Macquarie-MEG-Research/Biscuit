from os import listdir
import os.path as op

import pandas as pd

from Biscuit.BIDSController.BIDSErrors import MappingError
from Biscuit.BIDSController.Session import Session
from Biscuit.BIDSController.Scan import Scan
from Biscuit.BIDSController.utils import copyfiles


class Subject():
    def __init__(self, id_, project):
        self.ID = id_
        self.project = project
        # Contained sessions
        self._sessions = dict()

        self.age = 'n/a'
        self.sex = 'n/a'
        self.group = 'n/a'

        self.get_subject_info()

        self.add_sessions()
        self._check()

#region public methods

    def add_sessions(self):
        for fname in listdir(self.path):
            full_path = op.join(self.path, fname)
            if op.isdir(full_path) and 'ses' in fname:
                ses_id = fname.split('-')[1]
                self._sessions[ses_id] = Session(ses_id, self)

    def get_subject_info(self):
        participant_path = op.join(op.dirname(self.path), 'participants.tsv')
        if not op.exists(participant_path):
            raise MappingError
        participants = pd.read_csv(participant_path, sep='\t')
        for i in range(len(participants)):
            row = participants.iloc[i]
            if row['participant_id'] == 'sub-{0}'.format(self.ID):
                self.age = row.get('age', 'n/a')
                self.sex = row.get('sex', 'n/a')
                self.group = row.get('group', 'n/a')
                break
        pass

    def add(self, other, mode='copy', copier=copyfiles):
        """Add another Session or Scan to this object.

        Parameters
        ----------
        other : Instance of Session or Scan
            Scan or Session object to be added to this Subject.
            The object must previously exist in the same project and subject
            as this current subject.
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
        if isinstance(other, Session):
            if (self.ID == other.subject.ID and
                    self.project.ID == other.project.ID):
                if mode == 'copy':
                    session = other.copy(self)
                else:
                    other.subject = self
                    session = other
                self._sessions[other.ID] = session
                # first, copy the scans.tsv file
        elif isinstance(other, Scan):
            if (self.ID == other.subject.ID and
                    self.project.ID == other.project.ID and
                    other.session.ID in self._sessions):
                self._sessions[other.session.ID].add(other, mode, copier)
        else:
            raise TypeError("Cannot add a {0} object to a Subject".format(
                other.__name__))

    def copy(self, project):
        """Return a new instance of this Subject with the new project."""
        return Subject(self.ID, project)

#region private methods

    def _check(self):
        if len(self._sessions) == 0:
            raise MappingError

#region properties

    @property
    def sessions(self):
        return list(self._sessions.values())

    @sessions.setter
    def sessions(self, other):
        self.add(other)

    @property
    def bids_folder(self):
        return self.project.bids_folder

    @property
    def path(self):
        """Determine path location based on parent paths."""
        return op.join(self.project.path, 'sub-{0}'.format(self.ID))

#region class methods

    def __repr__(self):
        output = []
        output.append('sub-{0}'.format(self.ID))
        output.append('Info:')
        output.append('Age: {0}'.format(self.age))
        output.append('Gender: {0}'.format(self.sex))
        output.append('Group: {0}'.format(self.group))
        return '\n'.join(output)

    def __iter__(self):
        return iter(self._sessions.values())
