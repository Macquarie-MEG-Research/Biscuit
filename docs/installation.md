# Installating prerequisites

Biscuit is completely written in python, allowing it to be run on any computer you can install python on.
To allow for the reading of MEG data and conversion a few libraries are required to be installed. There are a few options available depending on the current python install on your system.

## > Already have Python installed
Biscuit is written for python 3.4 and above, however it is recommended that you use at least the latest version of 3.6 which can be found [here](https://www.python.org/downloads/release/python-367/). If you already have python installed you can easily install Biscuit from a precompiled wheel.
This can be downloaded from the [releases tab](https://github.com/Macquarie-MEG-Research/Biscuit/releases) on github.
There are two ways to download and install using this. You can either just copy the link and enter
```
python3 -m pip install https://github.com/Macquarie-MEG-Research/Biscuit/releases/download/v0.9.3/Biscuit-0.9.3-py3-none-any.whl
```
(where the version may vary depending on the current release version),

or you can download the wheel (`.whl`) file to your local disk and enter
```
python3 -m pip install Biscuit-0.9.3-py3-none-any.whl
```
into your command line within the directory the downloaded file resides.

This wheel is preconfigured to download any prerequisites as well as create an executable in the scripts folder of your python install.

On linux you may also require `python3-pil.imagetk` and `python3-tk` for the GUI to function.

### Important: Installing BIDSHanlder

Biscuit also requires a library that is not yet on [PyPI](https://pypi.org/) and thus needs to be installed in a similar fashion as Biscuit.
To allow Biscuit to read and handle BIDS folder correctly it uses [BIDSHandler](https://github.com/Macquarie-MEG-Research/BIDSHandler).

This can be installed in a similar way to Biscuit by going to the [releases tab](https://github.com/Macquarie-MEG-Research/BIDSHandler/releases) and installing the most recent version.

Biscuit should always be compatible with the most recent version, however this method of installation will be replaced with a more stable version of installing for PyPi automatically once BIDSHandler has been added to it.

## > Don't have Python installed
If you do not have a current Python install on your system, you can either install the [Anaconda](https://anaconda.org/anaconda/python) Python distribution.
Anaconda is however a reasonably large installation, so you may prefer to simply download [Python from the website](https://www.python.org/downloads/release/python-367/) and install Biscuit using pip as above. This has the benefit of also being faster to install and gives you more control over what is installed.
You can also follow the steps to [install MNE-Python](https://www.martinos.org/mne/stable/getting_started.html).

---

# Issues with pip
If you are installing python 3 and the required libraries on a mac (or on a system with another python install) you may have conflicts with the internal python 2.7 install. To get around this you may need to specify excplitly the version of python the libraries are being install into.

Entering
```
python3 --version
```
into a command prompt should show the currently installed version of python 3.
If an error is raised, entering `python --version` should show the current version (>3.4).
If neither `python3 --version` or `python --version` return a value or error, then Python has not been installed correctly. You may need to ensure that python is installed to the path:
[![python_path](https://docs.python.org/3/_images/win_installer.png)](https://docs.python.org/3/using/windows.html)

Note that you *shouldn't* have to do this for python version 3.6 and above (but it is good to go though the "advanced" settings when installing to ensure that it is indeed added to the path to save any headaches later.)

Whichever command (`python` or `python3`) is the one which shows the correctly installed version of python > 3.4, can be used to call pip explicitly for that version:
```
python -m pip install <package names>
```
or
```
python3 -m pip install <package names>
```
where `<package names>` is the list of packages to be installed (`numpy`, `scipy` etc.).

---

# Installing and running Biscuit

Installing Biscuit from the wheel creates an executable in the python scripts folder (`<python install directory>\Scripts\Biscuit.<extension>`).
This executable is generally added to the path if you have administrative rights on the computer, so you can either run Biscuit by simply entering `Biscuit` into a command prompt, or you can create a shortcut to the executable (extension is platform dependent) and run Biscuit like any other executable.

If you create a shortcut to the executable and want to have the nice Biscuit icon it can be found at `<python install directory>\Lib\site-packages\Biscuit\assets\bisc.<ico/png/gif>`.