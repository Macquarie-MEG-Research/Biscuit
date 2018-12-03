from os import listdir
import os.path

from Biscuit.BIDSController.Project import Project
from Biscuit.BIDSController.BIDSErrors import MappingError


def find_projects(fpath):
    """ return a list of all the BIDS projects in the specified folder """
    proj_list = []
    try:
        for f in listdir(fpath):
            full_path = os.path.join(fpath, f)
            if os.path.isdir(full_path):
                proj_list.append(Project(full_path))
    except MappingError:
        return []
    return proj_list
