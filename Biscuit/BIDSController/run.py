from Biscuit.BIDSController.Project import Project
from os import listdir
import os.path

root = "C:\\Users\\MQ20184158\\Documents\\MEG data\\rs_test_data_for_matt\\BIDS\\BIDS-2018-20"  # noqa


def find_projects(fpath):
    """ return a list of all the BIDS projects in the specified folder """
    proj_list = []
    for f in listdir(fpath):
        full_path = os.path.join(fpath, f)
        if os.path.isdir(full_path):
            proj_list.append(Project(full_path))
    return proj_list


a = find_projects(root)
p = a[0]
print(p)
for subject in p:
    print(subject)
    for session in subject:
        print(session)
        for scan in session:
            print(scan)
            print(scan.associated_files)
#print(a)
