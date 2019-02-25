import subprocess


def authorise(fpath):
    ret = subprocess.run(["cmd",
                          "/c NET USE {0}".format(fpath)])

    if ret.returncode == 0:
        return True
    return False
