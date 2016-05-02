from os.path import join
from subl_mock import subl_patch
import sublime
from unittest import TestCase

class TestPathutils(TestCase):
    @subl_patch('libsass', 'pathutils')
    def test_subpaths(self, pathutils):
        path = join('/foo','bar','baz')
        exprmt = pathutils.subpaths(path)
        expect = [ join('/foo','bar','baz'), join('/foo','bar'), join('/foo'), join('/') ]
        self.assertEqual(exprmt, expect)

    @subl_patch('libsass', 'pathutils')
    def test_grep_r(self, pathutils):
        pathutils.os.walk = lambda x: [('/tmp','',['file.scss'])]

        self.assertEqual(pathutils.find_type_dirs('anything', '.scss'), ['/tmp'])
        self.assertEqual(pathutils.find_type_dirs('anything', ['.scss', '.sass']), ['/tmp'])
        self.assertEqual(pathutils.find_type_dirs('anything', '.sass'), [])
        self.assertEqual(pathutils.find_type_dirs('anything', ['.txt', '.csv']), [])
