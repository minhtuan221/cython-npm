# Add this line to the beginning of relative.py file
import sys, os
# sys.path.append('..')
# from cython_modules.cypm import require
# b = require('./build_example')
# b.hello.Hello()
from importlib import reload

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


def require(relative_path: str, recompile=False):
    if not os.path.isdir or not os.path.isfile:
        raise ValueError('require accept path only')
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    file_path = os.path.abspath(os.path.join(basedir, relative_path))
    try:
        module = import_path(file_path, recompile=recompile)
    except Exception as error:
        print(error)
        raise TypeError('Error when importing path')
    return module

# here = import_path(
#     '/Users/minhtuannguyen/MyWorking/Privates/cython/cython-npm/test/here')
here = require('../here')
here.Imhere()
