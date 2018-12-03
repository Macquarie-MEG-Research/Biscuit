from os import listdir
import os.path as op

import pandas as pd

from Biscuit.BIDSController.BIDSErrors import IDError, MappingError
from Biscuit.BIDSController.Session import Session


class Subject():
    def __init__(self, fpath, project):
        self.path = fpath
        self._id = self._get_id(fpath)
        self.project = project
        # list of contained sessions
        self._sessions = []

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
                self._sessions.append(Session(full_path, self))

    @property
    def sessions(self):
        return self._sessions

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
        return iter(self._sessions)

    @classmethod
    def from_path(cls, fpath):
        pass

    @staticmethod
    def _get_id(identifier):
        """Get the ID from the file path."""
        name = op.basename(identifier)
        split_name = name.split('-')
        if split_name[0] == 'sub':
            return split_name[1]
        else:
            raise IDError
