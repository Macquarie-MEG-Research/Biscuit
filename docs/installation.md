# Installating Biscuit

Biscuit is completely written in python, allowing it to be run on any computer you can install python on.
To allow for the reading of MEG data and conversion a few libraries are required to be installed.

If you do not have python installed already, or only have an older version installed (such as the built-in python 2 on Macs) simply download [Python from the official website](https://www.python.org/downloads/release/python-367/).

Biscuit can be installed easily in one of two ways:

## "Complete" install

If you are only really going to be using your python install for Biscuit the recommended method if installation is the "Complete" method.
This will automatically install the latest version of all of the prerequisites and install Biscuit as an executable so you can create a desktop icon for it or run it directly from the command line.
To do this select the `Downloads > 'Complete install'` button in the above menu and download the file to somewhere memorable on your computer.

## "Standard" install

If you already have a pre-existing python install and do not want any particular packages to be downloaded/know how to install any prerequisites yourself the normal install can be installed by selecting the `Downloads > 'Standard install'` button from the above menu.
The complete list of prequisites are as follows:

`numpy`, `scipy`, `matplotlib`, `pandas`, `Pygments`, `Pillow`, `mne (>= 0.17.0)`, `requests` and `bidshandler (>= 0.2.1)`

Unlike the complete install, this install will not create an executable to run Biscuit.

### Windows installation

Navigate to the folder in explorer, then hold the `shift` key and `right-click` to bring up the context menu.
Select `'Open PowerShell window here'` to open a command prompt in the current folder.
Enter
```
pip install -U Biscuit-X.Y.Zcomplete-py3-none-any.whl
```
where `X.Y.Z` is the version number of the package you downloaded.
The `-U` command will update any previously existing version of Biscuit you may have installed.

### Mac/Linux installation

Using the terminal, naviate to the folder the `.whl` file was downloaded to (eg. by using `cd location_of_file`)
Enter
```
python3 -m pip install -U Biscuit-X.Y.Zcomplete-py3-none-any.whl
```
where `X.Y.Z` is the version number of the package you downloaded.
The `-U` command will update any previously existing version of Biscuit you may have installed.

On linux you may also require `python3-pil.imagetk` and `python3-tk` for the GUI to function.

---

# Issues with pip
If you are installing python 3 and the required libraries on a mac (or on a system with another python install) you may have conflicts with the internal python 2.7 install. To get around this you may need to specify excplitly the version of python the libraries are being install into.

Entering
```
python3 --version
```
into a command prompt should show the currently installed version of python 3.
If an error is raised, entering `python --version` should show the current version (>3.4).
If neither `python3 --version` or `python --version` return a value or error, then Python has not been installed correctly.

**You may need to ensure that python is installed to the path. Select 'Add PythonX.Y to PATH' option:**
[![python_path](https://docs.python.org/3/_images/win_installer.png)](https://docs.python.org/3/using/windows.html)

Note that you *shouldn't* have to do this for python version 3.6 and above (but it is good to go though the "advanced" settings when installing to ensure that it is indeed added to the path to save any headaches later.)

Whichever command (`python` or `python3`) is the one which shows the correctly installed version of python > 3.4, can be used to call pip explicitly for that version:
```
python -m pip install <package name(s)>
```
or
```
python3 -m pip install <package name(s)>
```
where `<package names>` is the list of packages to be installed (`numpy`, `scipy` etc.).

---

# Running Biscuit

Installing Biscuit from the "complete" wheel file (`.whl`) creates an executable in the python scripts folder (`<python install directory>\Scripts\Biscuit.<extension>`).
This executable is generally added to the path if you have administrative rights on the computer, so you can either run Biscuit by simply entering `Biscuit` into a command prompt, or you can create a shortcut to the executable (extension is platform dependent) and run Biscuit like any other executable.

If you create a shortcut to the executable and want to have the nice Biscuit icon it can be found at `<python install directory>\Lib\site-packages\Biscuit\assets\bisc.<ico/png/gif>`.

If installing from the "standard" install, you can create a shortcut with the following path:
```
python -c "from Biscuit import run;run()"
```
This will call python and tell it to run Biscuit.