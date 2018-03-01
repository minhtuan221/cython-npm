from cython_npm.cythoncompile import install
Manymodules = [
    './build_example',
    './build_example/level2',
    'here.pyx'
]
install(Manymodules)
