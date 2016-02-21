from .pathutils import grep_r
from . import project
import os
import re


def is_partial(path):
    '''Check if file is a Sass partial'''

    return os.path.basename(path).startswith('_')


def partial_import_regex(partial):
    '''Get name of Sass partial file as would be used for @import'''

    def from_curdir(cwd):
        relpath = os.path.relpath(partial, cwd)
        dirname, basename = os.path.split(relpath)
        name = os.path.splitext(basename)[0][1:]
        partial_import = os.path.join(dirname, name).replace("\\","/")
        print(partial_import)
        import_stmt = re.compile(r"@import\s+'{0}'".format(partial_import))
        return import_stmt

    return from_curdir


def get_rec(file_path, start, files=None, partials=None):
    '''
    Recursively find files importing `partial` in `start` and if any are partials
    themselves, find those importing them.
    '''

    if files is None:
        files = []
    if partials is None:
        partials = []

    if not is_partial(file_path):
        files.append(file_path)
        return (files, partials)
    else:
        partials.append(file_path)

    partial_fn = partial_import_regex(os.path.join(start, file_path))
    for f in grep_r(partial_fn, start):
        if f not in files and f not in partials:
            files, partials = get_rec(f, start, files, partials)

    return (files, partials)


def get(path):
    '''Get files affected by change in contents of `path`'''

    rel, root = project.splitpath(path)
    deps, _ = get_rec(rel, root)
    return (deps, root)
