import sys
import subprocess
from platform import system as os_name

import requests

git_api = 'https://api.github.com'
owner = 'Macquarie-MEG-Research'
repo = 'Biscuit'
cmd = '/repos/{0}/{1}/releases/latest'.format(owner, repo)


def get_latest_release():
    r = requests.get(git_api + cmd)
    data = r.json()

    return data


def do_update(data):
    asset = data.get('assets', [None])[0]
    if asset is not None:
        whl_url = asset['browser_download_url']

    # get the current version of python running
    python_path = sys.executable

    update_args = ['-m', 'pip', 'install', '-U', whl_url]

    if os_name() == 'Windows':
        # code c/o Martin De la Fuente from Stackoverflow:
        # https://stackoverflow.com/a/41930586
        # we want to elevate the privileges:
        import ctypes

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
