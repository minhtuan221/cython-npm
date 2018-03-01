import subprocess as cmd
import os


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


def writeInitFile(listfile: list, path:str,name:str):
    file_path = os.path.abspath(os.path.join(path, name))
    # if not os.path.exists(file_path+'/__init__.py'):
    onefile = open(file_path+'/__init__.py', "w")
    # print(listfile,file_path)
    name = name.replace('./', '').replace("/", ".")
    for anyfile in listfile:
        if type(anyfile) is not str:
            raise TypeError
        head,tail = os.path.split(anyfile)
        onefile.write(
            'from {} import {} \n'.format(name,tail[:-4]))
    onefile.close()

def ccompile(path=None):
    if path is None:
        cmd.call('python cython_modules/setup.py build_ext --inplace', shell=True)
    else:
        cmd.call('python cython_modules/setup.py build_ext --build-lib {}'.format(path), shell=True)


def listFileinFolder(file_path: str):
    listFile=[]
    for file in os.listdir(file_path):
        if file.endswith(".pyx"):
            listFile.append(file_path+"/"+file)
    return listFile

def export(path:str, root=None):
    files = []
    # Get directory of modules need to compile:
    basedir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.abspath(os.path.join(basedir, path))
    # print(file_path)
    # check if file or directory exist
    if not os.path.exists(file_path):
        raise ValueError('Cannot compile this directory or file. It is not exist')
    
    # check if it is a .pyx file
    if not path.endswith(".pyx"):
        if file_path==__file__:
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


def install(listpath: list,root='./cython_modules'):
    basedir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.abspath(os.path.join(basedir, root))
    for path in listpath:
        files = export(path, root=root)
        if not path.endswith(".pyx"):
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
        name = path.replace('.pyx', '').replace('./','').replace('.', '').replace("/", ".")
        onefile.write("import {} as x; modules['{}'] = x \n".format(name, name))
    onefile.write("def require(modulesName: str): \n ")
    onefile.write("   cython=modules[modulesName] \n ")
    onefile.write("   return cython \n ")
    onefile.close()

    
# python setup.py build_ext --inplace

