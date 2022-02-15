# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 2022

MEMOIRE: "Etude numérique et expérimentale du comportement dynamique des structures de tenségrité"

ANNEE: 2021-2022
@author: Antoine Desmet
"""
import numpy as np
from StructureObj import *

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
Str.DynMasses = 4*np.array([1,1,1,1,1,1]) #kg
Prestrain = 10 #[kN]
w,PHI = Str.Module_dynamics_initial(Prestrain)
print(Str.ElementsA)
print(w)
#------------------------------------------------------------------------------
# 3D GRAPHICS - PLOT OF THE STRUCTURE
#------------------------------------------------------------------------------
"""import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

#Construction 3d structure
#Connectivité X,Y,Z
ConX = np.zeros(2*Str.ElementsCount) #[2*nbre elem] [X_debut_1,X_fin_1,X_debut_2,X_fin_2]
ConY = np.zeros(2*Str.ElementsCount)
ConZ = np.zeros(2*Str.ElementsCount)
print('ConX', ConX)
for i in range(Str.ElementsCount):
    ConX[2*i] = Str.NodesCoord[Str.ElementsEndNodes[i,0],0]
    ConY[2*i] = Str.NodesCoord[Str.ElementsEndNodes[i,0],1]
    ConZ[2*i] = Str.NodesCoord[Str.ElementsEndNodes[i,0],2]
    ConX[2*i+1] = Str.NodesCoord[Str.ElementsEndNodes[i,1],0]
    ConY[2*i+1] = Str.NodesCoord[Str.ElementsEndNodes[i,1],1]
    ConZ[2*i+1] = Str.NodesCoord[Str.ElementsEndNodes[i,1],2]







ax = plt.axes(projection='3d')





for i in range(Str.ElementsCount):
     ax.plot3D([ConX[2*i],ConX[2*i+1]],[ConY[2*i],ConY[2*i+1]],[ConZ[2*i],ConZ[2*i+1]],color = 'b')
     ax.scatter3D(ConX[2*i], ConY[2*i], ConZ[2*i], color='red')
     ax.scatter3D(ConX[2*i+1], ConY[2*i+1], ConZ[2*i+1], color='red')

# x = Str.NodesCoord[:,0]
# y = Str.NodesCoord[:,1]
# z = Str.NodesCoord[:,2]


# ax.scatter3D(x, y, z, color='red')
ax.set_title("3D Structure", pad=25, size=15)
ax.set_xlabel("X") 
ax.set_ylabel("Y") 
ax.set_zlabel("Z")

# matplotlib.pyplot.show()
"""