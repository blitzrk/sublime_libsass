from functools import wraps
import os
from sublime import version

def subl_patch(pkg, obj=None):
    def subl_deco(fn):
        @wraps(fn)
        def wrap(*args):
            repo = os.path.realpath(__file__).split(os.sep)[-3]
            wrap.pkg = pkg if version() < '3000' else repo
            mock = __import__(wrap.pkg)
            if version() >= '3000':
                mock = getattr(mock, pkg)
            if obj is not None:
                mock = getattr(mock, obj)
            args += (mock,)
            fn(*args)
        return wrap
    return subl_deco
