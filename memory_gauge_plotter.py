# -*- coding: utf-8 -*-
"""
Created on Monday June  29 11:27:12 2015

@author: Alireza
"""

"""========================================================================================="""
"""========================================================================================="""
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import os


with open("STATOIL_HULDRA_A09_US00015_3.5.2015.txt") as f:
#    data = f.readlines()
	data=[]
	for line in f:
		
		if line.startswith("2015"):
			data.append(line)
#print data
#data = data.split('\n')

#for row in data:
#	print row.split('\t')[0]

x=[]
for row in data:
	x.append(mdates.date2num(datetime.datetime.strptime(row.split('\t')[0],"%Y.%m.%d %H:%M:%S")))
		
#x = [mdates.date2num(datetime.datetime.strptime(row.split('\t')[0],"%Y.%m.%d %H:%M:%S")) for row in data]

#print x

y1=[]
for row in data:
	s1 = row.split('\t')[2]
	y1.append(float(s1.replace(',', '.')))
#s1 = [row.split('\t')[2] for row in data]

#print s1
#y1 = float(s1.replace(',', '.'))
y2=[]
for row in data:
	s2 = row.split('\t')[3]
	y2.append(float(s2.replace(',', '.')))
	
fig = plt.figure()

#ax1 = plt.subplot()

ax1 = fig.add_subplot(2,1,1)

ax1.set_title("Well A04")    
ax1.set_xlabel('Date and Time')
ax1.set_ylabel('BHA Pressure (psia)')
ax1.axes.get_xaxis().set_visible(False)

ax2 = fig.add_subplot(2,1,2,sharex=ax1)

#ax2.set_title("Well A05")    
ax2.set_xlabel('Date and Time')
ax2.set_ylabel('BHA Temperature (C)')


ax1.plot(x,y1, c='b', label='Pressure')
ax2.plot(x,y2, c='r', label='Temperature')

leg = ax1.legend()
leg = ax2.legend()

plt.xticks(rotation=30,ha='right')
ax1.xaxis_date()
date_format = mdates.DateFormatter("%Y.%m.%d %H:%M:%S")
ax1.xaxis.set_major_formatter(date_format)

ax2.xaxis_date()
date_format = mdates.DateFormatter("%Y.%m.%d %H:%M:%S")
ax2.xaxis.set_major_formatter(date_format)
plt.show()
