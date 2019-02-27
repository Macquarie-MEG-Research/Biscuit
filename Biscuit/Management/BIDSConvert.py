from contextlib import redirect_stdout
from time import sleep
import os
import os.path as op
from tkinter import StringVar
from datetime import date
import shutil
from warnings import warn

from bidshandler import Session

from mne_bids import write_raw_bids, make_bids_basename, make_bids_folders

from Biscuit.Management import StreamedVar
from Biscuit.utils.bids_postprocess import (update_sidecar, write_readme,
                                            update_participants,
                                            modify_dataset_description,
                                            clean_emptyroom, update_markers)
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

    # Find the SID of the BIDS folder.
    bids_root_folder_path = op.join(settings['DATA_PATH'], 'BIDS')
    bids_folder_path = op.join(bids_root_folder_path, subfolder_name)

    # Determine if the BIDS-YYYY-FF folder exists already:
    bidstree_folder_exists = op.exists(bids_folder_path)

    # Create variables for the dynamic displaying of the process.
    # We unfortunately cannot get particularly granular or precise progress
    # tracking due to the fact that the conversion is done externally.
    progress = StreamedVar(['Writing', 'Conversion done'],
                           {'Writing': _shorten_path})
    job_name = StringVar()

    has_error = False

    p = ProgressPopup(parent, progress, job_name)

    target_folder = op.join(bids_folder_path,
                            container.proj_name.get())

    # redict the stout to the StreamedVar as a way of capturing progress
    with redirect_stdout(progress):
        for job in container.jobs:
            if job.is_junk.get():
                continue

            extra_data = job.extra_data

            emptyroom_path = ''
            rec_date = None
            if 'Measurement date' in job.info:
                date_vals = job.info['Measurement date'].split('/')
                date_vals.reverse()
                rec_date = ''.join(date_vals)

            # also check to see if the file is meant to have an associated
            # empty room file
            if job.has_empty_room.get() is True:
                # we will auto-construct a file path based on the date of
                # creation of the con file
                # TODO: make this more robust?
                emptyroom_path = ('sub-emptyroom/ses-{0}/meg/'
                                  'sub-emptyroom_ses-{0}_task-'
                                  'noise_meg.con'.format(rec_date))

            # get the variables for the raw_to_bids conversion function:
            if job.is_empty_room.get():
                if rec_date is None:
                    warn('Recording date is not known. Emptry room cannot be '
                         'exported.')
                    continue
                subject_id = 'emptyroom'
                sess_id = rec_date
                subject_group = 'n/a'
                task = 'noise'
                run = None
                job.raw.info['subject_info'] = None
            else:
                subject_id = container.subject_ID.get()
                sess_id = container.session_ID.get()
                if sess_id == '':
                    sess_id = None
                subject_group = container.subject_group.get()
                task = job.task.get()
                if task == 'None':
                    task = None
                run = job.run.get()
                if run == '':
                    run = None
                if emptyroom_path != '':
                    extra_data['AssociatedEmptyRoom'] = emptyroom_path

            # TODO: change this to just use the event_info property
            trigger_channels, descriptions = job.get_event_data()

            # assume there is only one for now??
            event_ids = dict(zip(descriptions,
                                 [int(i) for i in trigger_channels]))

            job_name.set("Task: {0}, Run: {1}".format(task, run))

            try:
                bids_name = make_bids_basename(
                    subject=subject_id,
                    session=sess_id,
                    task=task,
                    run=run)

                write_raw_bids(
                    raw=job.raw,
                    bids_basename=bids_name,
                    output_path=target_folder,
                    event_id=event_ids,
                    overwrite=True,
                    verbose=True)
                bids_path = make_bids_folders(
                    subject=subject_id,
                    session=sess_id,
                    kind='meg',
                    output_path=target_folder,
                    make_dir=False)

                update_sidecar(op.join(bids_path,
                                       '{0}_meg.json'.format(bids_name)),
                               extra_data)
                update_participants(op.join(target_folder,
                                            'participants.tsv'),
                                    ('sub-{0}'.format(subject_id),
                                        subject_group))
                write_readme(op.join(target_folder, 'README.txt'),
                             container.readme)
                modify_dataset_description(
                    op.join(target_folder, 'dataset_description.json'),
                    container.proj_name.get())
                #update_markers(job, bids_path)
                if subject_id == 'emptyroom':
                    clean_emptyroom(bids_path)

            except:  # noqa
                # We want to actually just catch any error and print a
                # message.
                progress.curr_value.set("An error occurred during the "
                                        "conversion process.\nPlease check "
                                        "the python console to see the error.")
                has_error = True
                raise

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
            ext = op.splitext(file)[1]
            if ext in ['.m', '.py']:
                dst = op.join(target_folder, 'code')
            else:
                dst = op.join(target_folder,
                              'sub-{0}'.format(subject_id),
                              'ses-{0}'.format(sess_id), 'extras')
            if not op.exists(dst):
                os.makedirs(dst)
            shutil.copy(file, dst)
        progress.curr_value.set("Conversion done! Closing window in 3...")
        sleep(1)
        progress.curr_value.set("Conversion done! Closing window in 2...")
        sleep(1)
        progress.curr_value.set("Conversion done! Closing window in 1...")
        sleep(1)
        p._exit()

    # This is essentially useless but it suppresses pylint:E1111
    return True


def _shorten_path(fname):
    """ strip just the final part of the path """
    return op.basename(fname).split("'")[0]
