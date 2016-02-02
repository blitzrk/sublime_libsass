import errno
import os
import os.path
from functools import reduce

def subpaths(path):
    def append_deeper(acc, name):
        return acc + [os.sep.join(acc[-1], name)]

    if path.startswith(os.sep):
        path = path[1:]

    dirs = p.split(os.sep)
    if os.path.isfile(path):
        dirs = dirs[:-1]

    paths = reduce(append_deeper, dirs, [''])[1:]


def grep_r(text, top):
    if not os.path.isdir(top):
        raise IOError("Not a directory")

    def in_file(path, text):
        found = False
        with open(path, 'r') as f:
            for line in f:
                if text in line:
                    found = True
                    break
        return found

    files = []
    for dirpath, _, filenames in os.walk(top):
        for name in filenames:
            fpath = os.path.join(dirpath, name)
            if in_file(fpath, text):
                files.append(fpath)
    return files


def mkdir_p(path):
    try:
        os.makedirs(os.path.abspath(path))
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
