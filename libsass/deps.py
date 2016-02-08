from libsass.pathutils import grep_r
from libsass import project
import os
import re


def is_partial(path):
    '''Check if file is a Sass partial'''

    return os.path.basename(path).startswith('_')


def partial_import_name(path):
    '''Get name of Sass partial file as would be used for @import'''

    dirname, basename = os.path.split(path)
    name = os.path.splitext(basename)[0][1:]
    return os.path.join(dirname, name).replace("\\","/")


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

    import_stmt = re.compile(r"@import\s+'{0}'".format(partial_import_name(file_path)))
    for f in grep_r(import_stmt, start):
        if f not in files and f not in partials:
            files, partials = get_rec(f, start, files, partials)

    return (files, partials)


def get(path):
    '''Get files affected by change in contents of `path`'''

    rel, root = project.splitpath(path)
    deps, _ = get_rec(rel, root)
    return (deps, root)
