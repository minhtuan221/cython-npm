# Add this line to the beginning of relative.py file
import sys
sys.path.append('..')
from cython_modules.cypm import require
b = require('./build_example')
b.hello.Hello()
