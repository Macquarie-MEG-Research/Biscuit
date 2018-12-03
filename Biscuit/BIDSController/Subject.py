from os import listdir
import os.path as op

import pandas as pd

from Biscuit.BIDSController.BIDSErrors import IDError, MappingError
from Biscuit.BIDSController.Session import Session
from Biscuit.BIDSController.Scan import Scan


class Subject():
    def __init__(self, fpath, project):
        self.path = fpath
        self._id = self._get_id(fpath)
        self.project = project
        # Contained sessions
        self._sessions = dict()

        self.age = 'n/a'
        self.sex = 'n/a'
        self.group = 'n/a'

        self.get_subject_info()

        self.add_sessions()

        self._check()

    def add_sessions(self):
        for file in listdir(self.path):
            full_path = op.join(self.path, file)
            if op.isdir(full_path) and 'ses' in file:
                s = Session(full_path, self)
                self._sessions[s._id] = s

    @property
    def sessions(self):
        return list(self._sessions.values())

    @sessions.setter
    def sessions(self, other):
        self.add(other)

    @property
    def ID(self):
        return self._id

    def get_subject_info(self):
        participant_path = op.join(op.dirname(self.path), 'participants.tsv')
        if not op.exists(participant_path):
            raise MappingError
        participants = pd.read_csv(participant_path, sep='\t')
        for i in range(len(participants)):
            row = participants.iloc[i]
            if row['participant_id'] == 'sub-{0}'.format(self._id):
                self.age = row.get('age', 'n/a')
                self.sex = row.get('sex', 'n/a')
                self.group = row.get('group', 'n/a')
                break
        pass

    def add(self, other, do_copy=True):
        """Add another Session or Scan to this object."""
        if isinstance(other, Session):
            if (self._id == other.subject._id and
                    self.project._id == other.project._id):
                self._sessions[other._id] = other
        elif isinstance(other, Scan):
            if (self._id == other.subject._id and
                    self.project._id == other.project._id and
                    other.session._id in self._sessions):
                self._sessions[other.session._id].add(other, do_copy)

    def _check(self):
        if len(self._sessions) == 0:
            raise MappingError

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

    @staticmethod
    def _get_id(identifier):
        """Get the ID from the file path."""
        name = op.basename(identifier)
        split_name = name.split('-')
        if split_name[0] == 'sub':
            return split_name[1]
        else:
            raise IDError
