import sublime
import sublime_plugin

import os
import sass
import stat
from subprocess import PIPE, Popen

# Make subpackages importable
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from libsass import deps
from libsass import project


# Guarantee sassc is executable
if not os.access(sass.path, os.X_OK):
    mode = os.stat(sass.path).st_mode
    os.chmod(sass.path, mode | stat.S_IEXEC)


def compile_deps(path, out_dir, flags):
    files, root = deps.get(path)

    compiled = []
    for f in files:
        in_file  = os.path.join(root, f)
        out_file = os.path.join(out_dir, os.path.splitext(f)[0]+'.css')

        p = Popen([sass.path] + flags + [in_file, out_file],
                stdout=PIPE, stderr=PIPE, creationflags=0x00000008)
        out, err = p.communicate()

        if err:
            print(err)
            sublime.error_message("Failed to compile {0}\n\nView error with Ctrl+`".format(f))
            return

        compiled.append(f)

    return compiled


class CompileSassCommand(sublime_plugin.WindowCommand):
    '''
    WindowCommand `compile_sass` to compile Sass asset and assets importing it
    For use in a build system
    '''

    def run(self, **build):
        file_path = build['cmd'] # Only certain keys have values expanded, such as cmd
        out_dir, flags = project.config_for(file_path)
        compiled = compile_deps(file_path, out_dir, flags)
        if compiled:
            sublime.message_dialog("Compiled: {0}".format(",".join(compiled)))
        return
