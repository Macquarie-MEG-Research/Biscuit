from os.path import splitext


def get_bids_params(fname):
    filename, ext = splitext(fname)
    f = filename.split('_')
    data = {'ext': ext}
    for i in f:
        if '-' in i:
            data[i.split('-')[0]] = i.split('-')[1]
        else:
            data['file'] = i
    return data


def bids_params_are_subsets(params1, params2):
    """Equivalent to asking if params1 >= params2."""
    param1_keys = set(params1.keys())
    param2_keys = set(params2.keys())
    for key in ['file', 'ext']:
        param1_keys = param1_keys - {key}
        param2_keys = param2_keys - {key}
    if param1_keys >= param2_keys:
        for key in param2_keys:
            if not params2[key] == params1[key]:
                return False
        return True
    return False


if __name__ == "__main__":
    print(get_bids_params('sub-1111_ses-aab_scans'))
