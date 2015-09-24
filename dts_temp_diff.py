# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 08:49:59 2015

@author: bolatzh
"""

"""========================================================="""
"""===========================INPUT HEADER=================="""



main_dir=r'L:\Data\Daleel\BR-21\DTS\Calibrated_DTS\New\BR-21_cal_dts\BR-21_dts_merged.hdf'
cmap_lims=[-1.0,1.0]
colormap='jet'
hdf_group='Merged'

"""===========================END==========================="""
"""========================================================="""







import os
import sys
import datetime
import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates

data=[]

if os.path.isdir(main_dir):
    for root, dirs, files in os.walk(main_dir):
        for f in files:
            if f.endswith('.dts'):                
                print "reading: ",f                
                dts_file=open(os.path.join(root,f),'r')
                
                trace=[]
                trace_start=100000000    
                for index,line in enumerate(dts_file):                    
                    if "TIMESTAMP" in line:
                        date=line.split(": ")[1].split(" ")[0]
                        time=line.split(": ")[1].split(" ")[1]
                        dt=date+" "+time
                        dt=datetime.datetime.strptime(dt,"%Y/%m/%d %H:%M:%S")
                        header_split=index    
                    if "~A" in line:                    
                        trace_start=index
                        header_end=index    
                    if index>trace_start:
                        trace.append([float(line.split("\t")[0]),float(line.split("\t")[1])])
                
                trace=np.transpose(np.array(trace))            
                data.append([dt,trace])                
else:
    print 'loading hdf file..'
    dts_hdf = h5py.File(main_dir,'r')  
    dts_group_list=[] 
    block_values=dts_hdf['Data/Calibrated_DTS/DTS/'+hdf_group+'/block0_values'][...]
    depths=np.transpose(block_values[0])[0]
    temperature=np.transpose(np.array((np.transpose(dts_hdf['Data/Calibrated_DTS/DTS/'+hdf_group+'/block0_values'][...])[1])))
    timestamps=dts_hdf['Data/Calibrated_DTS/DTS/'+hdf_group+'/axis2'][...]
    data=[]
    for i,t in enumerate(timestamps):
        print t
        trace=np.array([depths,temperature[i]])
        data.append([datetime.datetime.strptime(t, "%Y/%m/%d %H:%M:%S"),trace])
    dts_hdf.close()



# sort fetched data by datetime
data=sorted(data, key=lambda x: x[0])


gs=gridspec.GridSpec(1,30)
fig=plt.figure(figsize=(18, 10))
ax2 = plt.subplot(gs[:,:6])
ax1 = plt.subplot(gs[:,7:], sharey=ax2)

temp_diff=[]
time_collection=[]

for i,d in enumerate(data):       
    ax2.plot(np.array(d[1][1]),np.array(d[1][0]))
    if i==0:
        init_trace=d[1][1]
        depth=d[1][0]        
    else:
        trace=[]
        for j in range(len(d[1][1])):
            trace.append(init_trace[j]-data[i-1][1][1][j])
        temp_diff.append(trace)
        time_collection.append(mdates.date2num(d[0]))

extent=[time_collection[0],time_collection[-1],depth[-1],depth[0]]
myplot=ax1.imshow(np.transpose(temp_diff[1:]),aspect='auto',extent=extent, \
                    vmin=cmap_lims[0],vmax=cmap_lims[1],interpolation='bilinear',cmap=colormap)

ax2.grid(True)

ax1.get_yaxis().set_visible(False)
cbar_ax = fig.add_axes([0.92, 0.15, 0.01, 0.75])
fig.colorbar(myplot,cax=cbar_ax)

ax1.set_xticklabels(ax1.xaxis.get_majorticklabels(), rotation=30,ha='right')
date_format = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(date_format)

ax2.set_ylabel("Depth MD, meter")
ax2.set_xlabel("Temperature, degC") 


plt.gcf().subplots_adjust(bottom=0.15)

plt.show()

    
    
