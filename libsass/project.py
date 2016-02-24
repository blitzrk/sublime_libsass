import json
from .pathutils import subpaths
import os
import re
import sublime


def user_config():
    '''Get global config from Default/User Preferences.sublime-settings'''

    settings = sublime.load_settings("Libsass Build.sublime-settings")
    output = {'dir':'build/css', 'structure':'nested'}
    output.update(settings.get('output'))
    config = {
        'output': output,
        'compile': settings.get('compile')
    }

    if os.name == 'nt':
        config['output']['dir'] = config['output']['dir'].replace('/','\\')

    return config


def find_root(file):
    '''Find root dir based on config or best guess if no config'''

    config_path = find_config(file)
    if config_path:
        root = os.path.dirname(config_path)
    else:
        root = guess_root(file)
    return root


def guess_root(file):
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

    if not is_sass(file):
        sublime.error_message("Please save the file")

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
        singlequotebefore = re.compile(r"'(.*?)'\s*:")
        singlequoteafter = re.compile(r":\s*'(.*?)'")
        for line in f:
            line = re.sub(newline, "", line)
            line = re.sub(comment, "", line)
            line = re.sub(singlequotebefore, "\"\\1\":", line)
            line = re.sub(singlequoteafter, ":\"\\1\"", line)
            lines.append(line)

    return json.loads("".join(lines))


def splitpath(path):
    '''Splits path based on config (guessed root, config location, or load-path)'''

    root = find_root(path)
    rest = os.path.relpath(path, root)
    return (rest, root)


def config_for(path):
    '''Determine output path and flags for compiling file at `path`'''

    config = user_config()
    config_path = find_config(path)
    if config_path:
        proj_conf = read_config(config_path)
        proj_conf['output'] and config['output'].update(proj_conf['output'])
        proj_conf['compile'] and config['compile'].update(proj_conf['compile'])

    output_dir = os.path.normpath(config['output']['dir'])
    if not os.path.isabs(output_dir):
        root = find_root(path)
        output_dir = os.path.normpath(os.path.join(root, output_dir))
    config['output']['dir'] = output_dir

    return config
