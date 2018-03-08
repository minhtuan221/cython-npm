#!/usr/bin python
from functools import lru_cache

@lru_cache(maxsize=128)
def dotest():
    cdef long mysum = 0
    cdef int i
    cdef int e
    for e in range(30):
        mysum = 0
        x = [i for i in range(1000000)]

        y = [x[i] + x[i+1] for i in range(1000000-1)]

        i = 0
        for i in range(0, 1000000, 100):
            mysum += y[i]

    print(mysum)
dotest()