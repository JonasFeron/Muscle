# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 16:13:58 2022

@author: desme
"""

import xlsxwriter
from StructureObj import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

a = 0
b = 8.5
step = 0.1
DeltaPrestrain = np.arange(a,b,step)
nbreMass = 11

omega = np.zeros((len(DeltaPrestrain),5*nbreMass))
Str = StructureObj()

for j in range(nbreMass):
    
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
        Str.DynMasses = np.array([4.66,4.66,4.66, 4.24,4.24,4.24])+j*10 #kg
        w,PHI = Str.Module_dynamics_initial(DeltaPrestrain[i])
        omega[i,0+5*j] = w[0]
        omega[i,1+5*j] = w[1]
        omega[i,2+5*j] = w[2]
        omega[i,3+5*j] = w[3]
        omega[i,4+5*j] = w[4]




freq = omega/(2*np.pi)

################################################################
# WRITE THE RESULT IN EXCEL
################################################################

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('C:/Users/desme/OneDrive - UCL\Mémoire - Drive/Simulation_num/Geom_initale.xlsx')
worksheet = workbook.add_worksheet('prestrain')

# Some data we want to write to the worksheet.




# Start from the first cell. Rows and columns are zero indexed.
#worksheet.write(row, col,item)
for i in range(nbreMass):
    strlettre = 'A'
    str1 = strlettre+str(i)
    strin = 'Intitial Mass +'
    str2 = i*10
    str3 = '[kN]'
    worksheet.write(0,1+5*i, strin+str(str2)+str3)
    
    worksheet.write(1, 1+i*5,'freq'+str(1))
    worksheet.write(1, 1+i*5+1,'freq'+str(2))
    worksheet.write(1, 1+i*5+2,'freq'+str(3))
    worksheet.write(1, 1+i*5+3,'freq'+str(4))
    worksheet.write(1, 1+i*5+4,'freq'+str(5))
    
# worksheet.write('A1', 'Prestrain [kN]')
# worksheet.write('A2', 'Frequency  [Hz]')
worksheet.write(1, 0,'Précontrainte [kN]')

for i in range(len(DeltaPrestrain)):
    worksheet.write(2+i, 0,DeltaPrestrain[i])
    
row = 0

for col, data in enumerate(freq.T):
    worksheet.write_column(2+row, 1+col, data)


# row = 1
# col = 0
# # Iterate over the data and write it out row by row.
# for item, cost in (expenses):
#     worksheet.write(row, col,item)
#     worksheet.write(row, col + 1, cost)
#     row += 1

# # Write a total using a formula.
# worksheet.write(row, 0, 'Total')
# worksheet.write(row, 1, '=SUM(B1:B4)')

workbook.close()
