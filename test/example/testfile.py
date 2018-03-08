# Add this line to the beginning of relative.py file
import sys, os
# sys.path.append('..')
# from cython_modules.cypm import require
# b = require('./build_example')
# b.hello.Hello()
from importlib import reload
from cython_npm.cythoncompile import require

def import_path(fullpath, recompile=False):
    """ 
    Import a file with full path specification. Allows one to
    import from anywhere, something __import__ does not do. 
    """
    path, filename = os.path.split(fullpath)
    filename, ext = os.path.splitext(filename)
    sys.path.append(path)
    module = __import__(filename)
    if recompile:
        reload(module)  # Might be out of date
    del sys.path[-1]
    return module

# here = import_path(
#     '/Users/minhtuannguyen/MyWorking/Privates/cython/cython-npm/test/here')
h = require('./')
h.hello.Hello()
h.secondapp.goodbye()
