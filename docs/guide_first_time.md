# First-time use guide

At first glance Biscuit may look a little bit daunting to use, but once you are familiar with how it works it is very simple and fast to use.

### Add new project settings

If it is your first time using Biscuit to convert some MEG data, you must ensure that the first thing you do before trying to convert any data is to enter the default project settings for your project.
This will allow Biscuit to automatically assign a number of values which saves a lot of time for yourself and can lead to almost automatic exporting, requiring only a few values to be selected.

To add new project settings you can follow the guide [here](guide_new_proj_settings.md).
It is recommended that you add these settings as soon as you know what they are so that when you take some measurements and open Biscuit for file conversion the data is already added and you do not need to worry about adding them then.
Don't worry if you mess up the settings, they can be changed later and the old file will be overwritten with the new settings.

### Exporting data to a BIDS compliant folder

Next, select the folder on the left-hand side that contains the newly acquired data.

If you have acquired data using a Yokogawa/KIT system, you can proceed to follow the guide specifically for this data [here](guide_kit.md).
If you have acquired data using an Elekta system, the specific guide can be found [here](guide_elekta.md).

### Copying data off computer (if required)

The BIDS-compliant data exported by Biscuit will be placed in a sub-folder of a folder named `BIDS`. Depending on your settings it will most likely be placed in a folder named `BIDS-XX` where `XX` is a number. This is to chunk the data so if Biscuit is used on a computer where large amounts of data is being generated, finding the most recent data is easy for those who may need to back up the data.

To transfer the data off one computer and onto another the easiest way is to use Biscuit's built in file-transfer abilities. This is recommended because it is able to transfer the data in a way that is 'BIDS-safe'. This means that you can transfer the data to another folder containing BIDS-compliant data and the new data will be merged automatically into the file hierarchy.

Transferring your BIDS-compliant data is as easy as selecting the folder you want to transfer, right-click the folder name in the built-in file browser, then selecting 'Send to...'.
This will display a pop-up which will let you select the location to transfer your files. It is **highly recommnded** that you select the same folder every time you do this. This is most easily achieved by using an external HDD and having a folder on it called `BIDS` (for example). Every time you transfer data off the computer using Biscuit, transfer to this BIDS folder and it will always contain the entire BIDS folder structure of your data.

*Note*: If you do not see the 'Send to...' option the folder hasn't been specified as a folder containing BIDS formatted data. You can fix this by right-clicking the `BIDS_XX` folder and selecting 'Assign as BIDS folder'.

### Finishing up

Now that your data has been "BIDSified", you have an easy to search folder containing all the data from your various experiments.
In the future Biscuit will be able to be used to search this data so that specific tests or recordings can be found easily to allow for easy identification for analysis purposes.