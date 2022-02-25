# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 15:14:18 2022

@author: Antoine Desmet
"""

from StructureObj import *
import matplotlib.pyplot as plt


DeltaPrestrain = np.arange(0.00,8,0.01)


omega = np.zeros((len(DeltaPrestrain),1))

for i in range(len(DeltaPrestrain)):
    Struct = StructureObj()
    Struct.NodesCoord = np.array([[0.00, 0.00, 0.00],
                                  [2.50, 0.00, 0.00],
                                  [5.00, 0.00, 0.00]])

    Struct.IsDOFfree = np.array([False, False, False,
                                 True, False, False,
                                 False, False, False])

    Struct.ElementsType = np.array([1,1])
    Struct.NodesCount = 3
    Struct.ElementsCount = 2
    Struct.FixationsCount = 8
    Struct.DOFfreeCount = 3 * Struct.NodesCount - Struct.FixationsCount
    Struct.ElementsEndNodes = np.array([[0, 1],[1,2]])

    Struct.ElementsE = 71750 * np.ones((Struct.ElementsCount, 2))  # MPa
    Struct.ElementsA = 50.3 * np.ones((Struct.ElementsCount, 2))  # mm2
    Struct.DynMasses = 1 * np.array([1, 1, 1])  # kg
    w, PHI = Struct.Module_dynamics_initial(DeltaPrestrain[i])
    omega[i] = w



plt.figure(0)
plt.plot(DeltaPrestrain,omega,label="Omega")


plt.xlabel('Prestrain')
plt.ylabel('Omega')
plt.title('Circular frequency in function of the prestrain')
plt.xlim(0, 8)
plt.ylim(1694, 1700)
plt.legend() 