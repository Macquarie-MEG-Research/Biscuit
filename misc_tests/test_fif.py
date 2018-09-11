from mne.io import read_raw_fif
from os.path import join
from datetime import datetime

basefolder = 'C:\\Users\\MQ20184158\\Documents\\MEG data\\rs_test_data_for_matt\\3000'
fname = 'rs_asd_rs_aliens_quat_tsss.fif'
f = join(basefolder, fname)

a = read_raw_fif(f)
x = [str(i) for i in a.info['subject_info']['birthday']]
x.reverse()
print(','.join(x))
