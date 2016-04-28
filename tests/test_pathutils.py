from os.path import join
import sublime
import sys
from unittest import TestCase

version = sublime.version()

try:
    from libsass import pathutils
except ImportError:
    from sublime_libsass.libsass import pathutils


class TestPathutils(TestCase):
    def test_subpaths(self):
        path = join('/foo','bar','baz')
        exprmt = pathutils.subpaths(path)
        expect = [ join('/foo','bar','baz'), join('/foo','bar'), join('/foo'), join('/') ]
        self.assertEqual(exprmt, expect)

    def test_grep_r(self):
        pathutils.os.walk = lambda x: [('/tmp','',['file.scss'])]

        self.assertEqual(pathutils.find_type_dirs('anything', '.scss'), ['/tmp'])
        self.assertEqual(pathutils.find_type_dirs('anything', ['.scss', '.sass']), ['/tmp'])
        self.assertEqual(pathutils.find_type_dirs('anything', '.sass'), [])
        self.assertEqual(pathutils.find_type_dirs('anything', ['.txt', '.csv']), [])
