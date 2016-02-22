import errno
from functools import reduce
import os

def subpaths(path):
    '''List of all recursive parents of `path` in distance order'''

    def append_deeper(acc, name):
        return acc + [acc[-1] + os.sep + name]

    drive, dirs = os.path.splitdrive(path)
    dirs = dirs.split(os.sep)
    if os.path.isfile(path):
        dirs = dirs[:-1]

    paths = reduce(append_deeper, dirs, [''])[1:]
    paths = [d[1:] if d.startswith(os.sep+os.sep) else d for d in paths]
    paths = [drive + d for d in paths]

    paths.reverse()
    return paths


def grep_r(pattern_fn, start, **kwargs):
    '''
    Search recursively down from `start` for regex `pattern` in
    files and return list of all matching files relative to `start`

    `pattern` should be derived from `pattern_fn` by applying the
    current directory being searched to the 1-arity function
    '''

    if not os.path.isdir(start):
        raise IOError("Not a directory")

    def in_file(path, pattern):
        ext = os.path.splitext(path)[1]
        if kwargs['exts'] and ext not in kwargs['exts']:
            return False

        found = False
        with open(path, 'r') as f:
            for line in f:
                if pattern.match(line):
                    found = True
                    break
        return found

    files = []
    for dirpath, _, filenames in os.walk(start):
        pattern = pattern_fn(dirpath)
        for name in filenames:
            fpath = os.path.join(dirpath, name)
            if in_file(fpath, pattern):
                files.append(os.path.relpath(fpath, start))
    return files


def mkdir_p(path):
    '''Make directory and all subdirectories if they do not exist'''

    if os.path.exists(path):
        return
    
    try:
        os.makedirs(os.path.abspath(path))
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
