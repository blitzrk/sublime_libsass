from os.path import join, realpath
import os
import sublime
import sys
from unittest import TestCase
from functools import wraps


def subl_patch(pkg, obj=None):
    def subl_deco(fn):
        @wraps(fn)
        def wrap(*args):
            wrap.pkg = pkg
            o = []
            if obj != None:
                o += [obj]
                wrap.pkg += '.' + obj
            try:
                mock = __import__(wrap.pkg, globals(), locals(), o, 0)
            except ImportError:
                wrap.pkg = realpath(__file__).split(os.sep)[-3] + '.' + wrap.pkg
                mock = __import__(wrap.pkg, globals(), locals(), o, 0)
            args += (mock,)
            fn(*args)
        return wrap
    return subl_deco


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
