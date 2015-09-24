# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 15:46:14 2014

@author: bolatzh
"""

import h5py
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib
try:
    from PIL import Image
except:
    import Image
#import Image
import pandas as pd
import matplotlib.gridspec as gridspec


#plot_folder=r'W:\Data\Maersk\HDA-17\DAS\DAS_plotcuts'
plot_folder=r'P:\Data\BP\G-21_2015\DAS\1sec-Time-Resolution\Plots'


mem_file=r'O:\Data\BP\G-21_2015\Memory-Gauge\US00038_DataFiles\Memory_Gauge_G21.txt'

freq=25 #Only one Frequency at a time
pres_lim=[5870,6030]
#pres_lim=-1
pres_unit='psi'
#temp_lim=[91.32,91.2]
temp_lim=-1
temp_unit='degC'
plot_depth_unit='m'


def readmemgauge(mem_gau_file):
    print 'Reading Memory gauge file...'
    timestamps = []
    pressure = []
    temperature = []
    with open(mem_gau_file, 'rb') as csvfile:
        for ind,line in enumerate(csvfile):
            if ind>20:            
                d = line.split()
#                print d
                timestamps.append(matplotlib.dates.date2num(
                    datetime.datetime.strptime(d[0] + ' ' + d[1], '%Y.%m.%d %H:%M:%S')))                
                pressure.append(float(d[3].replace(",",".")))
                temperature.append(float(d[4].replace(",",".")))    
    mem=pd.DataFrame({'timestamps':timestamps,'temperature':temperature,'pressure':pressure})   
    mem=mem.sort(['timestamps'])    
    return mem

mem_data=readmemgauge(mem_file)
print mem_data

gs=gridspec.GridSpec(10,1)

fig = plt.figure(figsize=(18, 8))
ax1 = plt.subplot(gs[:7,:])
ax2 = plt.subplot(gs[7:,:], sharex=ax1)

plot_start_time=[]
plot_end_time=[]
for root, dirs, files in os.walk(plot_folder):
    for f in files:
        if f.endswith('.png'):
            head,ext=os.path.splitext(f)
            
            if int(head.split('_')[0])==freq:
                print 'plotting %s' % f
                attrs=head.split('_')
                freq=int(attrs[0])
                t_start=datetime.datetime.strptime(attrs[1],'%Y.%m.%d.%H.%M.%S')
                t_sec=float(attrs[2])
                t_end=t_start+datetime.timedelta(seconds=t_sec)
                t_start_mt=matplotlib.dates.date2num(t_start)
                t_end_mt=matplotlib.dates.date2num(t_end)
                if plot_depth_unit=='ft':
                    d_start=float(attrs[3])*3.2808
                    d_end=float(attrs[4])*3.2808
                elif plot_depth_unit=='m':
                    d_start=float(attrs[3])
                    d_end=float(attrs[4])
    
                im=Image.open(os.path.join(root,f))            
                extent=[t_start_mt,t_end_mt,d_end,d_start]
                ax1.imshow(im,origin='upper', extent=extent,aspect='auto')
                        
                plot_start_time.append(t_start_mt)
                plot_end_time.append(t_end_mt)

if pres_unit=='bar':
    mem_data['pressure']=mem_data['pressure']*0.0689475729
elif pres_unit=='kpa':
    mem_data['pressure']=mem_data['pressure']*6.89475729

if temp_unit=='degF':
    mem_data['temperature']=mem_data['temperature']*9.0/5.0+32.0

mem_plot1,=ax2.plot(mem_data['timestamps'],mem_data['pressure'],'b')
ax3=ax2.twinx()
mem_plot2,=ax3.plot(mem_data['timestamps'],mem_data['temperature'],'g')

date_format = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S')

ax1.get_xaxis().set_visible(False)
ax1.set_ylabel("Depth, %s MD" % plot_depth_unit)
ax2.set_xticklabels(ax3.xaxis.get_majorticklabels(), rotation=30,ha='right')
ax2.xaxis_date()
ax2.xaxis.set_major_formatter(date_format)
ax2.yaxis.label.set_color(mem_plot1.get_color())
ax2.tick_params(axis='y', colors=mem_plot1.get_color())
ax2.set_xlim(min(plot_start_time),max(plot_end_time))
ax2.set_ylabel("Pressure, %s" % pres_unit)
ax2.grid(True)
if pres_lim!=-1:
    ax2.set_ylim(pres_lim[0],pres_lim[1])

ax3.yaxis.label.set_color(mem_plot2.get_color())
ax3.tick_params(axis='y', colors=mem_plot2.get_color())
ax3.set_ylabel("Temperature, %s" % temp_unit)
if temp_lim!=-1:
    ax3.set_ylim(temp_lim[0],temp_lim[1])

plt.show()
        
