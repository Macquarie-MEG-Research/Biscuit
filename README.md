# Biscuit

## Description
Biscuit is a simple graphical application that facilitates the reformatting of raw KIT MEG data to comply with the international [BIDS specification](https://docs.google.com/document/d/1HFUkAEE-pB-angVcYe6pf_-fVf4sCpOHKesUvfb8Grc)

## Installation
Biscuit is written in Python and requires a number of pre-requisite libraries to operate.
### Installing pre-requisites:
#### Already have Python installed:
If you already have Python (>3.4 preferrably), install [MNE-Python](https://pypi.org/project/mne/) and ensure any required dependencies have been installed. Further, ensure [Pandas](https://pypi.org/project/pandas/) is installed (can be done easily with `pip install pandas`).
#### Don't have Python installed:
If you do not have a current Python install on your system, it is recommended that you install the [Anaconda](https://anaconda.org/anaconda/python) Python distribution. You can also follow the steps to [install MNE-Python](https://www.martinos.org/mne/stable/getting_started.html).
### Installing Biscuit:
Next Biscuit can be installed by cloning the github repo to your local drive.
This can be done from a browser by selecting the green `clone or download` button near the top right of the page, or by entering `git clone https://github.com/Macquarie-MEG-Research/Biscuit.git` into your favorite command line program. The second method requires [Git](https://git-scm.com/downloads) to be installed. You can check if your system has Git installed by entering `git --version` into your command prompt. If the version appears without error then it is installed.

## Usage
Biscuit can be run by running the `GUI.py` file with Python.
A window will pop up which allows you to enter all the required information to convert your data to be BIDS compatible

## Notes:
[MNE-Bids](https://github.com/mne-tools/mne-bids) is included in the project as a modified version is used to add extra functionality. It is hoped that in the future all the extra features will be integrated officially into the library and it can be included as a requirement instead of included in the source.
