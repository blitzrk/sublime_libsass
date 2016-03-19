import sublime
import sublime_plugin

import os

try:
    from . import libsass
except ValueError:
    import libsass

project = libsass.project


example = r'''{{
    "output": {{
        "dir": "{0}",      // Relative or absolute path (can have ..)
        "structure": "nested"       // "flat", "nested", or ["nested", "relative/root/of/nest"]
    }},
    "compile": {{
        "style": false,             // String | Output style: nested/expanded/compact/compressed
        "line-numbers": false,      // Bool   | Emit comments showing original line numbers
        "line-comments": false,     // Bool   | Alias for line-numbers, does not override
        "load-path": false,         // List   | Sass import paths: e.g. [ "C:\\bourbon", "C:\\compass" ]
        "plugin-path": false,       // String | Path to autoload plugins (libsass issue 878)
        "sourcemap": false,         // Bool   | Emit .css.map file for debugging in browser
        "omit-map-comment": false,  // Bool   | Omit comment about .css.map file in .css file
        "precision": false          // Int    | Decimal places for computed values
    }}
}}'''.format(os.path.join('build','css').replace('\\',r'\\\\'))


class LibsassBuildConfigCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        view = window.active_view()
        folder = (window.folders() or [None])[0]

        if not folder:
            name = view.file_name()
            folder = os.path.dirname(name) if name else ""

        config = project.find_config(folder) if folder else None
        if config:
            window.open_file(config)
        else:
            new = window.new_file()
            new.settings().set('default_dir', folder)
            new.set_name('.libsass.json')
            new.run_command('insert_snippet', {'contents': example})
