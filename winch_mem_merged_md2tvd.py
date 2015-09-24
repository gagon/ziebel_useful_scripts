# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 19:24:15 2015

@author: bolatzh
"""

#=======================================================================================
# INPUT ================================================================================

# "InputFile" is merged ASEP and memory gauge files using mergescript.py
# "dev" is deviation file. Same format as for plotting DTS/DAS using main.py 
# "outfile" is output file in txt format. It can be any name you want. Convention is to extend merged file name with "_tvd" 
# if using Windows put 'r' in front of directory path, example: r'W:\Data\CoP\A-02\DTS'

inputFile=r'O:\Data\BP\G-21_2015\ASEP\MergedPTD.txt'
dev=r'O:\Data\BP\G-21_2015\Completion-Inclination\Inclination.csv'
outfile=r'O:\Data\BP\G-21_2015\ASEP\G21_merged_tvd.txt'

# specify depth units for input and output files: 'm' ot 'ft'           
dev_depth_unit='m'      
    

#=======================================================================================
#=======================================================================================


import csv
import numpy as np
import math


md_arr=[]
tvd_arr=[]
incl_arr=[]
with open(dev, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for idx, row in enumerate(spamreader):

        md_arr.append(float(row[0]))
        incl_arr.append(float(row[1]))
        if idx==0:
            tvd_arr.append(float(row[0]))
        else:
            md_diff=md_arr[idx]-md_arr[idx-1]
            slope=math.cos(math.radians((incl_arr[idx-1]+incl_arr[idx])/2.0))        
            tvd_diff=slope*md_diff
            tvd_arr.append(tvd_arr[idx-1]+tvd_diff)
    if dev_depth_unit=="ft":
        md_arr=md_arr*3.2808
        tvd_arr=tvd_arr*3.2808


print md_arr
print '==='
print tvd_arr

new_data=[]
with open(inputFile, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for idx, row in enumerate(spamreader):
        
        if idx==0:
            print row
            row.insert(2,str("TVD (m)" ))
            new_data.append(row)
        elif idx > 1:
			md=float(row[1])
			tvd=np.interp(md,md_arr,tvd_arr)
			row.insert(2,str(tvd))
			new_data.append(row[:-1])

with open(outfile, 'wb') as csvfile:    
    for row in new_data:
        row.append('\r\n')
        csvfile.write(','.join(map(str, row)) )

print 'output written to: ' + outfile
