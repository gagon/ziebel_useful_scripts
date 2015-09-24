# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 09:10:08 2015

@author: bolatzh
"""


""" ============================================================================================== """
""" ============================================================================================== """
""" ======================= INPUT HEADER ========================================================= """



# BHP
well_name="CoP Buck Federal 17-5H"

# set data type for plotting, DAS or DTS
data_type='DAS'

#############################################
### INPUT FILES #############################


# files to plot
dev_file=r'Y:\Data\US\CoP\Buck_Federal_17-5H\Well_info\Deviation.csv'
memgauge_file=r'Y:\Data\US\CoP\Buck_Federal_17-5H\Memory_gauge\Memory_Gauge.txt'
completion_file=r'Y:\Data\US\CoP\Buck_Federal_17-5H\Well_info\Completion_BF_17_5H_noperfs.csv'
hdf_file=r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_processed\2015.08.06.00.12.02.hdf'

#hdf_file=r'Y:\Data\US\BHP\B5H\DTS\DTS_calibrated\Run2_old\B5H_cal_dts\Donnell_B5H_Run1_SEQSI2_AVG1M\average\average_10min.hdf'



#############################################
### DAS SETTINGS ############################

# processing ('new' or 'old')
processing='new'
# set frequency band to plot
frequency_band=1
# intensity scales in dB
das_scale_min=10
das_scale_max=50
# DAS file attrs
numblocks=9.765625
das_offset=-72
das_timeshift=-5

#############################################
### DTS SETTINGS ############################

# DTS hdf group name to plot
dts_group='Averaged'
# temperature scale in degC
dts_scale_min=270
dts_scale_max=292

#############################################
### GENERAL SETTINGS ########################

# animation speed
speed=0.05
animation_step=10

# True or False if you want or don't want memory gauge plot
memgauge=True
# units of input and plotting 
dev_depth_unit='ft'
compl_depth_unit='ft'
plot_depth_unit='ft'
# plot window (in plot_depth_unit)
xlim_min=-5000
xlim_max=10000
ylim_min=-1000
ylim_max=14000

# scales to increase/decrease distance of signal/scales from well
data_scale=30
tick_scale=800
compl_scale=200
perf_scale=50
md_ticks=1000       
# coordinates of datetime on the plot (in plot_depth_unit)
dt_annot_coord=[2500,2500]
# test=True for testing or test=False for animation
test=False
# pressure,temperature plotting units 
# pressure: "psi","kPa","bar"
# temperature: "degC","degF"
pres_unit='psi'
temp_unit='degF'
# memory gauge limits (in plotting units)
pres_lim=[4015,4030]
temp_lim=[144.1,144.4]





""" ============================================================================================== """
""" ============================================================================================== """
""" =============================== DO NOT EDIT CODE BELOW THIS POINT ============================ """





import numpy as np
import math
import matplotlib.pyplot as plt
import time
import h5py
import os
import matplotlib.gridspec as gridspec
import datetime
import matplotlib
import sys
from matplotlib.widgets import Button



def getDASdataMod(hdffile,numblocks,depth_offset):

    blocklength = 1024
    depth_start=0
    time_offset=0

    depth_resol_m = float(hdffile['RAWdata/DASdata/FDSdata'].attrs.__getitem__('DataLocusSpacing_m'))
    fsampling = float(hdffile['RAWdata/DASdata/FDSdata'].attrs.__getitem__('TimeStepFrequency_Hz'))
    time_resol_sec = (blocklength*numblocks)/fsampling

    return (time_resol_sec,time_offset,depth_resol_m,depth_offset,depth_start)

def getDASdataMod2(hdffile,numblocks,depth_offset):

    blocklength = 1024
    depth_start=0
    time_offset=0

    depth_resol_m = float(hdffile['data'].attrs.__getitem__('depthspacing'))
    fsampling = float(hdffile['data'].attrs.__getitem__('samplerate'))
    time_resol_sec = (blocklength*numblocks)/fsampling

    return (time_resol_sec,time_offset,depth_resol_m,depth_offset,depth_start)


def read_dev_file(dev_file):
    f=open(dev_file,'r')    
    dev=[]
    for ind,line in enumerate(f):        
        if ind>0:            
            r=[]            
            for l in line.split(","):
                if '\n' in l:
                    r.append(l.rstrip('\n'))
                else:
                    r.append(l)
            if dev_depth_unit=='ft':
                r[0]=float(r[0])/3.2808
            elif dev_depth_unit=='m':
                r[0]=float(r[0])                
            dev.append([r[0],float(r[1])])
    return dev

def read_completions(completion_file):
    f=open(completion_file,'r')    
    compl=[]
    for ind,line in enumerate(f):
        row=line.split(";")
        if row[2]=='barrier':
            compl.append([float(row[5]),'barrier',row[4]])
        elif row[2]=='perforation':
            compl.append([float(row[5]),'perf',row[4]])
    return compl
            
            
            
def unit_converter(arr,unit_in,unit_out):
    if unit_in=='m' and unit_out=='ft':  
        converter=3.2808
        new_arr=[]
        for a in arr:
            new_arr.append(a*converter)
        return new_arr
    elif unit_in=='m' and unit_out=='m':
        return arr

def read_mem_gauge(memgauge_file,pres_unit,temp_unit):
    # assumption is that mem gauge data is always in psia and degC
    mem=open(memgauge_file,'r')
    mem_dt=[]
    mem_pres=[]
    mem_temp=[]    
    for ind,line in enumerate(mem):
        d=line.split('\t')
        if len(d)>=4 and ':' in d[0] and ind>30:
            mem_dt.append(matplotlib.dates.date2num(
                datetime.datetime.strptime(d[0], '%Y.%m.%d %H:%M:%S')))
#            mem_pres.append(float(d[4].replace(",",".")))
#            mem_temp.append(float(d[6].replace(",",".")))
            mem_pres.append(float(d[2].replace(",",".")))
            mem_temp.append(float(d[3].replace(",",".")))            
    if pres_unit=="bar":
        mem_pres=np.array(mem_pres)*0.0689475728
    elif pres_unit=="kPa":
        mem_pres=np.array(mem_pres)*6.89475728
    if temp_unit=="degF":  
        mem_temp=np.array(mem_temp)*9.0/5.0+32.0
    return mem_dt,mem_pres,mem_temp


def start_anim(self):
    print 'button clicked'
    plt.show(block=False)
    
    
def animate(self):

    curve1_ax=[]
    timeline_line=[]
    timeline_line2=[]

    # check if test then make 1 iteration else animate
    if test:
        iterations=1
    else:
        iterations=len(data)
        # make figure visually appear
        plt.show(block=False)
 
    
    
    for k in range(0,iterations,animation_step):
        if k>0:
            curve1_ax.pop(0).remove()         
            timeline_line.pop(0).remove()
            if memgauge:
                timeline_line2.pop(0).remove()

        trace=data[k]
        curve1=[]
        for ind,t in enumerate(trace):
            x=trace_xaxis[ind]
            y=trace_tvd[ind]
            if t>=scale_min:
                x_diff=(t-scale_min)*data_scale*abs(math.cos(math.radians(trace_angle[ind])))
                y_diff=(t-scale_min)*data_scale*abs(math.sin(math.radians(trace_angle[ind])))
                curve1.append([x-x_diff,y+y_diff])
            else:
                curve1.append([x,y])
        curve1=np.transpose(np.array(curve1))
    
        if data_type=='DAS':        
            curve1_ax=ax.plot(curve1[0],curve1[1],color='g',linestyle='-',linewidth=0.3)
            cur_datetime=datetime.datetime.strptime(time_start,'%Y.%m.%d.%H.%M.%S')+ \
                        datetime.timedelta(seconds=k*float(time_resol_sec))+datetime.timedelta(hours=das_timeshift)
                        
        elif data_type=='DTS':
            curve1_ax=ax.plot(curve1[0],curve1[1],color='g',linestyle='-',linewidth=1)
            cur_datetime=datetime.datetime.strptime(timestamps[k],'%Y/%m/%d %H:%M:%S')
        timeline_line=ax2.plot([matplotlib.dates.date2num(cur_datetime), \
                                matplotlib.dates.date2num(cur_datetime)], \
                                [timeline_ymin,timeline_ymax],color='red',linestyle='-',linewidth=3)
                                
        if memgauge:
            timeline_line2=ax3.plot([matplotlib.dates.date2num(cur_datetime), \
                                matplotlib.dates.date2num(cur_datetime)], \
                                [timeline_ymin,timeline_ymax],color='red',linestyle='-',linewidth=3)                            
        
        if iterations>1:
            plt.draw()
            time.sleep(speed)
        else:
            plt.show()   
            
    curve1_ax.pop(0).remove()         
    timeline_line.pop(0).remove()
    if memgauge:
        timeline_line2.pop(0).remove()


def update_imshow(self):
    xlim_min=ax.get_xlim()[0]
    xlim_max=ax.get_xlim()[1]
    ylim_min=ax.get_ylim()[1]
    ylim_max=ax.get_ylim()[0] 
    imshow_depth_min=1e10
    imshow_depth_max=0
    for i,d in enumerate(trace_tvd):
        if trace_tvd[i]<=ylim_max and trace_tvd[i]>=ylim_min:
            if trace_xaxis[i]<=xlim_max and trace_xaxis[i]>=xlim_min:
                if trace_depth[i]<=imshow_depth_min:
                    imshow_depth_min=trace_depth[i]
                if trace_depth[i]>=imshow_depth_max:
                    imshow_depth_max=trace_depth[i]
    ax2.set_ylim(imshow_depth_max,imshow_depth_min)
    plt.draw()



# read deviation file
dev=read_dev_file(dev_file)
compl=read_completions(completion_file)


# calculate tvds and xaxis from dev
md=[]
tvd=[]
xaxis=[]
angle=[]
for ind,point in enumerate(dev):
    if ind==0:
        md.append(point[0])
        tvd.append(point[0])
    else:
        md.append(point[0])
        md_diff=point[0]-md[ind-1]
        slope=math.cos(math.radians((dev[ind-1][1]+dev[ind][1])/2.0))        
        tvd_diff=slope*md_diff
        tvd.append(tvd[ind-1]+tvd_diff)
    xaxis.append(md[ind]-tvd[ind])
    angle.append(dev[ind][1])


if data_type=='DTS':
    hdf=h5py.File(hdf_file, 'r')
    dts_group='/Data/Calibrated_DTS/DTS/'+dts_group
    data=np.transpose(np.transpose(hdf[dts_group+'/block0_values'][...])[1])
    if temp_unit=='degF':
        data=np.array(data)*9.0/5.0+32.0
    timestamps=hdf[dts_group+'/axis2'][...]
    trace_depth=np.transpose(np.transpose(hdf[dts_group+'/block0_values'][...])[0])[0]
    
elif data_type=='DAS':
    # fetching DAS data and attrs
    hdf=h5py.File(hdf_file, 'r')
    if processing=='old':
        hdf_attrs=getDASdataMod(hdf,numblocks,das_offset)
        data=hdf['/OUTdata/DASdata/OCTdata/13Octaves/13Octaves'][:,:,frequency_band]
    elif processing=='new':
        hdf_attrs=getDASdataMod2(hdf,numblocks,das_offset)
        data=hdf['data'][:,:,frequency_band]
    time_resol_sec=hdf_attrs[0]
    time_offset=hdf_attrs[1]
    time_start=os.path.splitext(os.path.split(hdf_file)[1])[0]
    depth_resol_m=hdf_attrs[2]
    depth_offset=hdf_attrs[3]
    depth_start=hdf_attrs[4]
    trace_depth=np.array([i*depth_resol_m+das_offset for i in range(len(data[0]))])
    
    # QC
    if len(data[0])*depth_resol_m+das_offset>md[-1]:
        print "well length in DAS (%s,m) > deviation file (%s,m)!" % (len(data[0])*depth_resol_m,md[-1])
        print "plotting stopped"
        sys.exit()

# define reference curve for trace
trace_tvd=np.interp(trace_depth,md,tvd)
trace_xaxis=np.interp(trace_depth,md,xaxis) 


# define inclination angle for the curve
trace_angle=[]
for ind,t in enumerate(trace_depth):
    if ind==0:
        trace_angle.append(0)
    else:            
        x_p1=trace_xaxis[ind-1]
        x_p2=trace_xaxis[ind]
        y_p1=trace_tvd[ind-1]
        y_p2=trace_tvd[ind]                        
        trace_angle.append(math.degrees(math.atan((x_p2-x_p1)/(y_p2-y_p1))))


# convert all array depth units to plot_depth_units
trace_depth=unit_converter(trace_depth,'m',plot_depth_unit)
trace_tvd=unit_converter(trace_tvd,'m',plot_depth_unit)
trace_xaxis=unit_converter(trace_xaxis,'m',plot_depth_unit)
md=unit_converter(md,'m',plot_depth_unit)
tvd=unit_converter(tvd,'m',plot_depth_unit)
xaxis=unit_converter(xaxis,'m',plot_depth_unit)


# reference curve for scales
trace_scale_md=[sc for sc in range(0,int(trace_depth[-1]),md_ticks)]



# define start and end times
if data_type=='DAS':    
    time_start_dt=datetime.datetime.strptime(time_start,'%Y.%m.%d.%H.%M.%S')+datetime.timedelta(hours=das_timeshift)
    time_end_dt=time_start_dt+datetime.timedelta(seconds=len(data)*float(time_resol_sec))    
elif data_type=='DTS':    
    time_start_dt=datetime.datetime.strptime(timestamps[0],'%Y/%m/%d %H:%M:%S')
    time_end_dt=datetime.datetime.strptime(timestamps[-1],'%Y/%m/%d %H:%M:%S')
time_start_mt=matplotlib.dates.date2num(time_start_dt)   
time_end_mt=matplotlib.dates.date2num(time_end_dt)

# limits for imshow
extent=[time_start_mt,time_end_mt,trace_depth[-1],trace_depth[0]]

# check if limits are for DAS or DTS
if data_type=='DAS':    
    scale_min=das_scale_min
    scale_max=das_scale_max
elif data_type=='DTS':
    scale_min=dts_scale_min
    scale_max=dts_scale_max


# define imshow max min depending on plot window
imshow_depth_min=1e10
imshow_depth_max=0
for i,d in enumerate(trace_tvd):
    if trace_tvd[i]<=ylim_max and trace_tvd[i]>=ylim_min:
        if trace_xaxis[i]<=xlim_max and trace_xaxis[i]>=xlim_min:
            if trace_depth[i]<=imshow_depth_min:
                imshow_depth_min=trace_depth[i]
            if trace_depth[i]>=imshow_depth_max:
                imshow_depth_max=trace_depth[i]



# create figures and subplots
if memgauge:
    fig = plt.figure(figsize=(18, 10))
    gs=gridspec.GridSpec(10,40)
    ax = plt.subplot(gs[:,:23])
    ax2 = plt.subplot(gs[:7,26:])
    ax3 = plt.subplot(gs[7:,26:])
else:
    fig = plt.figure(figsize=(10, 12))
    gs=gridspec.GridSpec(40,1)
    ax = plt.subplot(gs[:26,:])
    ax2 = plt.subplot(gs[28:,:])

# plot the well path
lines=ax.plot(xaxis,tvd,color='#A52A2A',linestyle='-',linewidth=5)

    
# plot colormap of data    
timeline=ax2.imshow(np.transpose(data),aspect="auto",extent=extent,vmin=scale_min,vmax=scale_max)



# set plot limits and titles
ax.set_ylim(ylim_max,ylim_min)
ax.set_xlim(xlim_min,xlim_max) 
ax.grid(True)
ax.set_ylabel("Depth TVD, %s" % plot_depth_unit)
ax.set_xlabel("X-axis, %s" % plot_depth_unit) 
ax2.set_ylabel("Depth MD, %s" % plot_depth_unit)
ax2.set_ylim(imshow_depth_max,imshow_depth_min)
ax2.set_xlim(time_start_mt,time_end_mt)
ax2.set_xticklabels(ax2.xaxis.get_majorticklabels(), rotation=30,ha='right')
ax2.xaxis_date()
date_format = matplotlib.dates.DateFormatter('%b.%d %H:%M:%S')
ax2.xaxis.set_major_formatter(date_format)
if memgauge:
    cbar_ax = fig.add_axes([0.92, 0.35, 0.01, 0.55])
else:
    cbar_ax = fig.add_axes([0.92, 0.1, 0.01, 0.24])
cbar = plt.colorbar(timeline, cax=cbar_ax)

if memgauge:
    # read memory gauge data
    mem_dt,mem_pres,mem_temp=read_mem_gauge(memgauge_file,pres_unit,temp_unit)
    # plot the well
    mem_plot1,=ax3.plot(mem_dt,mem_pres,color='g',linestyle='-')    
    ax4= ax3.twinx()
    mem_plot2,=ax4.plot(mem_dt,mem_temp,color='r',linestyle='-')
    # set plot limits and titles
    ax2.get_xaxis().set_visible(False)
    ax3.set_xticklabels(ax3.xaxis.get_majorticklabels(), rotation=30,ha='right')
    ax3.xaxis_date()
    ax3.xaxis.set_major_formatter(date_format)
    ax3.yaxis.label.set_color(mem_plot1.get_color())
    ax3.tick_params(axis='y', colors=mem_plot1.get_color())
    ax3.set_xlim(time_start_mt,time_end_mt)
    ax3.set_ylabel("Pressure, %s" % pres_unit)
    ax3.grid(True)
    ax3.set_ylim(pres_lim[0],pres_lim[1])
    ax4.yaxis.label.set_color(mem_plot2.get_color())
    ax4.tick_params(axis='y', colors=mem_plot2.get_color())
    ax4.set_xlim(time_start_mt,time_end_mt)
    ax4.set_ylabel("Temperature, %s" % temp_unit)
    ax4.set_ylim(temp_lim[0],temp_lim[1])
    y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
    ax3.yaxis.set_major_formatter(y_formatter)
    ax4.yaxis.set_major_formatter(y_formatter)


# this is for timeline_line that show where the trace is on colormap
timeline_ymin=trace_depth[0]
timeline_ymax=trace_depth[-1]


# create depth scale along the well path
for ind,p in enumerate(trace_scale_md):
    x=np.interp(p,md,xaxis)
    y=np.interp(p,md,tvd)
    if trace_scale_md[ind]-100>=md[0] and trace_scale_md[ind]+100<=md[-1]:
        if ind==0:
            angle_cur=np.interp(trace_scale_md[ind],md,angle)
            offset_x=tick_scale*math.cos(math.radians(angle_cur))
            offset_y=tick_scale*math.sin(math.radians(angle_cur))
        else:   
            x_p1=np.interp(trace_scale_md[ind]-100,md,xaxis)
            x_p2=np.interp(trace_scale_md[ind]+100,md,xaxis)
            y_p1=np.interp(trace_scale_md[ind]-100,md,tvd)
            y_p2=np.interp(trace_scale_md[ind]+100,md,tvd)      
            angle_cur=math.degrees(math.atan((x_p2-x_p1)/(y_p2-y_p1)))
            offset_x=tick_scale*math.cos(math.radians(angle_cur))
            offset_y=tick_scale*math.sin(math.radians(angle_cur))
        annot_coord=(x-offset_x,y+offset_y)
        ax.annotate(str(trace_scale_md[ind])+str(plot_depth_unit),annot_coord,fontsize=8, \
                    horizontalalignment='right', verticalalignment='center')   
        ax.plot([x,x-offset_x],[y,y+offset_y],color='grey',linestyle='-',linewidth=1)       

# create completions along the well path
for ind,item in enumerate(compl):
    x=np.interp(item[0],md,xaxis)
    y=np.interp(item[0],md,tvd)
    if item[0]-100>=md[0] and item[0]+100<=md[-1]:
        if item[1]=='perf': 
            if ind==0:
                angle_cur=np.interp(item[0],md,angle)
                offset_x=tick_scale/10.0*abs(math.cos(math.radians(angle_cur)))
                offset_y=tick_scale/10.0*abs(math.sin(math.radians(angle_cur)))
            else:   
                x_p1=np.interp(item[0]-100,md,xaxis)
                x_p2=np.interp(item[0]+100,md,xaxis)
                y_p1=np.interp(item[0]-100,md,tvd)
                y_p2=np.interp(item[0]+100,md,tvd)      
                angle_cur=math.degrees(math.atan((x_p2-x_p1)/(y_p2-y_p1)))
                offset_x=perf_scale*abs(math.cos(math.radians(angle_cur)))
                offset_y=perf_scale*abs(math.sin(math.radians(angle_cur)))     
                
            ax.plot([x+offset_x,x-offset_x],[y-offset_y,y+offset_y],color='red',linestyle='-',linewidth=1) 
            
        elif item[1]=='barrier':
            if ind==0:
                angle_cur=np.interp(item[0],md,angle)
                offset_x=compl_scale*abs(math.cos(math.radians(angle_cur)))
                offset_y=compl_scale*abs(math.sin(math.radians(angle_cur)))
            else:   
                x_p1=np.interp(item[0]-100,md,xaxis)
                x_p2=np.interp(item[0]+100,md,xaxis)
                y_p1=np.interp(item[0]-100,md,tvd)
                y_p2=np.interp(item[0]+100,md,tvd)      
                angle_cur=math.degrees(math.atan((x_p2-x_p1)/(y_p2-y_p1)))
                offset_x=compl_scale*abs(math.cos(math.radians(angle_cur)))
                offset_y=compl_scale*abs(math.sin(math.radians(angle_cur)))     
            if ind % 2 == 0:
                annot_coord=(x+offset_x,y-offset_y)
                ax.annotate(str(item[2]),annot_coord,fontsize=8, \
                            horizontalalignment='left', verticalalignment='center')   
                ax.plot([x,x+offset_x],[y,y-offset_y],color='b',linestyle='-',linewidth=1) 
            else:
                annot_coord=(x-offset_x,y+offset_y)
                ax.annotate(str(item[2]),annot_coord,fontsize=8, \
                            horizontalalignment='right', verticalalignment='center')   
                ax.plot([x,x-offset_x],[y,y+offset_y],color='b',linestyle='-',linewidth=1) 
                


# create intensity scale along the well path
scale_curve1=[]
scale_curve2=[]
for ind,t in enumerate(trace_tvd):
    x=trace_xaxis[ind]
    y=trace_tvd[ind]
    x_diff=(scale_max-scale_min)*data_scale*abs(math.cos(math.radians(trace_angle[ind])))
    y_diff=(scale_max-scale_min)*data_scale*abs(math.sin(math.radians(trace_angle[ind])))
    scale_curve1.append([x-x_diff,y+y_diff])
    scale_curve2.append([x-x_diff/2.0,y+y_diff/2.0])
scale_curve1=np.transpose(np.array(scale_curve1))
scale_curve2=np.transpose(np.array(scale_curve2))

scale_curve1_ax=ax.plot(scale_curve1[0],scale_curve1[1],color='grey',linestyle='-',linewidth=1)
scale_curve2_ax=ax.plot(scale_curve2[0],scale_curve2[1],color='grey',linestyle='-',linewidth=1)
if data_type=='DAS':
    scale_unit='dB'
elif data_type=='DTS':
    scale_unit=temp_unit
    
scale_max_annot1=ax.annotate(str(scale_max)+scale_unit,(scale_curve1[0][-1]+50,scale_curve1[1][-1]), \
                                    fontsize=8,horizontalalignment='left', verticalalignment='center')
scale_max_annot2=ax.annotate(str((scale_max+scale_min)/2)+scale_unit,(scale_curve2[0][-1]+50,scale_curve2[1][-1]), \
                                    fontsize=8,horizontalalignment='left', verticalalignment='center')
scale_min_annot=ax.annotate(str(scale_min)+scale_unit,(trace_xaxis[-1]+50,trace_tvd[-1]),fontsize=8,verticalalignment='center')

# set title of the figure
if data_type=='DAS':
    ax.set_title("Well %s / Frequency band: %s" % (well_name,frequency_band))
elif data_type=='DTS':
    ax.set_title("Well %s / DTS group: %s" % (well_name,dts_group))


# define non-default arguments
if data_type=='DTS':
    time_start=0
    time_resol_sec=0
    




axplay = plt.axes([0.79, 0.91, 0.05, 0.05])
axupdate = plt.axes([0.85, 0.91, 0.05, 0.05])
playbut = Button(axplay, 'Play',color='green')
playbut.on_clicked(animate)
updatebut = Button(axupdate, 'Update',color='green')
updatebut.on_clicked(update_imshow)




plt.show()

##
#print xlims,ylims










