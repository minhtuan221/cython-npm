## Speed test battle

### script for test

#### test pure python code
time python test_python.py
9999010000

real    0m12.825s
user    0m11.721s
sys     0m1.061s

#### test python with array in python
time python test_python_array.py
9999010000

real    0m16.674s
user    0m16.285s
sys     0m0.360s

#### test_cython.pyx with python list
time python run.py
9999010000

real    0m5.803s
user    0m4.496s
sys     0m1.211s

#### test_cythonlist.pyx with python list optimize x = [i for i in range(1000000)]
time python run.py
9999010000

real    0m4.378s
user    0m3.331s
sys     0m1.034s

#### test_cythonlist_cache.pyx with python list optimize and cache
time python run.py
9999010000

real    0m3.373s
user    0m2.360s
sys     0m1.001s

#### test_cythonarray.pyx with pre-sized array in C
time python run.py
9999010000

real    0m0.247s
user    0m0.182s
sys     0m0.043s

#### test_cythoncache.pyx with pre-sized array in C and cache
time python run.py
9999010000

real    0m0.085s
user    0m0.067s
sys     0m0.015s