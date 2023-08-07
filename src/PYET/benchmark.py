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

xdata = np.arange(0,0.15,0.001)
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

def mesh(r,t):
    tfit = t
    R, T = np.meshgrid(r,tfit)
    exp_rt = np.exp(-R*T)  # matrix
    exp_t = np.exp(-tfit)     # vector
    return exp_rt, exp_t, tfit

def fun_meshgrid_opt(rad, c, A, offset, interact1): 
    return (exp_t**rad * np.sum(exp_rt**c,axis=1))*A/len(interact1) + offset



start = timer()
y = fun_original(xdata, A , c, data, rad, offset = 0)
dt = timer() - start
print ("Unoptimised python implementation ran in %f s" % dt)

start = timer()
exp_rt, exp_t, tfit = mesh(data,xdata)
dt = timer() - start
print ("Meshing process ran in %f s" % dt) 
start = timer()
y2 = fun_meshgrid_opt(rad, c, A, 1,data)
dt = timer() - start
print ("Simulation using meshgrid optimisation ran in %f s" % dt) 

  
start = timer()
y3 = optimized_fun(xdata, A , c, data, rad, offset = 2)
dt = timer() - start
print ("Numpy implementation (ChatGPT) ran in %f s" % dt) 

plt.plot(xdata,y)
plt.plot(xdata,y2)
plt.plot(xdata,y3)
plt.show()


