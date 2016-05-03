import errno
from functools import reduce
import io
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

    if type(pattern_fn) is str:
        pattern_fn = lambda x: pattern_fn

    def in_file(path, pattern):
        ext = os.path.splitext(path)[1]
        if kwargs['exts'] and ext not in kwargs['exts']:
            return False

        found = False
        with io.open(path, 'r', encoding="utf-8") as f:
            try:
                lineno = 0
                for line in f:
                    if pattern.match(line):
                        found = True
                        break
                    lineno += 1
            except UnicodeError as e:
                name = os.path.basename(path)
                print(u"Cannot read file {0} at line {1}:".format(name, lineno))
                print(e.object[e.start:e.end])
                print(e.reason)
                print(u"Warning: skipping file {0}".format(path))
        return found

    files = []
    for dirpath, _, filenames in os.walk(start):
        pattern = pattern_fn(dirpath)
        for name in filenames:
            fpath = os.path.join(dirpath, name)
            if in_file(fpath, pattern):
                files.append(os.path.relpath(fpath, start))
    return files


def find_type_dirs(root, filetypes):
    '''Find all directories below and incl root that contain filetypes'''
    if type(filetypes) is str:
        filetypes = (filetypes,)

    #TODO: remove duplicates
    return [path for path, _, files in os.walk(root) 
            if any([os.path.splitext(f)[1] in filetypes for f in files])]


def mkdir_p(path):
    '''Make directory and all subdirectories if they do not exist'''

    try:
        os.makedirs(os.path.abspath(path))
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
