from struct import unpack
from os.path import join

import mne

bpath = "C:\\Users\\MQ20184158\\Documents\\MEG data\\rs_test_data_for_matt\\2897"

fname = join(bpath, '2897_TM_ME125_2018_02_02_B1.con')
outfile = join(bpath, "reTHM_data.txt")
outfile_time = join(bpath, "reTHM_event_data.txt")
mrk = join(bpath, "2897_TM_ME125_2018_02_02_ini.mrk")
elp = join(bpath, "2897_TM_ME125_2018_02_02.elp")
hsp = join(bpath, "2897_TM_ME125_2018_02_02.hsp")

initial_pulses = 2      # can this be read from the .con file??

raw = mne.io.read_raw_kit(fname,
                          mrk=mrk,
                          elp=elp,
                          hsp=hsp,
                          stim=['191'],
                          slope='-',
                          stim_code='channel',
                          stimthresh=0.5)
events = mne.find_events(raw, stim_channel='STI 014', min_duration=0.050)
onsets = events[initial_pulses:, 0]

sfreq = raw.info['sfreq']
print(sfreq, 'sfreq')
corrected_offsets = [i / sfreq for i in onsets]

ignore_bads = False

"""
with open(fname, 'rb') as file:
    with open(outfile, 'w') as out:
        file.seek(0x1D0)
        offset, size, count = unpack('3i', file.read(0xC))
        elements = 5            # maybe read this from the marker data??
        count = int(count / elements)   # total count
        file.seek(offset)
        # we are now at the start of the reTHM data...
        total = min(count, len(corrected_offsets))      # there will be less events, but just to make sure...
        for i in range(total):
            out.writelines(str(corrected_offsets[i]))
            for j in range(elements):
                ch_is_good, = unpack('i', file.read(4))
                if ch_is_good == 1 or ignore_bads:
                    x, y, z, gof = unpack('4d', file.read(0x20))
                    out.writelines(['\t{0:.2f}\t{1:.2f}\t{2:.2f}\t{3:.4f}'.format(1000 * x, 1000 * y, 1000 * z, gof)])
                else:
                    out.writelines(['\t', 'nan', '\t', 'nan', '\t', 'nan', '\t', 'nan'])
                    file.seek(0x20, 1)      # need to skip over the data
            out.writelines(['\n'])
"""
for ch in raw.info['chs']:
    print(ch['kind'], ch['coil_type'])


def reTHM(file):
    # general reTHM data:
    file.seek(0x1B0)
    unknown0 = unpack('i', file.read(4))
    unknown1 = unpack('i', file.read(4))
    num_reTHM_channels = unpack('i', file.read(4))
    reTHM_channels = []
    # next is a list of the channels numbers that are reTHM channels
    for _ in range(num_reTHM_channels):
        reTHM_channels.append(unpack('i', file.read(4)))
    # and the rest... I don't know...

    # FFT data:
    file.seek(0x1C0)
    # pointer to data, size of each individual data block, number of total values, (same again)
    fft_offset, fft_size, fft_count, _ = unpack('4i', file.read(0x10))
    #fft_count = num_channels * num_markers * 8 * 16
    # each block of size 0xC (in our data) consists of a 4 byte int, and an 8 byte double

    # continuous head movement data
    file.seek(0x1D0)
    hm_offset, hm_size, hm_count, _ = unpack('4i', file.read(0x10))
    # hm_count = num_channels * num_markers
