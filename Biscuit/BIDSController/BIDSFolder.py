from os import listdir
import os.path

from Biscuit.BIDSController.Project import Project
from Biscuit.BIDSController.Subject import Subject
from Biscuit.BIDSController.Session import Session
from Biscuit.BIDSController.Scan import Scan
from Biscuit.BIDSController.BIDSErrors import MappingError


class BIDSFolder():
    def __init__(self, fpath):
        self.path = fpath
        self._projects = []
        self.determine_content()

#region public methods

    def determine_content(self):
        """ return a list of all the BIDS projects in the specified folder """
        proj_list = []
        try:
            for f in listdir(self.path):
                full_path = os.path.join(self.path, f)
                if os.path.isdir(full_path):
                    proj_list.append(Project(f, self))
        except MappingError:
            self._projects = []
        self._projects = proj_list

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

#region properties

    @property
    def projects(self):
        return self._projects

#region class methods

    def __repr__(self):
        return "BIDS folder containing {0} projects".format(len(self.projects))

    def __iter__(self):
        return iter(self.projects)
