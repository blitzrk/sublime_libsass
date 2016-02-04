import sublime
import sublime_plugin

import errno
from functools import reduce
import json
import os
import os.path
import re
import sass
import stat
from subprocess import PIPE, Popen

# Guarantee sassc is executable
if not os.access(sass.path, os.X_OK):
    mode = os.stat(sass.path).st_mode
    os.chmod(sass.path, mode | stat.S_IEXEC)


def subpaths(path):
    '''List of all recursive parents of `path` in distance order'''

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
    '''
    Search recursively down from `start` for regex `pattern` in
    files and return list of all matching files relative to `start`
    '''

    if not os.path.isdir(start):
        raise IOError("Not a directory")

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
    '''Make directory and all subdirectories if they do not exist'''

    try:
        os.makedirs(os.path.abspath(path))
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


default_opts = {
    "output_dir": "build/css",
    "options": {
        "line-comments": True,
        "line-numbers":  True,
        "style":         "nested"
    }
}


def find_opts(top):
    '''Search up parent tree for libsass config file'''

    for path in subpaths(top):
        file = os.path.join(path, '.libsass.json')
        if os.path.isfile(file):
            return file


def read_opts(file):
    '''
    Read json-formatted config file into map and fill missing values
    with defaults
    '''

    with open(file, 'r') as f:
        user_opts = json.load(f)

    opts = default_opts
    opts.update(user_opts)
    return opts


def to_flags(options):
    '''Convert map into list of standard POSIX flags'''

    flags = []
    for key, value in options.items():
        if value is True:
            flags.append('--{0}'.format(key))
        elif value is not False:
            flags.append('--{0}={1}'.format(key, value))
    return flags


def is_partial(path):
    '''Check if file is a Sass partial'''

    return os.path.basename(path).startswith('_')


def partial_import_name(path):
    '''Get name of Sass partial file as would be used for @import'''

    dirname, basename = os.path.split(path)
    name = os.path.splitext(basename)[0][1:]
    return os.path.join(dirname, name).replace("\\","/")


def importing_files(file_path, start, files=None, partials=None):
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
            files, partials = importing_files(f, start, files, partials)

    return (files, partials)


class CompileSassCommand(sublime_plugin.WindowCommand):
    '''
    WindowCommand `compile_sass` to compile Sass asset and assets importing it
    For use in a build system
    '''

    def run(self, **build):
        file_path = build['cmd'] # Only certain keys have values expanded, such as cmd
        file_dir = os.path.dirname(file_path)
        opts_path = find_opts(file_dir)

        if opts_path is not None:
            opts = read_opts(opts_path)
            root_dir = os.path.dirname(opts_path)
        else:
            opts = default_opts
            root_dir = file_dir

        output_dir = os.path.normpath(opts['output_dir'])
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(root_dir, output_dir)
        mkdir_p(output_dir)

        flags = to_flags(opts['options'])

        compiled = []
        in_files = importing_files(os.path.relpath(file_path, root_dir), root_dir)[0]

        for fname in in_files:
            in_file = os.path.join(root_dir, fname)
            out_file = os.path.join(root_dir, output_dir, os.path.splitext(fname)[0]+'.css')

            p = Popen([sass.path] + flags + [in_file, out_file], stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()

            compiled.append(fname)
            if err:
                print(err)
                sublime.error_message("Failed to compile {0}\n\nView error with Ctrl+`".format(fname))
                return

        sublime.message_dialog("Compiled: {0}".format(",".join(compiled)))
        return
