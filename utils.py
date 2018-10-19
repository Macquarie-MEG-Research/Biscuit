from functools import wraps
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


def get_object_class(dtype):
    from FileTypes import (con_file, mrk_file, elp_file, hsp_file,
                           tsv_file, json_file, generic_file, FIFData)
    map_ = {'.con': con_file,    # continuous data
            '.mrk': mrk_file,    # marker
            '.elp': elp_file,    # electrode placement
            '.hsp': hsp_file,    # headspace
            '.tsv': tsv_file,    # tab-separated file
            '.json': json_file,
            '.fif': FIFData}    # Elekta data
    # if not in the list, just return the data type
    if dtype != '':
        return map_.get(dtype, generic_file)
    else:
        # TODO: maybe scan the folder to see if it contains any .con files
        # if so, then assign as a KITData object, otherwise just a folder?
        return 'folder'     # maybe??


def flatten(lst):
    """ Flattens a 2D array to a 2D list """
    out = []
    for sub in lst:
        if isinstance(sub, list):
            out += sub
        else:
            out = lst
            break
    return out


def threaded(func):
    """
    Simple function to be used as a decorator to allow the
    decorated function to be threaded automatically
    """
    from threading import Thread

    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def clear_widget(widget):
    """
    Will set the weights of all columns of widget to 0
    and remove all children
    """
    rows, columns = widget.grid_size()
    # we want to refresh all the grid configurations:
    for row in range(rows):
        widget.grid_rowconfigure(row, weight=0)      # default weight = 0
    for column in range(columns):
        widget.grid_columnconfigure(column, weight=0)

    for child in widget.grid_slaves():
        child.grid_forget()


def generate_readme(data):
    """
    Takes in a dictionary containing all the relevant information on the
    project and produces a string that can be passed to mne-bids
    * might actually change this to produce a .md file to have nicer formatting
    """
    out_str = ""
    out_str += "Project Title:\t\t{0}\n".format(
        data.get('ProjectTitle', 'None'))
    out_str += "Project ID:\t\t{0}\n\n".format(data.get('ProjectID', 'None'))
    out_str += "Expected experimentation period:\n"
    s_date = data.get('StartDate', None)
    if s_date is not None:
        start_date = '/'.join(s_date)
    else:
        start_date = 'Unknown'
    out_str += "Start date:\t\t{0}\n".format(start_date)
    e_date = data.get('EndDate', None)
    if e_date is not None:
        end_date = '/'.join(e_date)
    else:
        end_date = 'Unknown'
    out_str += "End date:\t\t{0}\n\n".format(end_date)
    out_str += "Project Description:\n"
    out_str += data.get("Description", "None")
    return out_str


if __name__ == "__main__":
    a = [1, 2, 3]
    print(a)
    a = flatten(a)
    print(a)
    b = [[1, 2], [6, 7]]
    print(b)
    b = flatten(b)
    print(b)
