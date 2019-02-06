from contextlib import redirect_stdout
from time import sleep
import os
import os.path as path
from tkinter import StringVar
from datetime import date
import shutil
from bidshandler import Session

from Biscuit.mne_bids import raw_to_bids
from Biscuit.Management import StreamedVar
from Biscuit.Windows import ProgressPopup
from Biscuit.utils.utils import threaded, assign_bids_data, assign_bids_folder

from Biscuit.utils.timeutils import get_chunk_num, get_year


@threaded
def convert(container, settings, parent=None):
    """
    Main function to take all the data from some container (IC or fif file
    currently) and call the bids conversion function (from mne_bids).
    parent is the main GUI object
    """

    # first, make sure that the container obejct is ready for conversion
    container.prepare()

    # Construct a name for storing 2 weeks worth of BIDS formatted data.
    # We chunk into 2 week blocks for ease of uploading to the MEG_RAW archive.
    chunk_length = settings.get('CHUNK_FREQ', 14)
    if chunk_length == 0:
        subfolder_name = ''
    else:
        curr_date = date.today()
        subfolder_name = 'BIDS-{0}-{1}'.format(
            get_year(curr_date), get_chunk_num(curr_date, chunk_length))

    bids_root_folder_path = path.join(settings['DATA_PATH'], 'BIDS')
    bids_folder_path = path.join(bids_root_folder_path, subfolder_name)

    # Determine if the BIDS-YYYY-FF folder exists already:
    bidstree_folder_exists = path.exists(bids_folder_path)

    # Create variables for the dynamic displaying of the process.
    # We unfortunately cannot get particularly granular or precise progress
    # tracking due to the fact that the conversion is done externally.
    progress = StreamedVar(['Writing', 'Conversion done'],
                           {'Writing': _shorten_path})
    job_name = StringVar()

    has_error = False

    p = ProgressPopup(parent, progress, job_name)

    # get the variables for the raw_to_bids conversion function:
    subject_id = container.subject_ID.get()
    sess_id = container.session_ID.get()
    if sess_id == '':
        sess_id = None
    subject_group = container.subject_group.get()

    target_folder = path.join(bids_folder_path,
                              container.proj_name.get())

    # redict the stout to the StreamedVar as a way of capturing progress
    with redirect_stdout(progress):
        for job in container.jobs:
            if not job.is_junk.get():

                extra_data = job.extra_data

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
                    rec_date = ''.join(date_vals)
                    # TODO: make this more robust?
                    emptyroom_path = ('sub-emptyroom/ses-{0}/meg/'
                                      'sub-emptyroom_ses-{0}_task-'
                                      'noise_meg.con'.format(rec_date))

                if job.is_empty_room.get():
                    emptyroom = True
                    task = 'noise'
                    run = None
                else:
                    task = job.task.get()
                    if task == 'None':
                        task = 'n/a'
                    run = job.run.get()
                    if run == '':
                        run = 'n/a'
                    if emptyroom_path != '':
                        emptyroom = emptyroom_path
                    else:
                        emptyroom = False

                job_name.set("Task: {0}, Run: {1}".format(task, run))

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

                try:
                    raw_to_bids(subject_id=subject_id, task=task,
                                raw_file=job.raw, output_path=target_folder,
                                session_id=sess_id, kind='meg',
                                event_id=event_ids, hpi=mrks, run=run,
                                emptyroom=emptyroom, extra_data=extra_data,
                                subject_group=subject_group,
                                readme_text=container.readme, verbose=True,
                                **container.make_specific_data)
                except:  # noqa
                    # We want to actually just catch any error and print a
                    # message.
                    progress.set("An error occurred during the conversion "
                                 "process.\nPlease check the python console "
                                 "to see the error.")
                    has_error = True

        new_sids = parent.file_treeview.refresh()

        if not bidstree_folder_exists:
            assign_bids_folder(bids_folder_path, parent.file_treeview,
                               parent.preloaded_data)
        else:
            # assign any new BIDS data
            assign_bids_data(new_sids, parent.file_treeview,
                             parent.preloaded_data)

        # find the first instance from the newly added folders that is a
        # bidshandler.Session object and set this is the focus of the treeview.
        for sid in new_sids:
            if isinstance(parent.preloaded_data.get(sid, None), Session):
                parent.file_treeview.see(sid)
                parent.file_treeview.focus(item=sid)
                # sid added as a tuple for pre-3.6 compatibilty
                parent.file_treeview.selection_set((sid,))
                break

        if not has_error:
            # copy over any extra files:
            for file in container.extra_files:
                ext = path.splitext(file)[1]
                if ext in ['.m', '.py']:
                    dst = path.join(target_folder, 'code')
                else:
                    dst = path.join(target_folder,
                                    'sub-{0}'.format(subject_id),
                                    'ses-{0}'.format(sess_id), 'extras')
                if not path.exists(dst):
                    os.makedirs(dst)
                shutil.copy(file, dst)
            print("Conversion done! Closing window in 3...")
            sleep(1)
            print("Conversion done! Closing window in 2...")
            sleep(1)
            print("Conversion done! Closing window in 1...")
            sleep(1)
            p._exit()

    # This is essentially useless but it suppresses pylint:E1111
    return True


def _shorten_path(fname):
    """ strip just the final part of the path """
    return path.basename(fname).split("'")[0]
