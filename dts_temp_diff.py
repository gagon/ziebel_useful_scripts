# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 08:49:59 2015

@author: bolatzh
"""

"""========================================================="""
"""===========================INPUT HEADER=================="""



main_dir=r'P:\Data\Altus\HAL_FO-Cable-Interface-Test\DTS\Calibrated\Altus_cal_dts\Altus_cal_dts_hdf.hdf'

cmap_lims=[-0.6,0.6]

# can be set from: http://matplotlib.org/examples/color/colormaps_reference.html
colormap='jet'

hdf_group='Sep'
#hdf_group='Alldata'

plot_temp_unit="C" #F for farenheit
plot_depth_init="m" #ft for feet
plot_pres_unit="psi"

memgauge_use=False
memgauge_file=r'O:\Data\BP\A10\Memory-Gauge\A10_Memory-Gauge.txt'

depth_lim= -1 # if you want to specify depth write:[from, to]
temp_lim= -1 # if you want to specify temperature write:[from, to]

# Makes a gradient, calculated: degC/m
geoth_grad_use=False
dev=r'C:\Users\bolatzh\ownCloud\Buck_Federal_17-5H\Well_info\Deviation.csv'
dev_depth_unit="ft"
geoth_grad=0.01205
geoth_surf=30.0

# Moving window of the data in the hdf file
smooth=True
mov_av_num=5

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
import csv
import math
from matplotlib import cm
import matplotlib


def convert_depth(list_to_convert):
    if plot_depth_init=="ft":
        return np.array(list_to_convert)*3.2808
    else:
        return np.array(list_to_convert)

def convert_temp(list_to_convert):
    if plot_temp_unit=="F":
        return np.array(list_to_convert)*9.0/5.0+32.0
    else:
        return np.array(list_to_convert)


def read_mem_gauge(memgauge_file,pres_unit,temp_unit,start_time,end_time):
    # assumption is that mem gauge data is always in psia and degC
    mem=open(memgauge_file,'r')
    mem_dt=[]
    mem_pres=[]
    mem_temp=[]    
    for ind,line in enumerate(mem):
        d=line.split('\t')
        if len(d)>=4 and ':' in d[0] and ind>30:
            dt=datetime.datetime.strptime(d[0], '%Y.%m.%d %H:%M:%S')
            if dt>=start_time and dt<=end_time:
                mem_dt.append(matplotlib.dates.date2num(dt))
    #            mem_pres.append(float(d[4].replace(",",".")))
    #            mem_temp.append(float(d[6].replace(",",".")))
                mem_pres.append(float(d[2].replace(",",".")))
                mem_temp.append(float(d[3].replace(",",".")))            
    if plot_pres_unit=="bar":
        mem_pres=np.array(mem_pres)*0.0689475728
    elif plot_pres_unit=="kPa":
        mem_pres=np.array(mem_pres)*6.89475728
    if plot_temp_unit=="F":  
        mem_temp=np.array(mem_temp)*9.0/5.0+32.0
    return mem_dt,mem_pres,mem_temp


def moving_average(a, n) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    b=ret[n - 1:] / n
    add_val=int(n/2)
    b=np.insert(b,0,a[:add_val])
    b=np.insert(b,-1,a[(-1)*add_val:])
    return b


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

if smooth:
#    mov_av_num=5
    smoothed_data=[]
    for i in data:
        smoothed_data.append([i[0],[i[1][0],moving_average(i[1][1],mov_av_num)]])
    print len(moving_average(i[1][1],mov_av_num)),len(i[1][0])
    data=smoothed_data

if geoth_grad_use:

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
        md_arr=np.array(md_arr)/3.2808
        tvd_arr=np.array(tvd_arr)/3.2808                

    geoth_depth_md=data[0][1][0]
    geoth_depth_tvd=[]
    geoth_trace=[]
    for idx,md in enumerate(geoth_depth_md):        
        tvd=np.interp(md,md_arr,tvd_arr)
        
        temp=geoth_grad*tvd+geoth_surf        
        
#        print md,tvd,temp        
        
        geoth_trace.append([md,temp])        
        
        geoth_depth_tvd.append(tvd)
    geoth_trace=np.array(geoth_trace).T


if memgauge_use:
    mem_dt,mem_pres,mem_temp=read_mem_gauge(memgauge_file,plot_pres_unit,plot_temp_unit,data[1][0],data[-1][0])
        
# convert data to plot units
converted_data=[]
for i in data:
    converted_data.append([i[0],[convert_depth(i[1][0]),convert_temp(i[1][1])]])
data=converted_data

if geoth_grad_use:
    geoth_trace=[convert_depth(geoth_trace[0]),convert_temp(geoth_trace[1])]
    


# make plot
gs=gridspec.GridSpec(30,30)
fig=plt.figure(figsize=(18, 10))
ax2 = plt.subplot(gs[:22,:9])
ax1 = plt.subplot(gs[:22,10:], sharey=ax2)
if memgauge_use:
    ax3 = plt.subplot(gs[23:,10:], sharex=ax1)

temp_diff=[]
time_collection=[]

colors=list(iter(cm.jet(np.linspace(0,1,len(data)))))

for i,d in enumerate(data):       
    ax2.plot(np.array(d[1][1]),np.array(d[1][0]),color=colors[i],linewidth=0.5)
    if i==0:
        if geoth_grad_use:
            init_trace=geoth_trace[1]            
        else:
            init_trace=d[1][1]
        depth=d[1][0]                
    else:
        trace=[]
        for j in range(len(d[1][1])):
            trace.append(data[i-1][1][1][j]-init_trace[j])
        temp_diff.append(trace)
        time_collection.append(mdates.date2num(d[0]))

if geoth_grad_use:
    ax2.plot(geoth_trace[1],geoth_trace[0],'black',linewidth=4)

extent=[time_collection[1],time_collection[-1],depth[-1],depth[0]]
myplot=ax1.imshow(np.transpose(temp_diff[1:]),aspect='auto',extent=extent, \
                    vmin=cmap_lims[0],vmax=cmap_lims[1],interpolation='none',cmap=colormap)

ax2.grid(True)

ax1.get_yaxis().set_visible(False)
cbar_ax = fig.add_axes([0.92, 0.35, 0.01, 0.55])
fig.colorbar(myplot,cax=cbar_ax)

ax1.set_xticklabels(ax1.xaxis.get_majorticklabels(), rotation=30,ha='right')
date_format = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(date_format)
if depth_lim!=-1:
    ax2.set_ylim(depth_lim[1],depth_lim[0])
if temp_lim!=-1:
    ax2.set_xlim(temp_lim[0],temp_lim[1])

ax2.set_ylabel("Depth MD, %s" % plot_depth_init)
ax2.set_xlabel("Temperature, %s" % plot_temp_unit) 


plt.gcf().subplots_adjust(bottom=0.15)


if memgauge_use:
	mem_plot1,=ax3.plot(mem_dt,mem_pres,color='g',linestyle='-')    
	ax4= ax3.twinx()
	mem_plot2,=ax4.plot(mem_dt,mem_temp,color='r',linestyle='-')
	# set plot limits and titles
	ax1.get_xaxis().set_visible(False)
	ax3.set_xticklabels(ax3.xaxis.get_majorticklabels(), rotation=30,ha='right')
	ax3.xaxis_date()
	ax3.xaxis.set_major_formatter(date_format)
	ax3.yaxis.label.set_color(mem_plot1.get_color())
	ax3.tick_params(axis='y', colors=mem_plot1.get_color())
	ax3.set_ylabel("Pressure, %s" % plot_pres_unit)
	ax3.grid(True)
	ax4.yaxis.label.set_color(mem_plot2.get_color())
	ax4.tick_params(axis='y', colors=mem_plot2.get_color())
	ax4.set_ylabel("Temperature, %s" % plot_temp_unit)
	y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
	ax3.yaxis.set_major_formatter(y_formatter)
	ax4.yaxis.set_major_formatter(y_formatter)


plt.show()

    
    
