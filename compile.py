import sublime
import sublime_plugin

import os
import sass
import stat
from subprocess import PIPE, Popen

# Make subpackages importable
try:
    from libsass import deps
    from libsass import project
except ImportError:
    from .libsass import deps
    from .libsass import project


# Guarantee sassc is executable
if not os.access(sass.path, os.X_OK):
    mode = os.stat(sass.path).st_mode
    os.chmod(sass.path, mode | stat.S_IEXEC)


# Platform-specific subprocess options
if os.name is 'nt':
    _platform_opts = { 'creationflags': 0x00000008 }
else:
    _platform_opts = {}


def compile_deps(path, out_dir, flags):
    files, root = deps.get(path)

    compiled = []
    for f in files:
        in_file  = os.path.join(root, f)
        out_file = os.path.join(out_dir, os.path.basename(os.path.splitext(f)[0]+'.css'))

        command = [sass.path] + flags + [in_file, out_file]
        p = Popen(command, stdout=PIPE, stderr=PIPE, **_platform_opts)
        out, err = p.communicate()

        if err:
            print(err)
            print("Command: {0}".format(command))
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
            self._set_status("Compiled: {0}".format(",".join(compiled)))
        return

    def _set_status(self, message):
        view = self.window.active_view()
        view.set_status('libsass', message)
        sublime.set_timeout(self._clear_status, 5000)
        return

    def _clear_status(self):
        self._set_status('')
        return
