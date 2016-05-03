from functools import wraps
import os
from sublime import version

def subl_patch(pkg, obj=''):
    def subl_deco(fn):
        @wraps(fn)
        def wrap(*args):
            repo = os.path.realpath(__file__).split(os.sep)[-3]
            wrap.obj = [obj] if obj != '' else []
            wrap.pkg = pkg if version() < '3000' else repo+'.'+pkg
            mock = __import__(wrap.pkg, None, None, wrap.obj)
            mock = getattr(mock, obj, mock)
            args += (mock,)
            fn(*args)
        return wrap
    return subl_deco
