from cython_npm.cythoncompile import export
import os
import sys
from importlib import reload

def require(path: str):
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    file_path = os.path.abspath(os.path.join(basedir, path))
    x = 0
    return x


def weirdimport(fullpath):
    global project
    import os
    import sys
    sys.path.append(os.path.dirname(fullpath))
    try:
        project = __import__(os.path.basename(fullpath))
        sys.modules['project'] = project
    finally:
        del sys.path[-1]


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




