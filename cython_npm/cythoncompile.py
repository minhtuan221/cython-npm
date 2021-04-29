import subprocess as cmd
import os
import sys
from importlib import reload
import traceback
import glob
import re
from typing import List
from pathlib import Path

def list_file_by_glob(path_pattern, suffix='*.py'):
    res = []
    if os.path.isfile(path_pattern):
        return [str(Path(path_pattern).absolute())]
    for path in Path(path_pattern).glob(suffix):
        res.append(str(path.absolute()))
    return res

# list_file_by_glob('./smart_trade/pkgs/signalr', '**/order.py')

def is_included(word: str, include: List[str]=[]):
    for p in include:
        if '*' not in p and p == word:
            return True
        elif p.startswith('*') or p.endswith('*'):
            x = p.replace("*","").replace("./","/")
            if x in word:
                return True
        # elif p.endswith('*'):
        #     x = p.replace("*","").replace("./","/")
        #     if word.startswith(x):
        #         return True
        # elif p.startswith('*'):
        #     x = p.replace("*","").replace("./","/")
        #     if word.endswith(x):
        #         return True
    return False

def write_setup_file(listfile, name=None):
    if not os.path.exists('build'):
        os.makedirs('build')
    onefile = open('build/setup.py', "w")
    onefile.write('from distutils.core import setup \n')
    onefile.write('from Cython.Build import cythonize \n')
    list_modules = []
    for anyfile in listfile:
        if type(anyfile) is not str:
            raise TypeError
        # if anyfile.endswith('__init__.py'):
        #     continue
        list_modules.append(f"'{anyfile}'")
    onefile.write(f"modules = [{','.join(list_modules)}] \n")
    l = f"language_level='{str(sys.version_info[0])}'"
    onefile.write("setup(ext_modules=cythonize(%s, %s, compiler_directives={'annotation_typing': False})) \n" % ('modules', l))
    onefile.close()


def write_init_file(listfile, path, name: str):
    file_path = os.path.abspath(os.path.join(path, name))
    if not os.path.exists(file_path+'/__init__.py'):
        onefile = open(file_path+'/__init__.py', "w")
        # print(listfile,file_path)
        name = name.replace('./', '').replace("/", ".")
        for anyfile in listfile:
            if type(anyfile) is not str:
                raise TypeError
            _head, tail = os.path.split(anyfile)
            onefile.write(
                'from {} import {} \n'.format(name, tail[:-4]))
        onefile.close()


def ccompile(path=None, name=None):
    if path is None:
        if name:
            cmd.call(
                'python build/setup.py build_ext --inplace –name {}'.format(name), shell=True)
        else:
            cmd.call(
                'python build/setup.py build_ext --inplace', shell=True)
    else:
        cmd.call(
            'python build/setup.py build_ext --build-lib "{}"'.format(path), shell=True)


def list_file_in_folder(file_path, suffix='.pyx', include=[], exclude=[]):
    list_file = []
    for file in os.listdir(file_path):
        if not os.path.isdir(file) and file.endswith(suffix):
            list_file.append(os.path.join(file_path, file))
        if os.path.isdir(os.path.join(file_path, file)) and not file.endswith('__pycache__'):
            folder_path = os.path.abspath(os.path.join(file_path, file))
            # print(folder_path)
            list_file.extend(list_file_in_folder(folder_path, suffix=suffix, exclude=exclude))
    return list_file

def find_all_import_in_python_file(file_path):
    res = []
    with open(file_path, "r") as f:
        data = f.read().splitlines()
        for row in data:
            if row.startswith('from ') or row.startswith('import ') or row.startswith('    from ') or row.startswith('    import '):
                res.append(row)
    return res

def find_import_statement(path, suffix='.pyx', exclude=[]):
    # check if file or directory exist
    if not os.path.exists(path):
        raise ValueError('File or path not exist error:' + path)
    # Get directory of modules need to compile:
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    # __file__ will get the current cythoncompile path
    file_path = os.path.abspath(os.path.join(basedir, path))
    exclude_paths = []
    files = []
    list_import = set()
    for p in exclude:
        exclude_paths.extend(list_file_by_glob(p, suffix=suffix))
    if os.path.isdir(file_path):
        # loop over all file
        raw_files = list_file_by_glob(file_path, suffix=suffix)
        for f in raw_files:
            if f not in exclude_paths:
                f = f.replace("\\", "/")
                files.append(f) # for window path
        for f in files:
            d = find_all_import_in_python_file(f)
            list_import.update(d)
        res = list(list_import)
        res.sort(reverse=True)
        return res
    else:
        d = find_all_import_in_python_file(file_path)
        d.sort(reverse=True)
        return d

def remove_redundant_c_file(list_file: List[str]):
    new_list = []
    for f in list_file:
        if f.endswith('.py'):
            x = f[:-3] + '.c'
        elif f.endswith('.pyx'):
            x = f[:-4] + '.c'
        else:
            x, _ = f.split('.')
            x = x + '.c'
        new_list.append(x)
    for f in new_list:
        if os.path.exists(f) and os.path.isfile(f):
            os.remove(f)
            print('remove redundant file', f)
        else:
            print('file not exists', f)

def is_match_pattern(word, pattern=[]):
    if len(pattern)==0:
        return True
    for p in pattern:
        if re.search(p, word):
            return True
    return False


def build_one(src_dirs: List[str], onefile: str, root=None, ext='.py', outfile_ext='.pyx'):
    convert_one_file(src_dirs, onefile)
    export(onefile, root=root, suffix=outfile_ext)


def convert_one_file(src_dirs: List[str], onefile: str, ext='.py'):
    includesContents = ""
    for src_dir in src_dirs:
        files = []
        # Get directory of modules need to compile:
        basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
        # __file__ will get the current cythoncompile path
        file_path = os.path.abspath(os.path.join(basedir, src_dir))
        # print(file_path)
        # check if file or directory exist
        if not os.path.exists(file_path):
            print('File path error:', file_path)
            raise ValueError(
                'Cannot compile this directory or file. It is not exist')

        # check if it is a .pyx file
        if os.path.isdir(src_dir):
            if file_path == sys.argv[0]:
                print('File path error:', file_path)
                raise ValueError('Cannot compile this directory or file')
            files = list_file_in_folder(file_path, suffix=ext, exclude=[])

        for f in files:
            if f.endswith(ext):
                f = f.replace('\\','/')
                includesContents += f'include "{f}" \n'

    includesFile = open(onefile, "w")
    includesFile.write(includesContents)
    includesFile.close()


def export(path, name=None, root=None, remove_redundant=True, suffix='.pyx', exclude=[], view_only=False):
    """Compile cython file (.pyx) into .so C-share file which can import and run in cpython as normal python package

    Arguments:
        path {str} -- Relative or absolute path of file or folder for import

    Keyword Arguments:
        root {[str]} -- is a Folder relative or absolute path. If not None, it will export to the folder as specified in root (default: {None})

    Raises:
        ValueError -- [description]
        ValueError -- [description]

    Returns:
        [type] -- [description]
    """

    files = []
    # Get directory of modules need to compile:
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    # __file__ will get the current cythoncompile path
    file_path = os.path.abspath(os.path.join(basedir, path))
    # print(file_path)
    exclude_paths = []
    for p in exclude:
        exclude_paths.extend(list_file_by_glob(p, suffix=suffix))
    # print(exclude_paths)
    # check if file or directory exist
    if not os.path.exists(file_path):
        print('File path error:', file_path)
        raise ValueError(
            'Cannot compile this directory or file. It is not exist')

    # check if it is a .pyx file
    if os.path.isdir(path):
        if file_path == sys.argv[0]:
            print('File path error:', file_path)
            raise ValueError('Cannot compile this directory or file')
        raw_files = list_file_by_glob(file_path, suffix=suffix)
        # we should exclude '__init__.py' file due to this problem https://github.com/cython/cython/issues/2968
        # update to version cython >3.0a5 may fix the problem
        files = []
        for f in raw_files:
            if f not in exclude_paths: # exclude this refer to https://github.com/cython/cython/issues/2968
                f = f.replace("\\", "/")
                files.append(f) # for window path
                print('compile file', f)
            # else:
            #     print('exclude file', f)
        if view_only:
            return
        write_setup_file(files, name=name)
        # must be basedir because setup code will create a folder name as path
        if root is not None:
            basedir = os.path.abspath(os.path.join(basedir, root))
            file_path = os.path.abspath(os.path.join(basedir, path))
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            ccompile(path=basedir, name=name)
        else:
            ccompile(path=basedir, name=name)
    else:
        files.append(path)
        write_setup_file(files, name=name)
        if root is not None:
            basedir = os.path.abspath(os.path.join(basedir, root))
            ccompile(path=basedir, name=name)
        else:
            ccompile(name=name)
    # remove *.c file => this is redundant product
    if remove_redundant:
        remove_redundant_c_file(files)
    return files


def install(listpath):
    allpath = []
    for path in listpath:
        files = export(path)
        allpath.append(files)
    return allpath


def import_path(fullpath, recompile=True):
    """ 
    Import a file with full path specification. Allows one to
    import from anywhere, something __import__ does not do. 
    """
    path, filename = os.path.split(fullpath)
    filename, _ext = os.path.splitext(filename)
    sys.path.append(path)
    module = __import__(filename)
    if recompile:
        reload(module)  # Might be already compile
    del sys.path[-1]
    return module


def require(relative_path, recompile=True):
    """Return a python module which is similar to require in nodejs

    Arguments:
        relative_path {str} -- Relative or absolute path of file or folder for import

    Keyword Arguments:
        recompile {bool} -- [description] (default: {True})

    Raises:
        ValueError -- [description]
    """

    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    file_path = os.path.abspath(os.path.join(basedir, relative_path))
    try:
        module = import_path(file_path, recompile=recompile)
    except:
        traceback.print_exc()
        print(file_path)
        raise ImportError('Error when importing path')
    return module


def requirepyx(relative_path, recompile=False):
    """Return a cython module (.pyx) which is similar to require in nodejs. This action also export the module before import.

    Arguments:
        relative_path {str} -- Relative or absolute path of file or folder for import

    Keyword Arguments:
        recompile {bool} -- [description] (default: {True})

    Raises:
        ValueError -- [description]
    """
    export(relative_path)
    module = require(relative_path, recompile=recompile)
    return module


def install_global(listpath, root='/usr/bin/cython_modules'):
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    file_path = os.path.abspath(os.path.join(basedir, root))
    for path in listpath:
        files = export(path, root=root)
        if os.path.isdir(path):
            write_init_file(files, file_path, path)
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
