#!/usr/bin python

cdef long sum = 0
cdef int i
cdef int e
for e in range(30):
    sum = 0
    x = []

    for i in range(1000000):
        x.append(i)

    y = []
    for i in range(1000000 - 1):
        y.append(x[i] + x[i+1])

    i = 0
    for i in range(0, 1000000, 100):
        sum += y[i]

print(sum)
