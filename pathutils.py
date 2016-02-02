import errno
from functools import reduce
import os
import os.path
import re

def subpaths(path):
    def append_deeper(acc, name):
        return acc + [acc[-1] + os.sep + name]

    if path.startswith(os.sep):
        path = path[1:]

    dirs = path.split(os.sep)
    if os.path.isfile(path):
        dirs = dirs[:-1]

    paths = reduce(append_deeper, dirs, [''])[1:]
    paths.reverse()
    return paths


def grep_r(pattern, start):
    if not os.path.isdir(start):
        raise IOError("Not a directory")

    pattern = re.compile(pattern)

    def in_file(path, pattern):
        found = False
        with open(path, 'r') as f:
            for line in f:
                if pattern.match(line):
                    found = True
                    break
        return found

    files = []
    for dirpath, _, filenames in os.walk(start):
        for name in filenames:
            fpath = os.path.join(dirpath, name)
            if in_file(fpath, pattern):
                files.append(os.path.relpath(fpath, start))
    return files


def mkdir_p(path):
    try:
        os.makedirs(os.path.abspath(path))
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
