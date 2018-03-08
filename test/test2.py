from cythoncompile import require, export

export('./example')
from example import hello
from example.level2 import Third
hello.Hello()
Third.three()

x = require('./example')
x.secondapp.goodbye()
y = require('./')
y
print(y)
