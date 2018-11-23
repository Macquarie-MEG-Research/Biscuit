# Biscuit

![biscuit](Biscuit/assets/bisc.png)

## Convert your MEG data to a BIDS compliant format
Biscuit is a simple graphical application that facilitates the reformatting of raw KIT and Elekta MEG data to comply with the international [BIDS Standard](http://bids.neuroimaging.io/).
Current discussion on the BIDS specification can be found [here](https://github.com/bids-standard/bids-specification).

Biscuit requires at least Python 3.4, but it is recommended to have [Python 3.6](https://www.python.org/downloads/release/python-367/) or [Python 3.7](https://www.python.org/downloads/release/python-371/)

For full installation and usage instructions visit the [Biscuit GitHub page](https://macquarie-meg-research.github.io/Biscuit/)

Biscuit uses [MNE-Python](https://github.com/mne-tools/mne-python) and [MNE-BIDS](https://github.com/mne-tools/mne-bids) to load the MEG data and convert to BIDS format.

Note:
Because the BIDS specification is still being developed the output is likely to change over the next few months, so the data generated currently may not be BIDS compliant in the future. This is an unavoidable side-effect of this being developed while the BIDS specifcation is still in active development.
