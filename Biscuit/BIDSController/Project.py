import os.path as op
from os import listdir
from collections import OrderedDict

import pandas as pd

from Biscuit.BIDSController.Subject import Subject
from Biscuit.BIDSController.Session import Session
from Biscuit.BIDSController.Scan import Scan
from Biscuit.BIDSController.BIDSErrors import NoSubjectError, MappingError
from Biscuit.BIDSController.utils import copyfiles, realize_paths


class Project():
    def __init__(self, id_, bids_folder):
        self.ID = id_
        self.bids_folder = bids_folder
        self.participants_tsv = None
        self._subjects = dict()
        self.description = 'None'

        self.add_subjects()

        self._check()

#region public methods

    def add(self, other, mode='copy', copier=copyfiles):
        """Add another Subject, Session or Scan to this object."""
        # !IMPORTANT! file copying MUST occur before instantiation of the
        # new object
        if isinstance(other, Subject):
            if self.ID == other.project.ID:
                # merge the subject data into the participants.tsv file.
                df = pd.read_csv(self.participants_tsv, sep='\t')
                other_sub_df = pd.DataFrame(
                    OrderedDict([
                        ('participant_id', ['sub-{0}'.format(other.ID)]),
                        ('age', [other.age]),
                        ('sex', [other.sex]),
                        ('group', [other.group])]),
                    columns=['participant_id', 'age', 'sex', 'group'])
                df = df.append(other_sub_df)
                df.to_csv(self.participants_tsv, sep='\t', index=False,
                          na_rep='n/a', encoding='utf-8')
                # add the other subject to the list of subjects.
                if mode == 'copy':
                    subject = other.copy(self)
                else:
                    other.project = self
                    subject = other
                self._subjects[other.subject.ID] = subject
        if isinstance(other, Session):
            if (self.ID == other.project.ID and
                    other.subject.ID in self._subjects):
                self._subjects[other.subject.ID].add(other, mode, copier)
        elif isinstance(other, Scan):
            if (self.ID == other.project.ID and
                    other.subject.ID in self._subjects and
                    other.session.ID in
                    self._subjects[other.subject.ID]._sessions):
                self._subjects[other.subject.ID]._sessions.add(other, mode,
                                                               copier)

    def add_subjects(self):
        """Add all the subjects in the folder to the Project."""
        for fname in listdir(self.path):
            full_path = op.join(self.path, fname)
            # TODO: use utils.get_bids_params?
            if op.isdir(full_path) and 'sub-' in fname:
                sub_id = fname.split('-')[1]
                self._subjects[sub_id] = Subject(sub_id, self)
            elif fname == 'participants.tsv':
                self.participants_tsv = fname

    def subject(self, id_):
        try:
            return self._subjects[str(id_)]
        except KeyError:
            raise NoSubjectError(
                "Subject {0} doesn't exist in project {1}. "
                "Possible subjects: {2}".format(id_, self.ID,
                                                list(self._subjects.keys())))

    def query(self, **kwargs):
        # return any data within the project that matches the kwargs given.
        pass

    def contained_files(self):
        """Get the list of contained files."""
        file_list = set()
        # TODO: add readme and dataset_description.json
        file_list.add(realize_paths(self, self.participants_tsv))
        for subject in self.subjects:
            file_list.update(subject.contained_files())
        return file_list

#region private methods

    def _check(self):
        """Check that there aren't no subjects."""
        if len(self._subjects) == 0:
            raise MappingError

#region properties

    @property
    def subjects(self):
        return list(self._subjects.values())

    @subjects.setter
    def subjects(self, other):
        self.add(other)

    @property
    def path(self):
        """Determine path location based on parent paths."""
        return op.join(self.bids_folder.path, self.ID)

#region class methods

    def __repr__(self):
        output = []
        output.append('Project ID: {0}'.format(self.ID))
        output.append('Number of subjects: {0}'.format(len(self.subjects)))
        return '\n'.join(output)

    def __contains__(self, other):
        """ other: instance of Subject """
        if isinstance(other, Subject):
            sid = other.ID
            if sid in self._subjects.keys():
                return True
        else:
            raise ValueError("Can only check whether a subject is contained")

    def __iter__(self):
        return iter(self._subjects.values())
