from functools import wraps
from tkinter import IntVar, BooleanVar, DoubleVar, StringVar
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
                           tsv_file, json_file, generic_file)
    map_ = {'.con': con_file,    # continuous data
            '.mrk': mrk_file,    # marker
            '.elp': elp_file,    # electrode placement
            '.hsp': hsp_file,    # headspace
            '.tsv': tsv_file,    # tab-separated file
            '.json': json_file}
    # if not in the list, just return the data type
    if dtype != '':
        return map_.get(dtype, generic_file)
    else:
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
    out_str += "Start date:\t\t{0}/{1}/{2}\n".format(
        *data.get('StartDate', ['01', '01', '1970']))
    out_str += "End date:\t\t{0}/{1}/{2}\n\n".format(
        *data.get('EndDate', ['31', '12', '2020']))
    out_str += "Project Description:\n"
    out_str += data.get("Description", "None")
    return out_str


def pickle_var(var):
    """
    Takes in a Variable type object var and returns a tuple with the type as a
    string and value
    """
    if isinstance(var, IntVar):
        return ('int', var.get())
    elif isinstance(var, StringVar):
        return ('string', var.get())
    elif isinstance(var, BooleanVar):
        return ('bool', var.get())
    elif isinstance(var, DoubleVar):
        return ('double', var.get())
    else:
        raise TypeError


def unpickle_var(data):
    """
    Takes in a tuple of the form (type (str), value) and returns an actual
    Variable subclass object
    """
    if data[0] == 'int':
        _temp = IntVar()
    elif data[0] == 'string':
        _temp = StringVar()
    elif data[0] == 'bool':
        _temp = BooleanVar()
    elif data[0] == 'double':
        _temp = DoubleVar()
    else:
        print(data)
        raise ValueError(data[0])
    _temp.set(data[1])
    return _temp

if __name__ == "__main__":
    a = [1, 2, 3]
    print(a)
    a = flatten(a)
    print(a)
    b = [[1,2], [6,7]]
    print(b)
    b = flatten(b)
    print(b)