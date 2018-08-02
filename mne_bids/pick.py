# Authors: Matt Sanderson <matt.sanderson@mq.edu.au>
#
# License: BSD (3-clause)

from mne.io.constants import FIFF


def get_coil_types():
    """Return all known coul types.

    Returns
    -------
    coil_types : dict
        The keys contain the channel types, and the values contain the
        corresponding values in the info['chs'][idx]['kind']
    """

    return dict(meggradaxial=(FIFF.FIFFV_COIL_KIT_GRAD,
                              FIFF.FIFFV_COIL_CTF_GRAD,
                              FIFF.FIFFV_COIL_AXIAL_GRAD_5CM,
                              FIFF.FIFFV_COIL_BABY_GRAD),
                megrefgradaxial=(FIFF.FIFFV_COIL_CTF_REF_GRAD,
                                 FIFF.FIFFV_COIL_CTF_OFFDIAG_REF_GRAD),
                meggradplanar=(FIFF.FIFFV_COIL_VV_PLANAR_T1,
                               FIFF.FIFFV_COIL_VV_PLANAR_T2,
                               FIFF.FIFFV_COIL_VV_PLANAR_T3),
                megmag=(FIFF.FIFFV_COIL_POINT_MAGNETOMETER,
                        FIFF.FIFFV_COIL_POINT_MAGNETOMETER_X,
                        FIFF.FIFFV_COIL_POINT_MAGNETOMETER_Y,
                        FIFF.FIFFV_COIL_VV_MAG_W,
                        FIFF.FIFFV_COIL_VV_MAG_T1,
                        FIFF.FIFFV_COIL_VV_MAG_T2,
                        FIFF.FIFFV_COIL_VV_MAG_T3,
                        FIFF.FIFFV_COIL_MAGNES_MAG,
                        FIFF.FIFFV_COIL_BABY_MAG),
                megrefmag=(FIFF.FIFFV_COIL_KIT_REF_MAG,
                           FIFF.FIFFV_COIL_CTF_REF_MAG,
                           FIFF.FIFFV_COIL_MAGNES_REF_MAG,
                           FIFF.FIFFV_COIL_BABY_REF_MAG,
                           FIFF.FIFFV_COIL_BABY_REF_MAG2,
                           FIFF.FIFFV_COIL_ARTEMIS123_REF_MAG),
                eeg=(FIFF.FIFFV_COIL_EEG,),
                misc=(FIFF.FIFFV_COIL_NONE,))


def coil_type(info, idx):
    """Get coil type.

    Parameters
    ----------
    info : dict
        Measurement info
    idx : int
        Index of channel

    Returns
    -------
    type : 'meggradaxial' | 'megrefgradaxial' | 'meggradplanar'
           'megmag' | 'megrefmag' | 'eeg' | 'misc'
        Type of coil
    """
    ch = info['chs'][idx]
    for key, values in get_coil_types().items():
        if ch['coil_type'] in values:
            return key
    raise ValueError('Unknown coil of type {0} '
                     'for channel {1}'.format(ch['coil_type'], ch["ch_name"]))
