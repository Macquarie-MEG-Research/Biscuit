from utils import threaded, generate_readme
import os.path as path
from os import makedirs
#from FileTypes import KITData, fif_file
from mne_bids import raw_to_bids


@threaded
def convert(container, settings):
    """
    Main function to take all the data from some container (IC or fif file
    currently) and call the bids conversion function (from mne_bids).
    """

    # first, make sure that the container obejct is ready for conversion
    container.prepare()

    bids_folder_path = path.join(settings['DATA_PATH'], 'BIDS')
    if not path.exists(bids_folder_path):
        makedirs(bids_folder_path)

    for job in container.jobs:
        if not job.is_junk.get():
            print(job)
            print(job.raw, 'raw')
            progress = "Working on acquisition: {0}, task: {1}".format(
                job.acquisition.get(), job.task.get())
            target_folder = path.join(bids_folder_path,
                                      container.proj_name.get())

            # get the variables for the raw_to_bids conversion function:
            subject_id = container.subject_ID.get()
            #task_name = self.task_name.get()
            sess_id = container.session_ID.get()

            extra_data = job.extra_data

            participant_data = {'age': container.subject_age.get(),
                                'gender': container.subject_gender.get(),
                                'group': container.subject_group.get()}

            if sess_id == '':
                sess_id = None
            emptyroom_path = ''

            # TODO: optimize this to handle both FIF and KIT data
            # TODO: change this toi just use the event_info property
            trigger_channels, descriptions = job.trigger_channels()
            # assume there is only one for now??
            event_ids = dict(zip(descriptions,
                                 [int(i) for i in trigger_channels]))

            # also check to see if the file is meant to have an associated
            # empty room file
            if job.has_empty_room.get() is True:
                # we will auto-construct a file path based on the date of
                # creation of the con file
                date_vals = job.info['Measurement date'].split('/')
                date_vals.reverse()
                date = ''.join(date_vals)
                # TODO: make this more robust?
                emptyroom_path = ('sub-emptyroom/ses-{0}/meg/'
                                  'sub-emptyroom_ses-{0}_task-'
                                  'noise_meg.con'.format(date))

            if job.acquisition == 'emptyroom':
                emptyroom = True
            else:
                if emptyroom_path != '':
                    emptyroom = emptyroom_path
                else:
                    emptyroom = False

            mrks = [mrk.file for mrk in job.hpi]

            # finally, run the actual conversion
            raw_to_bids(subject_id, job.task.get(), job.raw, target_folder,
                        electrode=container.contained_files['.elp'][0].file,
                        hsp=container.contained_files['.hsp'][0].file,
                        hpi=mrks, session_id=sess_id,
                        acquisition=job.acquisition.get(),
                        emptyroom=emptyroom, extra_data=extra_data,
                        event_id=event_ids, participant_data=participant_data,
                        readme_text=container.readme)
    """
    # fill the tree all at once??
    self.parent._fill_file_tree(bids_folder_sid, bids_folder_path)
    # set the message to done, but also close the window if it hasn't
    # already been closed
    self.bids_conversion_progress.set("Done")
    """
