import json
import numpy as np
import matplotlib.pyplot as plt
from timeit import default_timer as timer
####
'''
A test of a few different implementations of the energy transfer function
'''
with open('cache/singlecross_10_5_QQ_50000.json') as json_file:
    dict = json.load(json_file)
    data = np.asarray(dict['r_components'])

xdata = np.arange(0,0.15,0.00001)
print(len(xdata))
A = 1
c = 3e5
rad = 145

def fun_original (x, A, c, interact1, rad, offset):
    n = len(interact1)
    return A/n * sum([ np.exp(-1*x*(c*interact1[i] + rad))  for i in range(n)]) + offset


def optimized_fun(x, A, c, interact1, rad, offset):
    exponentials = np.exp(-x[:, np.newaxis] * (c * interact1 + rad))
    result = A * np.sum(exponentials, axis=1) / len(interact1) + offset
    return result

start = timer()
#y1 = fun_original(xdata, A , c, data, rad, offset = 0)
dt = timer() - start
print ("Unoptimised python implementation ran in %f s" % dt)


start = timer()
y2 = optimized_fun(xdata, A , c, data, rad, offset = 2)
dt = timer() - start
print ("Numpy implementation ran in %f s" % dt) 
#plt.plot(xdata,y)
plt.plot(xdata,y2)
plt.show()


