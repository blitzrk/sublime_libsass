import sublime
import sublime_plugin

import json
import sass
from subprocess import PIPE, Popen
from .pathutils import *

default_opts = {
    "output_dir": "build/css",
    "options": {
        "line-comments": True,
        "line-numbers":  True,
        "style":         "nested"
    }
}


def find_opts(top):
    for path in subpaths(top):
        file = os.path.join(path, '.libsass.json')
        if os.path.isfile(file):
            return file


def read_opts(file):
    with open(file, 'r') as f:
        user_opts = json.load(f)

    opts = default_opts
    opts.update(user_opts)
    return opts


def to_flags(options):
    flags = []
    for key, value in options.items():
        if value is True:
            flags.append('--{0}'.format(key))
        elif value is not False:
            flags.append('--{0}={1}'.format(key, value))
    return flags


def is_partial(path):
    return os.path.basename(path).startswith('_')


def partial_import_name(path):
    return os.path.splitext(os.path.basename(path))[0][1:]


class CompileSassCommand(sublime_plugin.WindowCommand):
    def run(self, **build):
        file_path = build['cmd'] # Only select keys have values expanded, hence the bad name
        file_dir = os.path.dirname(file_path)
        opts_path = find_opts(file_dir)

        if opts_path is not None:
            opts = read_opts(opts_path)
            root_dir = os.path.dirname(opts_path)
        else:
            opts = default_opts
            root_dir = file_dir

        flags = to_flags(opts['options'])

        compiled = []
        in_files = []

        if is_partial(file_path):
            in_files += grep_r("@import.*{0}".format(partial_import_name(file_path)), root_dir)
        else:
            in_files.append(os.path.relpath(file_path, root_dir))

        for fname in in_files:
            in_file = os.path.join(root_dir, fname)
            out_file = os.path.join(root_dir, opts['output_dir'], os.path.splitext(fname)[0]+'.css')

            p = Popen([sass.path] + flags + [in_file, out_file], stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()

            out_short = os.path.basename(out_file)
            compiled.append(out_short)
            if err:
                print(err)
                sublime.error_message("Failed to compile {0}\nView with Ctrl+`".format(out_short))
                return

        sublime.message_dialog("Compiled: {0}".format(",".join(compiled)))
