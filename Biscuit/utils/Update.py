import sys
import subprocess

import requests

# TODO: figure out how to run as admin/only allow when run by admin??

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

    subprocess.run([python_path, '-m', 'pip', 'install', '-U', whl_url])