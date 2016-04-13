from os.path import join
import sublime
import sys
from unittest import TestCase
from unittest.mock import patch

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

    @patch('pathutils.os')
    def test_grep_r(self, mock_os):
        mock_os.walk = lambda x: [('/tmp','',['file.scss'])]

        self.assertEqual(pathutils.find_type_dirs('anything', '.scss'), ['/tmp'])
        self.assertEqual(pathutils.find_type_dirs('anything', ['.scss', '.sass']), ['/tmp'])
        self.assertEqual(pathutils.find_type_dirs('anything', '.sass'), [])
        self.assertEqual(pathutils.find_type_dirs('anything', ['.txt', '.csv']), [])
