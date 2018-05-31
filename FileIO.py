import os.path as path
from os import makedirs

def create_folder(location):
    # simple wrapper to create a folder.
    # If the folder already exists the second return value will be false
    if path.exists(location):
        return location, True
    else:
        makedirs(location)
        return location, False