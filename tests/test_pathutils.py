from os.path import join
import sublime
import sys
from unittest import TestCase

version = sublime.version()

if version < '3000':
    from libsass import pathutils
else:
    from sublime_libsass.libsass import pathutils


class test_pathutils(TestCase):
    def test_subpaths(self):
        path = join('/foo','bar','baz')
        exprmt = pathutils.subpaths(path)
        expect = [ join('/foo','bar','baz'), join('/foo','bar'), join('/foo'), join('/') ]
        self.assertEqual(exprmt, expect)
