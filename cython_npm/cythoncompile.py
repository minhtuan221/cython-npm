import subprocess as cmd
import os
import sys
from importlib import reload


def hello():
    print('import successfully')


def writeSetupFile(listfile: list, path='cython_modules'):
    if not os.path.exists('cython_modules'):
        os.makedirs('cython_modules')
    onefile = open('cython_modules/setup.py', "w")
    onefile.write('from distutils.core import setup \n')
    onefile.write('from Cython.Build import cythonize \n')
    for anyfile in listfile:
        if type(anyfile) is not str:
            raise TypeError
        onefile.write('setup(ext_modules=cythonize("{}")) \n'.format(anyfile))
    onefile.close()


def writeInitFile(listfile: list, path: str, name: str):
    file_path = os.path.abspath(os.path.join(path, name))
    if not os.path.exists(file_path+'/__init__.py'):
        onefile = open(file_path+'/__init__.py', "w")
        # print(listfile,file_path)
        name = name.replace('./', '').replace("/", ".")
        for anyfile in listfile:
            if type(anyfile) is not str:
                raise TypeError
            head, tail = os.path.split(anyfile)
            onefile.write(
                'from {} import {} \n'.format(name, tail[:-4]))
        onefile.close()


def ccompile(path=None):
    if path is None:
        cmd.call('python cython_modules/setup.py build_ext --inplace', shell=True)
    else:
        cmd.call(
            'python cython_modules/setup.py build_ext --build-lib {}'.format(path), shell=True)


def listFileinFolder(file_path: str):
    listFile = []
    for file in os.listdir(file_path):
        if file.endswith(".pyx"):
            listFile.append(file_path+"/"+file)
    return listFile


def export(path: str, root=None):
    files = []
    # Get directory of modules need to compile:
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    # __file__ will get the current cythoncompile path
    file_path = os.path.abspath(os.path.join(basedir, path))
    # print(file_path)
    # check if file or directory exist
    if not os.path.exists(file_path):
        raise ValueError(
            'Cannot compile this directory or file. It is not exist')

    # check if it is a .pyx file
    if os.path.isdir(path):
        if file_path == sys.argv[0]:
            raise ValueError('Cannot compile this directory or file')
        files = listFileinFolder(file_path)
        writeSetupFile(files)
        writeInitFile(files, basedir, path)
        # must be basedir because setup code will create a folder name as path
        if root is not None:
            basedir = os.path.abspath(os.path.join(basedir, root))
            file_path = os.path.abspath(os.path.join(basedir, path))
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            if not os.path.exists(file_path+'/__init__.py'):
                onefile = open(file_path+'/__init__.py', "w")
                onefile.close()
            # print(file_path)
            ccompile(path=basedir)
        else:
            ccompile(path=basedir)
    else:
        files.append(path)
        writeSetupFile(files)
        if root is not None:
            basedir = os.path.abspath(os.path.join(basedir, root))
            ccompile(path=basedir)
        else:
            ccompile()
    return files


def install(listpath: list):
    allpath = []
    for path in listpath:
        files = export(path)
        allpath.append(files)
    return allpath


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


def installGlobal(listpath: list, root='/usr/bin/cython_modules'):
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    file_path = os.path.abspath(os.path.join(basedir, root))
    for path in listpath:
        files = export(path, root=root)
        if os.path.isdir(path):
            writeInitFile(files, file_path, path)
    # writing install code
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    if not os.path.exists(file_path+'/__init__.py'):
        onefile = open(file_path+'/__init__.py', "w")
        onefile.close()
    onefile = open(file_path+'/cypm.py', "w")
    onefile.write("modules = dict() \n")
    for path in listpath:
        if os.path.isfile(path):
            path = path.replace('.pyx', '')
        name = path.replace('./', '').replace('.', '').replace("/", ".")
        onefile.write(
            "import {} as x; modules['{}'] = x \n".format(name, path))
    onefile.write("def require(modulesName: str): \n ")
    onefile.write("   cython=modules[modulesName] \n ")
    onefile.write("   return cython \n ")
    onefile.close()


# python setup.py build_ext --inplace
