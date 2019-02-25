import sys
import subprocess
from platform import system as os_name
import ctypes
import tempfile
from io import BytesIO
import os.path as op
import zipfile
import os

import requests

GIT_API = 'https://api.github.com'


def get_latest_release():
    owner = 'Macquarie-MEG-Research'
    repo = 'Biscuit'
    cmd = '/repos/{0}/{1}/releases/latest'.format(owner, repo)
    r = requests.get(GIT_API + cmd)
    data = r.json()

    return data


def do_update(data):
    asset = data.get('assets', [None])[0]
    if asset is not None:
        whl_url = asset['browser_download_url']

    # get the current version of python running
    python_path = sys.executable

    update_args = ['-m', 'pip', 'install', '-U', whl_url]

    run_elevated(python_path, update_args)


def run_elevated(python_path, update_args):
    if os_name() == 'Windows':
        # code c/o Martin De la Fuente from Stackoverflow:
        # https://stackoverflow.com/a/41930586
        # we want to elevate the privileges:

        def is_admin():
            return ctypes.windll.shell32.IsUserAnAdmin()

        if is_admin():
            subprocess.run([python_path] + update_args)
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, 'runas', python_path, ' '.join(update_args), None, 1)
    else:
        # TODO: figure out for linux and mac?
        subprocess.run([python_path] + update_args)


def update_mne_bids():
    cmd = '/repos/mne-tools/mne-bids/zipball'
    old_cwd = os.getcwd()
    r = requests.get(GIT_API + cmd)

    # get the current version of python running
    python_path = sys.executable

    tmp = tempfile.mkdtemp()

    print(tmp)

    data = BytesIO(r.content)
    with open(op.join(tmp, 'mne-bids.zip'), 'wb') as mne_zip:
        mne_zip.write(data.getvalue())
    mnezip = zipfile.ZipFile(op.join(tmp, 'mne-bids.zip'))
    folder_name = mnezip.namelist()[0].rstrip('/')
    mnezip.extractall(tmp)
    mnezip.close()
    # run setup.py on the library
    if folder_name in os.listdir(tmp):
        mne_bids_dir = op.join(tmp, folder_name)
        os.chdir(mne_bids_dir)
        subprocess.run([python_path, 'setup.py',
                        'sdist', 'bdist_wheel'])
        dist_dir = op.join(mne_bids_dir, 'dist')
        os.chdir(dist_dir)
        wheel = None
        for fname in os.listdir(dist_dir):
            if op.splitext(fname)[1] == '.whl':
                wheel = fname
        if wheel is not None:
            update_args = ['-m', 'pip', 'install', '-U', wheel]
            run_elevated(python_path, update_args)
    # reset the cwd
    os.chdir(old_cwd)
    return tmp
