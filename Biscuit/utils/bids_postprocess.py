# post-process some of the BIDS files produced to add any extra data we want

import pandas as pd
import json


def update_sidecar(fname):
    # add dewar angle
    # modify the continuous head localisation value
    # add software filters
    # add empty room info
    # add serial number?
    sidecar = json.load(fname)
    print(sidecar)


def update_participants(fname):
    # add/modify the groups property
    df = pd.read_csv(fname, sep='\t')
    print(df)
