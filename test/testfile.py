from cythoncompile import writeSetupFile, ccompile, export
# writeSetupFile(['test_Carray.pyx'])
# ccompile()
# import os
# for file in os.listdir("Test_cython"):
#     if file.endswith(".pyx"):
#         print(os.path.join("Test_cython", file))

# require('./build_example')
# from build_example import hello, secondapp
# hello.Hello()
# secondapp.goodbye()
# require('here.pyx')
# from here import here
# here()
# require('./build_example')
# require('./build_example/level2')
# require('here.pyx')
# from build_example.level2 import Third
# Third.three()

# This below is not recommended
# import pyximport
# pyximport.install()
# from build_example import secondapp
# from build_example.level2 import Third
# secondapp.goodbye()
# Third.three()
# export('here.pyx')
from cython_modules.cypm import require
a = require('here')
a.here()

b = require('build_example')
b.hello.Hello()
# export('./build_example/level2')
# b = require('build_example')
# import build_example as x
# x.secondapp.goodbye()

