from utils import threaded
import os.path as path
from os import makedirs
from tkinter import StringVar
from mne_bids import raw_to_bids
from Management import StreamedVar
from Windows import ProgressPopup
from contextlib import redirect_stdout
from time import sleep


@threaded
def convert(container, settings, parent=None):
    """
    Main function to take all the data from some container (IC or fif file
    currently) and call the bids conversion function (from mne_bids).
    parent is the main GUI object
    """

    # first, make sure that the container obejct is ready for conversion
    container.prepare()

    bids_folder_path = path.join(settings['DATA_PATH'], 'BIDS')
    if not path.exists(bids_folder_path):
        makedirs(bids_folder_path)
        bids_folder_sid = parent.file_treeview.ordered_insert(
            '', text='BIDS', values=('', bids_folder_path))
    else:
        for sid in parent.file_treeview.get_children():
            if parent.file_treeview.item(sid)['text'] == 'BIDS':
                bids_folder_sid = sid
                break

    progress = StreamedVar(['Writing', 'Conversion done'],
                           {'Writing': _shorten_path})
    job_name = StringVar()

    p = ProgressPopup(parent, progress, job_name)

    with redirect_stdout(progress):
        for job in container.jobs:
            job_name.set("Run: {0}, Task: {1}".format(
                job.run.get(), job.task.get()))
            if not job.is_junk.get():
                target_folder = path.join(bids_folder_path,
                                          container.proj_name.get())

                # get the variables for the raw_to_bids conversion function:
                subject_id = container.subject_ID.get()
                #task_name = self.task_name.get()
                sess_id = container.session_ID.get()

                extra_data = job.extra_data
                subject_group = container.subject_group.get()

                if sess_id == '':
                    sess_id = None
                emptyroom_path = ''

                # TODO: change this to just use the event_info property
                trigger_channels, descriptions = job.get_event_data()

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

                if job.is_empty_room.get():
                    emptyroom = True
                else:
                    if emptyroom_path != '':
                        emptyroom = emptyroom_path
                    else:
                        emptyroom = False

                mrks = None
                # process the list of mrks:
                if job.hpi is not None:
                    if isinstance(job.hpi, list):
                        if len(job.hpi) == 1:
                            # only have one marker coil
                            mrks = job.hpi[0].file
                        elif len(job.hpi) == 2:
                            # initiate an empty list
                            mrks = [None, None]
                            for mrk in job.hpi:
                                if mrk.acquisition.get() == 'pre':
                                    mrks[0] = mrk.file
                                elif mrk.acquisition.get() == 'post':
                                    mrks[1] = mrk.file
                                else:
                                    # in this case it isn't specified. Best we
                                    # can do it just add it. Maybe raise a
                                    # message?
                                    mrks.append(mrk.file)
                            # drop any None values just in case:
                            for _ in range(mrks.count(None)):
                                mrks.remove(None)

                raw_to_bids(subject_id=subject_id, task=job.task.get(),
                            raw_file=job.raw, output_path=target_folder,
                            session_id=sess_id, kind='meg', event_id=event_ids,
                            hpi=mrks, run=job.run.get(),
                            emptyroom=emptyroom, extra_data=extra_data,
                            subject_group=subject_group,
                            readme_text=container.readme, verbose=True,
                            **container.make_specific_data)
        print("Conversion done! Closing window in 3...")
        sleep(1)
        print("Conversion done! Closing window in 2...")
        sleep(1)
        print("Conversion done! Closing window in 1...")
        sleep(1)
        p._exit()

    parent._fill_file_tree(bids_folder_sid, bids_folder_path)

    # This is essentially useless but it suppresses pylint:E1111
    return True


def _shorten_path(fname):
    """ strip just the final part of the path """
    return path.basename(fname)[:-6]
