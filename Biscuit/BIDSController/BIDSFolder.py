from os import listdir
import os.path

from Biscuit.BIDSController.Project import Project
from Biscuit.BIDSController.Subject import Subject
from Biscuit.BIDSController.Session import Session
from Biscuit.BIDSController.Scan import Scan
from Biscuit.BIDSController.BIDSErrors import MappingError, NoProjectError


class BIDSFolder():
    def __init__(self, fpath):
        self.path = fpath
        self._projects = dict()
        self.determine_content()

#region public methods

    def determine_content(self):
        """ return a list of all the BIDS projects in the specified folder """
        projects = dict()
        try:
            for f in listdir(self.path):
                full_path = os.path.join(self.path, f)
                if os.path.isdir(full_path):
                    projects[f] = Project(f, self)
        except MappingError:
            self._projects = dict()
        self._projects = projects

    def add(self, other):
        """Add another BIDSFolder, Project, Subject, Session or Scan to this.
        The type of data passed in for other will automatically determine how
        it is to be merged.

        Parameters
        ----------
        other : instance of BIDSFolder, Project, Subject, Session or Scan
            Other object to be merged into the current BIDSFolder structure.
        """
        if isinstance(other, BIDSFolder):
            print('bidsfolder')
        if isinstance(other, Project):
            print('proj')
        if isinstance(other, Subject):
            print('sub')
        if isinstance(other, Session):
            print('sess')
        if isinstance(other, Scan):
            print('scan')

    def project(self, id_):
        try:
            return self._projects[id_]
        except KeyError:
            raise NoProjectError("Project {0} doesn't exist in this "
                                 "BIDS folder".format(id_))

#region properties

    @property
    def projects(self):
        return list(self._projects.values())

#region class methods

    def __repr__(self):
        return "BIDS folder containing {0} projects".format(len(self.projects))

    def __iter__(self):
        return iter(self.projects)
