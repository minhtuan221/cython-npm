#!/usr/bin python
from cpython cimport array
import array
cdef int x[1000000]
cdef int y[1000000]

cdef long sum = 0
cdef int i
cdef int e
for e in range(30):
    sum = 0
    # x = []

    for i in range(1000000):
        x[i] = i

    # y = []
    for i in range(1000000 - 1):
        y[i] = (x[i] + x[i+1])
        
    i = 0
    for i in range(0, 1000000, 100):
        sum += y[i]

print(sum)
