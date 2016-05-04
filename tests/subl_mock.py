from functools import wraps
import os
from sublime import version

def subl_import(pkg, obj=''):
    repo = os.path.realpath(__file__).split(os.sep)[-3]
    o = [obj] if obj != '' else []
    p = pkg if version() < '3000' else repo+'.'+pkg
    imp = __import__(p, None, None, o)
    return getattr(imp, obj, imp)


def subl_patch(pkg, obj=''):
    def subl_deco(fn):
        @wraps(fn)
        def wrap(*args):
            mock = subl_import(pkg, obj)
            args += (mock,)
            fn(*args)
        return wrap
    return subl_deco
