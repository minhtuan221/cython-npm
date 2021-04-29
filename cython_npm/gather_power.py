import os
from pathlib import Path
from typing import List, Iterable

from os import listdir
from os.path import isfile, join


def list_file_in_dir(mypath: str) -> List[str]:
    x = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return [i for i in x if i.endswith('.py')]


def get_dir_from_file(file_path: str):
    if os.path.exists(file_path):
        if os.path.isdir(file_path):
            return file_path
        return os.path.split(file_path)[0]
    raise ValueError('File or folder path is not exist')


def isfile_casesensitive(path):
    if not os.path.isfile(path): 
        return False   # exit early
    directory, filename = os.path.split(path)
    return filename in os.listdir(directory)


def list_file_by_glob(path_pattern, suffix='*.py'):
    res = []
    if os.path.isfile(path_pattern):
        return [str(Path(path_pattern).absolute())]
    for path in Path(path_pattern).glob(suffix):
        res.append(str(path.absolute()))
    return res


def read_python_file(file_path, suffix='*.py'):
    with open(file_path, "r") as f:
        data = f.read().splitlines()
    return data


def get_module_name(path_str: str):
    x = path_str.split('/')
    res = x[-1]
    if res.endswith('.py'):
        res = res[:-3]
    return res


class Importee(object):

    def __init__(self, import_path, name, mode='function', children: str = '', new_name='', delimiter='    ', level=0, init_file=False, base_path='./', import_level=0):
        self.path = import_path
        if mode not in ['function', 'file', 'folder']:
            raise ValueError('wrong mode type')
        self.mode = mode
        self.name = name
        self.children = children
        self.new_name = new_name
        self.delimiter = delimiter
        self.level = level
        self.import_level = import_level
        self.is_init_file = init_file
        self.base_path = base_path

    def is_file(self):
        if self.mode == 'file':
            return True
        return False

    def is_function(self):
        if self.mode == 'function':
            return True
        return False

    def set_class_code(self, name: str=''):
        if not name:
            name = self.name
        return [f"class {name}:", f"{self.delimiter}pass"]

    def set_var_attribute(self, dict_attr: str, var_name: str):
        return f"[setattr({var_name}, k, v) for k,v in {dict_attr}.items()]"

    def key(self):
        return f"{self.path}"
    
    def set_children_file(self):
        res = []
        if self.mode == 'folder':
            if self.path.endswith('__init__.py'):
                p = self.path.replace('__init__.py', '')
                files = list_file_in_dir(p)
                for f in files:
                    abs_f = p + f
                    n = get_module_name(abs_f)                
                    if n == self.children:
                        res.append(f"{self.get_space_level()}__global_import_path['{self.path}'].{n} = __global_import_path['{abs_f}']")
        return res
    
    def set_abs_import_path(self, name:str):
        return f"__global_import_path['{self.path}'] = {name}"

    def children_to_code(self):
        res = []
        if self.mode == 'function':
            if self.new_name:
                res.append(f"{self.get_space_level()}{self.new_name} = __global_import_path['{self.path}'].{self.children}")
            else:
                res.append(f"{self.get_space_level()}{self.children} = __global_import_path['{self.path}'].{self.children}")
        elif self.mode == 'file':
            if self.new_name:
                res.append(f"{self.get_space_level()}{self.new_name} = __global_import_path['{self.path}']")
            else:
                if not self.is_init_file:
                    res.append(f"{self.get_space_level()}{self.children} = __global_import_path['{self.path}']")
                else:
                    res.append(f"{self.get_space_level()}{self.children} = __global_import_path['{self.path}'].{self.children}")
        elif self.mode == 'folder':
            res.append(f"{self.get_space_level()}{self.children} = __global_import_path['{self.path}']")
        return res
    
    def get_space_level(self):
        if self.level > 0:
            return self.delimiter * self.level
        else:
            return ''

    @staticmethod
    def get_import_name(name=''):
        # f"load__import__{name}()"
        return f"__load_import__{name}()"

    def file_as_code(self, code_lines: List[str], name=''):
        if not name:
            name = self.name
        # m = f"def load__import__{name}():"
        m = f"def {self.get_import_name(name)}:"
        new_codes = [self.delimiter + c for c in code_lines]
        new_codes.insert(0, m)
        new_codes.append(self.delimiter + 'return locals()')
        # load_local
        new_codes.extend(self.set_class_code(name))
        new_codes.append(self.set_var_attribute(self.get_import_name(name), name))
        new_codes.append(self.set_abs_import_path(name))        
        new_codes.extend(self.set_children_file())
        codes = [self.get_space_level()+c for c in new_codes]
        return codes


def convert_import_to_path(code: str, prefix: str = './', delimiter='    ', level=0) -> List[Importee]:
    """return [] if not import path
    return List[str] with import path
    """
    lv = 0
    if code.startswith(delimiter):
        lv = 1
    elif code.startswith(delimiter*2):
        lv = 2
    impl = max(level, lv)
    char_list = [c for c in code.split(' ') if c != '']
    if len(char_list) == 0:
        return []
    import_list = []
    pre_path = ''
    # check level 1 import statement
    if char_list[0] == 'from' or char_list[0] == 'import':
        # check if fullpath or relative path import
        if char_list[1].startswith('...'):
            p = os.path.dirname(prefix)
            pre_path = os.path.dirname(p)
        elif char_list[1].startswith('..'):
            pre_path = os.path.dirname(prefix)
        elif char_list[1].startswith('.'):
            pre_path = prefix

        # check if: import path...
        if char_list[0] == 'import':
            # char_list[3:] can contain only one module
            base_path = pre_path + char_list[1].replace('.', '/').replace('//', '/').replace('///', '/')
            path_str = f"{base_path}.py"
            if os.path.exists(path_str):
                module_name = get_module_name(base_path)
                # check if import a file
                if isfile_casesensitive(path_str):
                    import_list.append(Importee(path_str, module_name, level=lv, base_path='', import_level=impl))
                elif os.path.isdir(path_str):
                    # check if import a dir
                    import_list.append(Importee(path_str + '/__init__.py', module_name, level=lv, import_level=impl))
            return import_list

        # check the case: from path import something as ...
        if char_list[0] == 'from' and char_list[2] == 'import':
            # char_list[3:] may contain multiple module
            base_path = pre_path + char_list[1].replace('.', '/')
            x = ' '.join(char_list[3:])
            im_l = [i.strip() for i in x.split(',')]
            for module in im_l:                
                # check if it use "(" and ")" in import statement such as from xxx import (x1, x2, x3)
                module = module.replace('(', '')
                module = module.replace(')', '')
                if module == '*':
                    raise ValueError('Do not support import * statement in: '+code)
                # check if base_path is a file:
                # => check if base_path.py import ....
                path_str = f"{base_path}.py"
                if os.path.exists(path_str) and isfile_casesensitive(path_str):
                    # check if: from ...base_path import ...module as new_name
                    module_name = get_module_name(base_path)
                    # check if: from ...base_path import ...module as new_name
                    if ' ' in module:
                        if 'as' in module:
                            m = module.split(' ')
                            import_list.append(Importee(path_str, name=module_name, children=m[0], new_name=m[2], level=lv, import_level=impl))
                            continue
                    else:
                        import_list.append(Importee(path_str, name=module_name, children=module, level=lv, import_level=impl))
                        continue
                
                # check if base_path is a dir:
                # => check if import file (file.py)
                # => check if import function (__init__.py)
                if os.path.exists(base_path) and os.path.isdir(base_path):
                    
                    # check if base_path/module is a folder
                    p = f"{base_path}/{module}"
                    if os.path.exists(p) and os.path.isdir(p):
                        # check if module is a folder also: from folder import folder
                        path_str = f"{base_path}/{module}/__init__.py"
                        if os.path.exists(path_str) and isfile_casesensitive(path_str):                        
                            import_list.append(Importee(path_str, name=module, mode='folder', children=module, level=lv, import_level=impl))
                            continue                             
                    
                    # check if module is a file: from folder import file as new_name
                    if 'as' in module:
                        m = module.split(' ')
                        path_str = f"{base_path}/{m[0]}.py"
                        if os.path.exists(path_str) and isfile_casesensitive(path_str):
                            import_list.append(Importee(path_str, name=m[0], mode='file', new_name=m[2], level=lv, import_level=impl))
                            continue
                    else:
                        # check if module is a file: from folder import file
                        path_str = f"{base_path}/{module}.py"
                        if os.path.exists(path_str) and isfile_casesensitive(path_str):
                            import_list.append(Importee(path_str, name=module, mode='file', level=lv, children=module, import_level=impl))
                            continue
                    
                    # check if: from folder import function
                    path_str = f"{base_path}/__init__.py"
                    module_name = get_module_name(base_path)
                    if os.path.exists(path_str) and isfile_casesensitive(path_str):
                        import_list.append(Importee(path_str, name=module_name, mode='file', children=module, level=lv, init_file=True, import_level=impl))
                        # continue
                    
            return import_list
    else:
        return import_list


class Collector(object):

    def __init__(self, delimiter='    ', tab2space='    '):
        self.delimiter = delimiter
        self.tab2space = tab2space
        self.imported_list = set()
        self.imported_list_lv1 = set()
        self.imported_code_lv1 = set()
    
    def convert_to_base_import_code(self, code: Iterable[str]):
        res = []
        for line in code:
            res.append(line.replace(self.delimiter, '', 1))
        res.sort()
        return res

    def gather_all(self, path):
        res = []
        path = os.path.abspath(path)
        # check file or path:
        if os.path.isfile(path):
            data = read_python_file(path)
            data.insert(0, '__global_import_path = dict()')
            # gather all import level 1
            res = self.gather_file(data)
            code = self.convert_to_base_import_code(self.imported_code_lv1)
            self.imported_list_lv1 = set()  # clear impost list
            res2 = self.gather_file(code)
            res.extend(res2)
            return res
        return []

    def gather_file(self, code_lines: List[str], base_folder='./', level=0):
        collection = []
        is_main_function = False
        is_comment = False
        is_continue_line = False
        last_code_line = ''
        for code in code_lines:
            # convert to easier code
            code = code.replace('\t', self.tab2space)  # replace tab by space

            c = code.strip()
            # check if blank line or comment line
            if c == '' or c.startswith('#'):
                continue

            # check if continue line => must merge with the last line
            if is_continue_line and last_code_line != '':
                code = last_code_line + c
                is_continue_line = False
                last_code_line = ''

            # check if ' \' at the end of line => mean continue line:
            if c.endswith('\\'):
                is_continue_line = True
                last_code_line = code[:-1]  # remove last 1 char
                continue

            # ignore main function or the app will raise error
            if not code.startswith(self.delimiter):
                if code.count('"__main__"') > 0 or code.count("'__main__'") > 0:
                    a = code.split(' ')
                    a = ' '.join(a)
                    if a.startswith("if __name__ == '__main__':") or a.startswith('if __name__ == "__main__":'):
                        is_main_function = True
                        continue
                else:
                    is_main_function = False
            else:
                if is_main_function:
                    continue

            # ignore ''' and """ text or the app will raise error
            if code.count('"""')%2 == 1 or code.count("'''")%2==1:
                is_comment = not is_comment
                # print('#', code, is_comment)

            # check if it is a import statement or not
            if is_comment:
                is_import = ''
            else:
                is_import = convert_import_to_path(code, delimiter=self.delimiter, prefix=base_folder, level=level)
            if len(is_import) != 0:
                for imp in is_import:
                    if os.path.exists(imp.path):
                        if os.path.isfile(imp.path):
                            if imp.key() not in self.imported_list:
                                if imp.import_level == 0 and level == 0:
                                    self.imported_list.add(imp.key())
                                    data = read_python_file(imp.path)
                                    d = self.gather_file(data, get_dir_from_file(imp.path), level=0)
                                    d2 = imp.file_as_code(d)         
                                    d2.insert(0, f"# {code}")                     
                                    collection.extend(d2)
                                    print('# import file: ', len(self.imported_list), len(self.imported_list_lv1))
                                else:
                                    self.imported_code_lv1.add(code)
                            d = imp.children_to_code()
                            collection.extend(d)
            else:
                # it is normal code
                collection.append(code)

        return collection


# testing session
# def create_log():
#     x = 100
#
#     def test1(parameter_list):
#         """
#         docstring
#         """
#         print('test me')
#         print(x)
#
#     # y = test1(123344)
#
#     class test2:
#         def __init__(self, parameter_list):
#             """
#             docstring
#             """
#             print('test 2', parameter_list)
#
#     y = test2(13122)
#     print(locals())
#     locals()['test2']('verions2')
#     locals().update({'my_test': test1})
#     return locals()
#
#
# class log:
#     pass
#
#
# [setattr(log, k, v) for k, v in create_log().items()]
# log.test1(1212)
# log.y
# log.test2(1243124214)
# log.y
# print(log.__dict__)

if __name__ == "__main__":
    # test01 = ['from smart_trade.domain.model import BrokerInterface',
    # 'import smart_trade.pkgs.tools',
    # '   from smart_trade.domain.repository.magic_number import MagicNumber',
    # 'from smart_trade.infrastructure.protobuf.trading_client import TradingAPIClient',
    # 'def match_return(all_required, all_results):']
    # for test in test01:
    #     t1 = convert_import_to_path(test)
    #     print(t1)
    # c = Collector()
    # x = c.gather_file(['from app.pkgs import errors'])
    # for i in x:
    #     print(i)
    # print(os.path.exists('app/domain/model/Role.py'))
    # print(os.listdir('app/domain/model'))
    print('#-----------------------------------------------')
    # col = Collector()
    # x = col.gather_all('../qtrader.py')
    # for i in x:
    #     print(i)
