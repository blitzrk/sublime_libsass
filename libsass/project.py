import json
from libsass.pathutils import subpaths, mkdir_p
import os


default_opts = {
    "output_dir": "build/css",
    "options": {
        "line-comments": True,
        "line-numbers":  True,
        "style":         "nested"
    }
}


def find_config(top):
    '''Search up parent tree for libsass config file'''

    top = os.path.dirname(os.path.realpath(top))
    for path in subpaths(top):
        file = os.path.join(path, '.libsass.json')
        if os.path.isfile(file):
            return file


def read_config(file):
    '''
    Read json-formatted config file into map and fill missing values
    with defaults
    '''

    with open(file, 'r') as f:
        user_opts = json.load(f)

    opts = default_opts
    opts.update(user_opts)
    return opts


def splitpath(path):
    opts_path = find_config(path)
    root = os.path.dirname(opts_path or path)
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
                flags.append('--{0} {1}'.format(key, v))
        elif value is not False:
            flags.append('--{0} {1}'.format(key, value))
    return flags


def config_for(path):
    '''Determine output path and flags for compiling file at `path`'''

    opts_path = find_config(path)
    root = os.path.dirname(opts_path or path)
    opts = default_opts if opts_path is None else read_config(opts_path)

    output_dir = os.path.normpath(opts['output_dir'])
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(root, output_dir)

    # Make sure output folder exists
    mkdir_p(output_dir)

    flags = to_flags(opts['options'])

    return (output_dir, flags)
