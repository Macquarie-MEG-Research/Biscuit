from mne.io import read_raw_fif
from os.path import join
from mne.io.constants import FIFF

basefolder = 'C:\\Users\\MQ20184158\\Documents\\MEG data\\rs_test_data_for_matt\\3000'
fname = 'rs_asd_rs_aliens_quat_tsss.fif'
f = join(basefolder, fname)

a = read_raw_fif(f)
i = a.info
max_info = i['proc_history'][0]['max_info']

COORDINATE_FRAMES = {FIFF.FIFFV_COORD_UNKNOWN: 'Unknown',
                     FIFF.FIFFV_COORD_DEVICE: 'Device',
                     FIFF.FIFFV_COORD_ISOTRAK: 'Isotrak',
                     FIFF.FIFFV_COORD_HPI: 'HPI',
                     FIFF.FIFFV_COORD_HEAD: 'Head',
                     FIFF.FIFFV_COORD_MRI: 'MRI',
                     FIFF.FIFFV_COORD_MRI_SLICE: 'MRI Slice',
                     FIFF.FIFFV_COORD_MRI_DISPLAY: 'MRI Display',
                     FIFF.FIFFV_COORD_DICOM_DEVICE: 'DICOM Device',
                     FIFF.FIFFV_COORD_IMAGING_DEVICE: 'Imaging Device'}

software_filters = dict()
if max_info.get('max_st'):
    software_filters['TSSS'] = {'Correlation':
                                max_info['max_st']['subspcorr']}
if max_info.get('sss_info'):
    sss_info = {'frame': COORDINATE_FRAMES[max_info['sss_info']['frame']]}
    software_filters['SSS'] = sss_info
print(software_filters)
print('SSS' in software_filters)