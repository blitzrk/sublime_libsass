import sublime
import sublime_plugin

import os

try:
    libsass = __import__("libsass")
    compile = libsass.compile
    deps = libsass.deps
    pathutils = libsass.pathutils
    project = libsass.project
except ImportError:
    from .libsass import deps
    from .libsass import compile
    from .libsass import pathutils
    from .libsass import project


clears = {}


def autoload_frameworks(config):
    root = config['root']
    loadpath = config['compile']['load-path'] or []
    if type(loadpath) is str:
        loadpath = [ loadpath ]

    # Find possible frameworks
    frameworks = pathutils.find_type_dirs(root, ['.sass', '.scss'])
    print("Possible frameworks: ", frameworks)
    frameworks = [ p for p in frameworks if p not in pathutils.subpaths(config['file']) ]
    print("Without current project: ", frameworks)

    config['compile']['load-path'] = loadpath + frameworks
    return config


def compile_deps(path, config):
    files, root = deps.get(path)
    config['root'] = root
    config['file'] = path

    autoload_frameworks(config)

    struct = config["output"]["structure"]
    if not struct or struct == "nested":
        return compile.nested(files, config)
    elif type(struct) is list and len(struct) is 2 and struct[0] == "nested":
        return compile.nested(files, config, struct[1])
    elif struct == "flat":
        return compile.flat(files, config)
    else:
        sublime.error_message("Unknown output structure: {0}".format(struct))
        return


class CompileSassCommand(sublime_plugin.WindowCommand):
    '''
    WindowCommand `compile_sass` to compile Sass asset and assets importing it
    For use in a build system
    '''

    def run(self, **build):
        file_path = build['cmd'] # Only certain keys have values expanded, such as cmd
        config = project.config_for(file_path)
        compiled = compile_deps(file_path, config)
        if compiled:
            self._set_status("Compiled: {0}".format(",".join(compiled)))
        else:
            self._set_status("Error: {0}".format(os.path.basename(file_path)))
        return

    def _set_status(self, message):
        view = self.window.active_view()
        view.set_status('libsass', message)
        
        global clears
        id = view.id()
        clears[id] = clears.get(id, 0) + 1
        sublime.set_timeout(self._clear_status(view), 5000)
        return

    def _clear_status(self, view):
        def clear():
            id = view.id()

            global clears
            clears[id] -= 1
            if clears[id] == 0:
                view.set_status('libsass', '')
            return
        return clear
