#!/usr/bin python
from functools import lru_cache
@lru_cache(maxsize=128)
def dotest():
    cdef long mysum = 0
    cdef int i
    cdef int e
    cdef int x[1000000]
    cdef int y[1000000]
    for e in range(30):
        mysum = 0
        for i in range(1000000):
            x[i] = i

        # y = []
        for i in range(1000000 - 1):
            y[i] = (x[i] + x[i+1])

        i = 0
        for i in range(0, 1000000, 100):
            mysum += y[i]

    print(mysum)
dotest()