from utils import threaded, generate_readme
import os.path as path
from os import makedirs
from FileTypes import KITData, fif_file
from mne_bids import raw_to_bids


@threaded
def _make_bids_folders(container, settings):
    """
    Main function to take all the data from some container (IC or fif file
    currently) and call the bids conversion function (from mne_bids).
    """

    # first, make sure that the container obejct is ready for conversion
    container.prepare()

    # how to sort out the pathing of the bids folder?
    bids_folder_sid = None
    bids_folder_path = path.join(settings['DATA_PATH'], 'BIDS')
    for sid in self.parent.file_treeview.get_children():
        if self.parent.file_treeview.item(sid)['text'] == 'BIDS':
            bids_folder_sid = sid
            break
    if bids_folder_sid is None:
        # in this case it doesn't exist so make a new folder
        makedirs(bids_folder_path)
        bids_folder_sid = self.parent.file_treeview.ordered_insert(
            '', text='BIDS', values=('', bids_folder_path))

    # we will need to be able to handle different type of data coming in.
    # Hopefully eventually this will be brough together so that there is one
    # unified standard for all files that contain the data required for
    # conversion...
    if isinstance(container, KITData):
        raw_files = container.raw_files
    elif isinstance(container, fif_file):
        raw_files = {(container.acquisition.get(), container.task.get()):
                     container._raw}

    for at, raw_kit in raw_files.items():
        self.bids_conversion_progress.set(
            "Working on acquisition {0}".format(at))
        target_folder = path.join(bids_folder_path,
                                    self.proj_name.get())

        # get the variables for the raw_to_bids conversion function:
        subject_id = container.subject_ID.get()
        #task_name = self.task_name.get()
        sess_id = container.session_ID.get()

        extra_data = container.extra_data[at]

        # generate the readme
        if isinstance(settings, dict):
            readme = generate_readme(settings)
        else:
            readme = None

        participant_data = {'age': container.subject_age.get(),
                            'gender': container.subject_gender.get(),
                            'group': container.subject_group.get()}

        if sess_id == '':
            sess_id = None
        emptyroom_path = ''

        # get the event data from the associated con files:
        for con in self.con_map[at]:
            trigger_channels, descriptions = con.get_trigger_channels()
            # assume there is only one for now??
            event_ids = dict(zip(descriptions,
                                 [int(i) for i in trigger_channels]))

            # also check to see if the file is meant to have an associated
            # empty room file
            if con.has_empty_room.get() is True:
                # we will auto-construct a file path based on the date of
                # creation of the con file
                date_vals = con.info['Measurement date'].split('/')
                date_vals.reverse()
                date = ''.join(date_vals)
                emptyroom_path = ('sub-emptyroom/ses-{0}/meg/'
                                    'sub-emptyroom_ses-{0}_task-'
                                    'noise_meg.con'.format(date))

        if at[0] == 'emptyroom':
            emptyroom = True
        else:
            if emptyroom_path != '':
                emptyroom = emptyroom_path
            else:
                emptyroom = False

        con = self.con_map[at][0]
        mrks = [mrk.file for mrk in con.hpi]

        # finally, run the actual conversion
        raw_to_bids(subject_id, at[1], raw_kit, target_folder,
                    electrode=self.contained_files['.elp'][0].file,
                    hsp=self.contained_files['.hsp'][0].file,
                    hpi=mrks, session_id=sess_id, acquisition=at[0],
                    emptyroom=emptyroom, extra_data=extra_data,
                    event_id=event_ids, participant_data=participant_data,
                    readme_text=readme)
    # fill the tree all at once??
    self.parent._fill_file_tree(bids_folder_sid, bids_folder_path)
    # set the message to done, but also close the window if it hasn't
    # already been closed
    self.bids_conversion_progress.set("Done")
