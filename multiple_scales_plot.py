# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 14:13:34 2015

@author: bolatzh
"""


#=======================================================================================
# INPUT ================================================================================

# "plots" is a list of files with data to plot with multiple scales 
#
# txt files format:
# first line is Series title
# next lines are "datetime \tab parameter"
# 
# for examples:
# HDA31:BHP, bar
# 27.01.2015 00:02:29	179
# 27.01.2015 00:06:26	178
# 27.01.2015 00:12:03	179
# ...
#
# NOTE: delete comma at the end of last item of the list
# if using Windows put 'r' in front of directory path, example: r'W:\Data\CoP\A-02\DTS'

plots=[
r"C:\Users\alirezaro\Desktop\A09_Statoil\Annulus_Pressure\Annulus-B-Pressure.txt",
r"C:\Users\alirezaro\Desktop\A09_Statoil\A-09_Memory-gauge-data\Multi-Plot\Memory-Gauge.txt"
#r"W:\Data\Maersk\HDA-33\Mem_gauge\Scada\HDA31_BHP.txt",
#r"W:\Data\Maersk\HDA-33\Mem_gauge\Scada\HDA31_BHT.txt",
#r"W:\Data\Maersk\HDA-33\Mem_gauge\Scada\HDA31_CHOKE.txt"
]


#=======================================================================================
#=======================================================================================




import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt
import matplotlib
import datetime


fig, host = plt.subplots()
fig.subplots_adjust(right=0.75)




# move the spine of the second axes outwards

colors=['b','r','g','c','m','k']
offset = 1.1
linewidth = 1
i=0
for myaxis in plots:
    print myaxis
    myfile=open(myaxis,'r')                                
    x=[]
    y=[]    
    for ind,line in enumerate(myfile):
        
        if ind==0:
            label=line
        else:
            x.append(matplotlib.dates.date2num(
                        datetime.datetime.strptime(
                            line.split('\t')[0], "%d.%m.%Y %H:%M:%S")))
            y.append(float(line.split('\t')[1]))

    if i+1>len(colors):
        color_ind=i-len(colors)
    else:
        color_ind=i            
        
    
    if i==0:
        p, = host.plot(x,y,color=colors[color_ind],label=label,linewidth=linewidth)
        host.yaxis.label.set_color(p.get_color())
        host.tick_params(axis='y', colors=p.get_color())
        host.set_ylabel(label)
    elif i==1:        
        par= host.twinx()
        p, = par.plot(x,y,color=colors[color_ind], label=label,linewidth=linewidth)
        par.yaxis.label.set_color(p.get_color())
        par.tick_params(axis='y', colors=p.get_color())
        par.set_ylabel(label)     
        par.set_ylim(215,216)		
    else:
        par = host.twinx()
        par.spines["right"].set_position(("axes", offset))
        par.set_frame_on(True)
        par.patch.set_visible(False)    
        plt.setp(par.spines.values(), visible=False)
        par.spines["right"].set_visible(True)        
        p,=par.plot(x,y,color=colors[color_ind],label=label,linewidth=linewidth)
        par.yaxis.label.set_color(p.get_color())
        par.spines["right"].set_edgecolor(p.get_color())        
        par.tick_params(axis='y', colors=p.get_color())
        par.set_ylabel(label)
        offset+=0.1
    i+=1    

host.xaxis_date()
date_format = matplotlib.dates.DateFormatter('%b.%d %H:%M')
host.xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()

plt.show()