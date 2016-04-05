import sublime

import os
from .pathutils import mkdir_p
import sass
import stat
from subprocess import PIPE, Popen


# Guarantee sassc is executable
if not os.access(sass.path, os.X_OK):
    mode = os.stat(sass.path).st_mode
    os.chmod(sass.path, mode | stat.S_IEXEC)


# Platform-specific subprocess options
if os.name == 'nt':
    _platform_opts = { 'creationflags': 0x00000008 }
else:
    _platform_opts = {}


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


def _compile(files, config, outfile_for):
    flags = to_flags(config['compile'])

    compiled = []
    for f in files:
        in_file  = os.path.join(config['root'], f)
        out_file = outfile_for(f)

        # Make sure output folder exists
        mkdir_p(os.path.dirname(out_file))

        command = [sass.path] + flags + [in_file, out_file]
        p = Popen(command, stdout=PIPE, stderr=PIPE, **_platform_opts)
        out, err = p.communicate()

        if err:
            print(u"Error: {0}".format(err))
            print(u"Command: {0}".format(" ".join(command)))
            sublime.error_message(u"Failed to compile {0}\n\nView error with Ctrl+`".format(f))
            return

        compiled.append(f)

    return compiled


def nested(files, config, rel=""):
    outroot = os.path.join(config['root'], config['output']['dir'])

    def outfile_for(infile):
        if rel and infile.startswith(os.path.normpath(rel)):
            infile = infile[len(rel)+1:]
        outname = os.path.splitext(infile)[0]+'.css'
        return os.path.join(outroot, outname)

    return _compile(files, config, outfile_for)


def flat(files, config):
    outroot = os.path.join(config['root'], config['output']['dir'])

    def outfile_for(infile):
        outname = os.path.basename(os.path.splitext(infile)[0]+'.css')
        return os.path.join(outroot, outname)

    return _compile(files, config, outfile_for)
