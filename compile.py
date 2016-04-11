import sublime
import sublime_plugin
import os
import threading

try:
    from . import libsass
except ValueError:
    import libsass

compile = libsass.compile
deps = libsass.deps
pathutils = libsass.pathutils
project = libsass.project


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

    # Not yet implemented
    # config['compile']['load-path'] = loadpath + frameworks
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
        sublime.error_message(u"Unknown output structure: {0}".format(struct))
        return


class CompileSassCommand(sublime_plugin.WindowCommand):
    '''
    WindowCommand `compile_sass` to compile Sass asset and assets importing it
    For use in a build system
    '''

    def run(self, **build):
        file_path = build['cmd'] # Only certain keys have values expanded, such as cmd
        thread = CompileThread(file_path, self.callback(file_path))
        thread.start()
        return

    def callback(self, file_path):
        # All this to mock currying
        def cb1(compiled):
            def cb2():
                if compiled:
                    self._set_status(u"Compiled: {0}".format(",".join(compiled)))
                else:
                    self._set_status(u"Error: {0}".format(os.path.basename(file_path)))
            return cb2
        return cb1

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


class CompileThread(threading.Thread):
    ''' Compile off the main thread. Only uses sublime.set_timeout for ST2 compatibility'''

    def __init__(self, file, callback):
        threading.Thread.__init__(self)
        self.file = file
        self.callback = callback
        self.config = project.config_for(file)
        return

    def run(self):
        compiled = compile_deps(self.file, self.config)
        sublime.set_timeout(self.callback(compiled), 1)
        return
