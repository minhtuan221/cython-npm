#!/usr/bin python
import array
sum = 0
x = array.array('l',[])
y = array.array('l',[])
for e in range(30):
    sum = 0

    for i in range(1000000):
        x.append(i)

    for i in range(1000000 - 1):
        y.append(x[i] + x[i+1])

    i = 0
    for i in range(0, 1000000, 100):
        sum += y[i]

print(sum)
