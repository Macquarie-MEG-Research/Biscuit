from FileTypes import *

def get_object_class(dtype):
    map_ = {'.con':con_file,    # continuous data
            '.mrk':mrk_file,    # marker
            '.elp':elp_file,    # electrode placement
            '.hsp':hsp_file,    # headspace
            '.tsv':tsv_file,    # tab-separated file. Giving this it's own class in case we want to do something else with it like display it nicer?
            '.json':json_file}  
    # if not in the list, just return the data type
    if dtype != '':
        return map_.get(dtype, generic_file)
    else:
        return 'folder'     # maybe??