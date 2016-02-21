import json
from .pathutils import subpaths, mkdir_p
import os
import re
import sublime


def settings():
    return sublime.load_settings("Libsass Build.sublime-settings")
	

def user_opts():
    '''Get global config from Default/User Preferences.sublime-settings'''

    s = settings()
    opts = {
        'output_dir': s.get('output_dir'),
        'options': s.get('options')
    }

    if os.name is 'nt':
        opts['output_dir'] = opts['output_dir'].replace('/','\\')

    return opts


def find_root(file):
    '''
    For projects without .libsass.json configs, search for the most distant
    parent directory that still has a .sass or .scss file
    '''

    def is_sass(file):
        ext = os.path.splitext(file)[1]
        return ext in ['.sass', '.scss']

    for i, path in enumerate(subpaths(file)):
        (_, _, files) = next(os.walk(path))
        if not any([is_sass(f) for f in files]):
            break

    assert is_sass(file)
    assert i > 0

    return subpaths(file)[i-1]


def find_config(top):
    '''Search up parent tree for libsass config file'''

    top = os.path.realpath(top)
    if not os.path.isdir(top):
        top = os.path.dirname(top)

    for path in subpaths(top):
        file = os.path.join(path, '.libsass.json')
        if os.path.isfile(file):
            return file


def read_config(file):
    '''
    Read json-formatted config file into map and fill missing values
    with defaults
    '''

    lines = []
    with open(file, 'r') as f:
        newline = re.compile(r'\r?\n$')
        comment = re.compile(r"//.*$")
        for line in f:
            line = re.sub(newline, "", line)
            line = re.sub(comment, "", line)
            lines.append(line)

    return json.loads("".join(lines))


def splitpath(path):
    opts_path = find_config(path)
    if opts_path:
        root = os.path.dirname(opts_path)
    else:
        root = find_root(path)
    rest = os.path.relpath(path, root)
    return (rest, root)


def to_flags(options):
    '''Convert map into list of standard flags'''

    flags = []
    for key, value in options.items():
        if value is True:
            flags.append('--{0}'.format(key))
        elif type(value) is list:
            for v in value:
                flags.append('--{0}={1}'.format(key, v))
        elif value is not False:
            flags.append('--{0}={1}'.format(key, value))
    return flags


def config_for(path):
    '''Determine output path and flags for compiling file at `path`'''

    opts = user_opts()
    config_path = find_config(path)

    if config_path:
        root = os.path.dirname(config_path)
        opts.update(read_config(config_path))
    else:
        root = find_root(path)

    output_dir = os.path.normpath(opts['output_dir'])
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(root, output_dir)

    # Make sure output folder exists
    mkdir_p(output_dir)

    flags = to_flags(opts['options'])

    return (output_dir, flags)
