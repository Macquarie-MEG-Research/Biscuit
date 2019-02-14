import pickle
import os.path as path
from os import makedirs, replace, rename
from tkinter import StringVar
from datetime import datetime
from warnings import warn

from bidshandler import BIDSTree

from Biscuit.FileTypes import FIFData, con_file, mrk_file, KITData
from Biscuit.utils.constants import OSCONST
from Biscuit.utils.utils import assign_bids_folder

""" Save format specification/taken names:
    # FileInfo:
    file:   file name           string
    jnk:    is junk             bool
    # BIDSFile:
    run:    run                 int
    tsk:    task                string
    hpi:    marker coils        dict
    ier:    is empty room       bool
    her:    has empty room      bool
    # BIDSContainer:
    prj:    project ID          string
    sid:    session ID          string
    sji:    subject ID          string
    sja:    subject age         int
    sjs:    subject gender      string
    sjg:    subject group       string
    # KITData:
    dwr:    dewar position
    # con_file:
    cin:    channel info        # TODO: merge with FIFData format (somehow???)
    # FIFData:
    chs:    channel info        # TODO: move to BIDSContainer
    evt:    event info
    # mrk_file
    # TODO: This will probably change at some point once the spec is decided on
    acq:    acquisition ('pre', 'post' or 'mult', file isn't saved if 'n/a')
"""


class SaveManager():
    """
    A class to organise the saving of all the data produced while interacting
    with the GUI.
    This will take any file that has had any changes made to it and store them
    to the HDD so that the next time a user runs the program they can be
    retreived and applied to avoid data having to be entered multiple times.
    """
    def __init__(self, parent=None):
        """
        parent is the main GUI object
        savepath is the location of the save data
        We will mainly just be getting the preloaded data from it so we can
        read any data we need when we are saving
        """
        self.parent = parent
        self.save_path = OSCONST.USRDIR
        savefile_name = 'savedata.save'
        self.save_file = path.join(self.save_path, savefile_name)

        self.saved_time = StringVar()
        self.saved_time.set("Last saved:\tNever")

        self.treeview_ids = []

#region public methods

    def get_file_id(self, path_):
        """
        Returns the id of the entry in the treeview that has the specified
        path.
        """
        try:
            return self.parent.file_treeview.sid_from_filepath(path_)
        except KeyError:
            raise FileNotFoundError

    # TODO: clean this up a bit? Not sure what can be re-factored, but it
    # should be able to be made a bit nicer...
    def load(self):
        """
        This needs some error handling!!
        """
        _data = self.parent.preloaded_data

        # get the list of all children to the treeview:
        self.treeview_ids = list(self.parent.file_treeview.all_children())
        # remove root
        self.treeview_ids.remove('')

        containers_to_load = []

        # first retrieve all the data from the save file
        if path.exists(self.save_file):
            load_time = datetime.fromtimestamp(path.getmtime(self.save_file))
            self.saved_time.set("Last saved:\t{0}".format(
                load_time.strftime("%Y-%m-%d %H:%M:%S")))
            for file in self._load_gen():
                try:
                    if isinstance(file, con_file):
                        # set the file's id from the treeview
                        sid = self.get_file_id(file.file)
                        file.ID = sid
                        # also give it the right settings
                        file.settings = self.parent.proj_settings
                        # then add the file to the preloaded data
                        _data[file.ID] = file
                    elif isinstance(file, KITData):
                        containers_to_load.append(file)
                    elif isinstance(file, FIFData):
                        file.loaded_from_save = True
                        sid = self.get_file_id(file.file)
                        file.ID = sid
                        file.parent = self.parent
                        # also give it the right settings
                        file.settings = self.parent.proj_settings
                        # the file is it's own container too
                        file.container = file
                        # get the file to load it's data
                        file.load_data()
                        # then add the file to the preloaded data
                        _data[file.ID] = file
                    elif isinstance(file, mrk_file):
                        sid = self.get_file_id(file.file)
                        file.ID = sid
                        _data[file.ID] = file
                    elif isinstance(file, list):
                        # TODO: improve...
                        # In this case it is the BIDSTree data
                        # load all the info (I guess?)
                        for fpath in file:
                            assign_bids_folder(fpath,
                                               self.parent.file_treeview,
                                               _data)
                except FileNotFoundError:
                    pass
            # load containers after files to ensure the files are referenced in
            # the container correctly.
            for file in containers_to_load:
                try:
                    sid = self.get_file_id(file.file)
                    file.ID = sid
                    file.parent = self.parent
                    file.load_data()
                    file.settings = self.parent.proj_settings
                    _data[file.ID] = file

                    # find any children of the IC and give them this object as
                    # the parent
                    for child_id in self.parent.file_treeview.get_children(sid):  # noqa
                        if child_id in _data:
                            _data[child_id].container = file
                            _data[child_id].parent = self.parent
                except FileNotFoundError:
                    pass

            # now fix up any associated_mrk's that need to be actual
            # mrk_file objects
            for _, obj in self.parent.preloaded_data.items():
                try:
                    obj.loaded_from_save = True
                    if isinstance(obj, con_file):
                        obj.load_data()
                        mrk_paths = obj.hpi
                        if isinstance(mrk_paths, dict):
                            for key, value in mrk_paths.items():
                                sid = self.get_file_id(value)
                                try:
                                    mrk_paths[key] = self.parent.preloaded_data[sid]  # noqa
                                except KeyError:
                                    mrk_paths[key] = mrk_file(id_=sid,
                                                              file=value)
                        elif isinstance(mrk_paths, list):
                            new_mrk_data = dict()
                            for mrk_path in mrk_paths:
                                sid = self.get_file_id(mrk_path)
                                try:
                                    mrk = self.parent.preloaded_data[sid]
                                except KeyError:
                                    mrk = mrk_file(id_=sid, file=mrk_path)
                                new_mrk_data[mrk.acquisition.get()] = mrk
                            obj.hpi = new_mrk_data
                        # also validate the con file:
                        obj.validate()
                except FileNotFoundError:
                    pass

            # autodetect any empty room changes
            for file in containers_to_load:
                file.autodetect_emptyroom()

    def save(self):
        """
        Saves all the entered user data.
        """
        # first make sure the directory exists:
        if not path.exists(self.save_path):
            makedirs(self.save_path)
        temp_save = self.save_file + '_temp'
        BIDSTree_paths = []
        with open(temp_save, 'wb') as f:
            for file in self.parent.preloaded_data.values():
                if hasattr(file, 'requires_save'):
                    if file.requires_save:
                        try:
                            pickle.dump(file, f)
                        except (TypeError, AttributeError):
                            warn('error saving file: {0}'.format(file))
                            raise
                if isinstance(file, BIDSTree):
                    BIDSTree_paths.append(file.path)
            pickle.dump(BIDSTree_paths, f)

            savetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.saved_time.set("Last saved:\t{0}".format(savetime))
        # if we have reached here then the file was saved and we can
        # replace the actual save data with the temp one
        if path.exists(self.save_path):
            replace(temp_save, self.save_file)
        else:
            rename(temp_save, self.save_file)

#region private methods

    def _load_gen(self):
        """
        This is a generator to iterate over the specified file and
        return the values as required

        script c/o Lutz Prechelt
        (cf. https://stackoverflow.com/questions/20716812/saving-and-loading-multiple-objects-in-pickle-file)  # noqa
        """
        with open(self.save_file, "rb") as f:
            while True:
                try:
                    yield pickle.load(f)
                except EOFError:
                    break
