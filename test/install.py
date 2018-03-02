from cython_npm.cythoncompile import install
Manymodules = [
    './example',
    './example/level2',
    'here.pyx'
]
install(Manymodules)
