# Installing Biscuit

Biscuit is completely written in Python, allowing it to be run on any computer you can install Python on.
To allow for the reading of MEG data and conversion a few libraries are required to be installed.

If you do not have Python installed already, or only have an older version installed (such as the built-in python 2 on Macs) simply download [Python from the official website](https://www.python.org/downloads/).

### There are two different install options for Biscuit:

### "Complete" install

If you are only going to be using Python for Biscuit the it is recommended that you download the "complete" version.
This will automatically install the latest version of Biscuit with all required prerequisites.
To install, enter the following into a command prompt:
<pre><code id="gh_download_command_complete">If you can read this, download the file from the link in the dropdown or from the github source release page.</code></pre>

### "Standard" install

If you already have a pre-existing python install and do not want any particular packages to be downloaded, or know how to install any prerequisites yourself, the normal install can be installed by entering the following into a command prompt:

<pre><code id="gh_download_command_standard">If you can read this, download the file from the link in the dropdown or from the github source release page.</code></pre>

The complete list of prequisites are as follows:

`numpy`, `scipy`, `matplotlib`, `pandas`, `Pygments`, `Pillow`, `mne (>= 0.17.0)`, `mne-bids (>= 0.1)`, `requests` and `bidshandler (>= 0.2.1)`

Unlike the complete install, this install will not create an executable to run Biscuit.

#### Current issue with MNE-BIDS

Due to Biscuit requiring some newer features included in MNE-BIDS it is required to have the most recent version from GitHub.
This can be obtained by downloading and building the most recent version of the master branch, or, if you want it done automatically the update feature in Biscuit is currently able to also install the most recent version from GitHub.
To find the update button press 'Info' > 'Credits', then select 'Update' on the pop up. This also allows for easy updating of Biscuit.
**Note** that the auto updater will install the "complete" version.

---

## Running Biscuit

Installing Biscuit from the "complete" wheel file (`.whl`) creates an executable in the python scripts folder (`<python install directory>\Scripts\Biscuit.<extension>`).
This executable is generally added to the path if you have administrative rights on the computer, so you can either run Biscuit by simply entering `Biscuit` into a command prompt, or you can create a shortcut to the executable (extension is platform dependent) and run Biscuit like any other executable.
The easiest way to do this is to simply create a shortcut with the location pointing to `Biscuit`.

If you create a shortcut to the executable and want to have the nice Biscuit icon it can be found at `<python install directory>\Lib\site-packages\Biscuit\assets\bisc.<ico/png/gif>`.

If installing from the "standard" install, you can create a shortcut with the following path:
```
python -c "from Biscuit import run;run()"
```
This will call python and tell it to run Biscuit.

---

### Potential issues

#### > `'pip' is not recognized as an internal or external command`:

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