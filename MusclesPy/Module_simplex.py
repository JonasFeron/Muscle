# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 16:37:11 2022

@author: desme
"""

from StructureObj import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

a = 2.5
b = 8.5
step = 0.01
DeltaPrestrain = np.arange(a,b,step)


omega = np.zeros((len(DeltaPrestrain),5))

for i in range(len(DeltaPrestrain)):
    Str = StructureObj()
    Str.NodesCount = 6
    Str.ElementsCount = 12
    Str.FixationsCount = 6
    Str.NodesCoord = np.array([[0.00, -2043.82, 0.00],
                          [0.00, 0.00, 0.00],
                          [1770.00, -1021.91, 0.00],
                          [590.00, -2201.91, 1950.00],
                          [-431.91, -431.91, 1950.00],
                          [1611.91, -431.91, 1950.00]]) * 1e-3
    
    
    Str.IsDOFfree = np.array([False, True, False,
                                  False, False, False,
                                  True, True, False,
                                  True, True, True,
                                  True, True, True,
                                  True, True, True])
    
    Str.ElementsType = np.array([-1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    Str.ElementsEndNodes = np.array([[2, 4],
                                [1, 3],
                                [0, 5],
                                [1, 2],
                                [0, 1],
                                [0, 2],
                                [4, 5],
                                [3, 4],
                                [3, 5],
                                [2, 5],
                                [1, 4],
                                [0, 3]])
    
    # Bars can only be in compression and cables only in tension
    Str.ElementsE = np.array([[70390, 0],
                          [70390, 0],
                          [70390, 0],
                          [0, 71750],
                          [0, 71750],
                          [0, 71750],
                          [0, 71750],
                          [0, 71750],
                          [0, 71750],
                          [0, 72190],
                          [0, 72190],
                          [0, 72190]])  # MPa
    
    Str.ElementsA = np.ones((12, 2))
    Str.ElementsA[0:3, :] = 364.4 # poutres
    Str.ElementsA[3:12, :] = 50.3 # cables
    Str.DynMasses = 4*np.array([1,1,1,1,1,1]) #kg
    w,PHI = Str.Module_dynamics_initial(DeltaPrestrain[i])
    omega[i,0] = w[0]
    omega[i,1] = w[1]
    omega[i,2] = w[2]
    omega[i,3] = w[3]
    omega[i,4] = w[4]
    
    
    
    
    
#################################
# PLOT
#################################


plt.figure(0)
plt.plot(DeltaPrestrain,omega[:,0],label="Omega 1")
plt.xlabel('Prestrain')
plt.ylabel('Omega')
plt.title('Circular frequency in function of the prestrain')
plt.legend() 


plt.figure(1)
plt.plot(DeltaPrestrain,omega[:,0],label="Omega 1", color='blue')
plt.plot(DeltaPrestrain,omega[:,1],label="Omega 2", color='orange')
plt.plot(DeltaPrestrain,omega[:,2],label="Omega 3", color='green')
plt.plot(DeltaPrestrain,omega[:,3],label="Omega 4", color='red')
plt.plot(DeltaPrestrain,omega[:,4],label="Omega 5", color='blueviolet')
plt.xlabel('Prestrain')
plt.ylabel('Omega')
plt.title('Circular frequency in function of the prestrain')
plt.legend()


delta = np.zeros((int(b-a),5))
position = np.arange(0, int(b-a), 1, dtype=int)*1/step
position = position.astype(int)

for j in range(5):
    for i in range(len(delta)):
        x = position[i]
        delta[i,j] = omega[x+99,j] - omega[x,j]


    
#################################
# PLOT
#################################


fig, ax = plt.subplots()
width = 0.15
x = np.arange(0, int(b-a), 1, dtype=int)
ax.bar(x- 2*width, delta[:,0], width-0.05, label='mode 1', color='blue')
ax.bar(x - width, delta[:,1], width-0.05, label='mode 2', color='orange')
ax.bar(x , delta[:,2], width-0.05, label='mode 3', color='green')
ax.bar(x + width, delta[:,3], width-0.05, label='mode 4', color='red')
ax.bar(x + 2*width, delta[:,4], width-0.05, label='mode 5', color='blueviolet')

ax.set_title('Increase of the natural frequency between two prestrain level in function of the modes')
ax.set_ylabel('Omega')
ax.set_xlabel('Range of prestrain [kN]')
text_x = np.array(["2.5-3.5","3.5-4.5","4.5-5.5","5.5-6.5","6.5-7.5","7.5-8.5"])
ax.set_xticks(x)    # This ensures we have one tick per year, otherwise we get fewer
ax.set_xticklabels(text_x.astype(str), rotation='horizontal')

ax.legend()
plt.show()
