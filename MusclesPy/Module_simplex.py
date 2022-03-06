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
Str = StructureObj()

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
    Str.DynMasses = np.array([4.66,4.66,4.66, 4.24,4.24,4.24]) #kg
    w,PHI = Str.Module_dynamics_initial(DeltaPrestrain[i])
    omega[i,0] = w[0]
    omega[i,1] = w[1]
    omega[i,2] = w[2]
    omega[i,3] = w[3]
    omega[i,4] = w[4]
    
    
    
    
    
#################################
# PLOT
#################################


# plt.figure(0)
# plt.plot(DeltaPrestrain,omega[:,0],label="mode 1", color='blue')
# plt.xlabel('Précontrainte [kN]')
# plt.ylabel('Omega [Rad/sec]')
# plt.title('Evolution de la première fréquence propre en fonction de la précontrainte')
# plt.grid(color='black', linestyle='-', linewidth=0.5)
# plt.legend() 


# plt.figure(1)
# plt.plot(DeltaPrestrain,omega[:,0],label="mode 1", color='blue')
# plt.plot(DeltaPrestrain,omega[:,1],label="mode 2", color='orange')
# plt.plot(DeltaPrestrain,omega[:,2],label="mode 3", color='green')
# plt.plot(DeltaPrestrain,omega[:,3],label="mode 4", color='red')
# plt.plot(DeltaPrestrain,omega[:,4],label="mode 5", color='blueviolet')
# plt.grid(color='black', linestyle='-', linewidth=0.5)
# plt.xlabel('Précontrainte [kN]')
# plt.ylabel('Omega [Rad/sec]')
# plt.title('Evolution des cinq premières fréquences propres en fonction de la précontrainte')
# plt.legend()


# delta = np.zeros((int(b-a),5))
# position = np.arange(0, int(b-a), 1, dtype=int)*1/step
# position = position.astype(int)

# for j in range(5):
#     for i in range(len(delta)):
#         x = position[i]
#         delta[i,j] = omega[x+99,j] - omega[x,j]


    
# #################################
# # PLOT
# #################################

# plt.figure(2)
# fig, ax = plt.subplots()
# width = 0.15
# x = np.arange(0, int(b-a), 1, dtype=int)
# ax.bar(x- 2*width, delta[:,0], width-0.05, label='mode 1', color='blue')
# ax.bar(x - width, delta[:,1], width-0.05, label='mode 2', color='orange')
# ax.bar(x , delta[:,2], width-0.05, label='mode 3', color='green')
# ax.bar(x + width, delta[:,3], width-0.05, label='mode 4', color='red')
# ax.bar(x + 2*width, delta[:,4], width-0.05, label='mode 5', color='blueviolet')

# ax.set_title('Variation des cinq premières fréquences propres en fonction de l\'augmentation de la précontrainte')
# ax.set_ylabel('Omega [Rad/sec]')
# ax.set_xlabel('Variation de précontrainte [kN]')
# text_x = np.array(["2.5-3.5","3.5-4.5","4.5-5.5","5.5-6.5","6.5-7.5","7.5-8.5"])
# # ax.grid(which='major')
# # ax.grid(which='minor', alpha=0.2, linestyle='--')
# axes = plt.gca()
# axes.yaxis.grid()
# ax.set_xticks(x)    # This ensures we have one tick per year, otherwise we get fewer
# ax.set_xticklabels(text_x.astype(str), rotation='horizontal')

# ax.legend()
# plt.show()


#################################
# PLOT 3D
#################################

# Str.NodesCoord = np.array([[0.00, -2043.82, 0.00],
#                           [0.00, 0.00, 0.00],
#                           [1770.00, -1021.91, 0.00],
#                           [590.00, -2201.91, 1950.00],
#                           [-431.91, -431.91, 1950.00],
#                           [1611.91, -431.91, 1950.00]]) * 1e-3

# CoordX = Str.NodesCoord[:,0]
# CoordY = Str.NodesCoord[:,1]
# CoordZ = Str.NodesCoord[:,2]
# NodeNum = np.arange(1,Str.NodesCount+1 ,1)
# ax = plt.axes(projection='3d')

# ax.set_title("Visualisation 3D de la structure", pad=25, size=15)
# ax.set_xlabel("X") 
# ax.set_ylabel("Y") 
# ax.set_zlabel("Z")
# ax.set_xlim3d(-1, 3)
# ax.set_ylim3d(-3, 1)
# ax.set_zlim3d(0, 3)
# ax.scatter3D(CoordX,CoordY,CoordZ,color='green')
# Str.ElementsType = np.array([-1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

# for j in range(Str.ElementsCount):
#     a = Str.ElementsEndNodes[j,0]
#     b = Str.ElementsEndNodes[j,1]
#     if Str.ElementsType[j] == -1:
#         ax.plot3D([CoordX[a],CoordX[b]],[CoordY[a],CoordY[b]],[CoordZ[a],CoordZ[b]],color='black')
#     else:
#         ax.plot3D([CoordX[a],CoordX[b]],[CoordY[a],CoordY[b]],[CoordZ[a],CoordZ[b]],color='blue')
        
# for i in range(Str.NodesCount):
#     # ax.text(CoordX[i],CoordY[i],CoordZ[i], 'Noeud '+str(NodeNum[i]) +'-'+ str((round(CoordX[i], 2),round(CoordY[i], 2),round(CoordZ[i], 2))), color="black", fontsize=10,fontweight='bold')
#     ax.text(CoordX[i],CoordY[i],CoordZ[i], 'Noeud '+str(NodeNum[i]), color="black", fontsize=10,fontweight='bold')
#     # ax.text(CoordX[i],CoordY[i],CoordZ[i], str((round(CoordX[i], 2),round(CoordY[i], 2),round(CoordZ[i], 2))), color="black", fontsize=10,fontweight='bold')