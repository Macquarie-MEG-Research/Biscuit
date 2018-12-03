import os.path as op
from os import listdir

from Biscuit.BIDSController.Subject import Subject
from Biscuit.BIDSController.BIDSErrors import (NoSubjectError, IDError,
                                               MappingError)


class Project():
    def __init__(self, fpath):
        self._id = op.basename(fpath)
        self.path = fpath
        self._subjects = dict()
        self.subject_ids = []
        self.description = 'None'

        self.add_subjects()

        self._check()

    def add_subjects(self):
        """Add all the subjects with the folder to the Project."""
        for f in listdir(self.path):
            full_path = op.join(self.path, f)
            if op.isdir(full_path) and 'sub-' in f:
                sub_id = f.split('-')[1]
                self._subjects[sub_id] = Subject(full_path, self)

    def subject(self, sid):
        try:
            self._subjects[sid]
        except KeyError:
            raise NoSubjectError("Subject {0} doesn't exist in "
                                 "project {1}".format(sid, self._id))

    def query(self, **kwargs):
        # return any data within the project that matches the kwargs given.
        pass

    @property
    def subjects(self):
        return list(self._subjects.values())

    def _check(self):
        """Check that there aren't no subjects."""
        if len(self._subjects) == 0:
            raise MappingError

    def __repr__(self):
        output = []
        output.append('ProjectID: {0}'.format(self._id))
        output.append('Num subjects: {0}'.format(len(self.subjects)))
        return '\n'.join(output)

    def __contains__(self, other):
        """ other: instance of Subject """
        if isinstance(other, Subject):
            sid = Subject.ID
            if sid in self.subject_ids:
                return True
        else:
            raise ValueError("Can only check whether a subject is contained")

    def __iter__(self):
        return iter(self._subjects.values())

    @staticmethod
    def _get_id(identifier):
        """Get the ID from the file path."""
        name = op.basename(identifier)
        split_name = name.split('-')
        if split_name[0] == 'sub':
            return split_name[1]
        else:
            raise IDError
