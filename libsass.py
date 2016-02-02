import sublime
import sublime_plugin

from .pathutils import *

class CompileSassCommand(sublime_plugin.WindowCommand):
    def run(self, **build):
        sublime.message_dialog(str(build))
