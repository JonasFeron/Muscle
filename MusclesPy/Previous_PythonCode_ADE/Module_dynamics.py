# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 2022

MEMOIRE: "Etude numérique et expérimentale du comportement dynamique des structures de tenségrité"

ANNEE: 2021-2022
@author: Antoine Desmet
"""
import numpy as np
from StructureObj import *
import matplotlib.pyplot as plt
import time
#------------------------------------------------------------------------------
# INITIAL STATE OF THE STRUCTURE
#------------------------------------------------------------------------------

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
DynMasses = 4*np.array([1,1,1,1,1,1]) #kg
Prestrain = 2 #[kN]
w,PHI = Str.test_Module_dynamics(Prestrain,DynMasses)
print(Str.ElementsA)
print(w)
#------------------------------------------------------------------------------
# 3D GRAPHICS - PLOT OF THE STRUCTURE
#------------------------------------------------------------------------------
#CODE
coord = np.zeros(3*Str.NodesCount)

CoordX = Str.NodesCoord[:,0]
CoordY = Str.NodesCoord[:,1]
CoordZ = Str.NodesCoord[:,2]

coord[Str.IsDOFfree] = PHI[0]
xpos = np.arange(0,3*Str.NodesCount,3)
ypos = xpos+1
zpos = xpos+2

X_all = np.take(coord, xpos ) #Take the extremum of the phi
Y_all = np.take(coord, ypos )
Z_all = np.take(coord, zpos )

freqaff = 30
t = np.arange(0,3,0.01)

Xtime = np.sin(freqaff*t)*np.ones((Str.NodesCount,len(t))) 
Ytime = np.sin(freqaff*t)*np.ones((Str.NodesCount,len(t))) 
Ztime = np.sin(freqaff*t)*np.ones((Str.NodesCount,len(t))) 

for i in range(Str.NodesCount):
    Xtime[i,:] *= X_all[i]
    Ytime[i,:] *= Y_all[i]
    Ztime[i,:] *= Z_all[i]


    

ax = plt.axes(projection='3d')

ax.set_title("3D Structure", pad=25, size=15)
ax.set_xlabel("X") 
ax.set_ylabel("Y") 
ax.set_zlabel("Z")
ax.set_xlim3d(-2, 2)
ax.set_ylim3d(-3, 1)
ax.set_zlim3d(0, 3)
ax.scatter3D(CoordX,CoordY,CoordZ,color='green')


i = 0
 

while i <len(t):

    ax.scatter3D(CoordX+Xtime[:,i],CoordY+Ytime[:,i],CoordZ+Ztime[:,i],color='red')
    for j in range(Str.ElementsCount):
        a = Str.ElementsEndNodes[j,0]
        b = Str.ElementsEndNodes[j,1]
        if Str.ElementsType[j] == -1:
            ax.plot3D([CoordX[a]+Xtime[a,i],CoordX[b]+Xtime[b,i]],[CoordY[a]+Ytime[a,i],CoordY[b]+Ytime[b,i]],[CoordZ[a]+Ztime[a,i],CoordZ[b]+Ztime[b,i]],color='black')
        else:
            ax.plot3D([CoordX[a]+Xtime[a,i],CoordX[b]+Xtime[b,i]],[CoordY[a]+Ytime[a,i],CoordY[b]+Ytime[b,i]],[CoordZ[a]+Ztime[a,i],CoordZ[b]+Ztime[b,i]],color='blue')
    i+=1;
    plt.pause(10)
    plt.show()
    plt.pause(0.0002)
    plt.clf() 
    ax = plt.axes(projection='3d')
    ax.set_title("3D Structure", pad=25, size=15)
    ax.set_xlabel("X") 
    ax.set_ylabel("Y") 
    ax.set_zlabel("Z")
    ax.set_xlim3d(-2, 2)
    ax.set_ylim3d(-3, 1)
    ax.set_zlim3d(0, 3)
    ax.scatter3D(CoordX,CoordY,CoordZ,color='green')




###########################################################################################################
