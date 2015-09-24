# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 08:49:59 2015

@author: bolatzh
"""

"""========================================================="""
"""===========================INPUT HEADER=================="""


#main_dir='/mnt/A1-Data1/Data/BP/A14/DTS/DTS_calibrate_new/test'
#main_dir='/mnt/A1-Data1/Data/BP/A14/Vintage-DTS-DAS-Case-Study-from-the-North-Sea/DTS/2014/A14_dts_merged.hdf'
#main_dir='/mnt/A1-Data1/Data/BP/A14/Vintage-DTS-DAS-Case-Study-from-the-North-Sea/DTS/2014/A14_cal_dts_hdf.hdf'
#main_dir='/mnt/A1-Data1/Data/BP/A14/Vintage-DTS-DAS-Case-Study-from-the-North-Sea/DTS/2014/BP_A14_BLExC1_AVG1_/dts_files'
#main_dir='/mnt/A1-Data1/Data/BP/A14/Vintage-DTS-DAS-Case-Study-from-the-North-Sea/DTS/2014/DTS_Calibrated_Data'
#main_dir='/mnt/A1-Data1/Data/BP/A14/DTS/DTS_calibrate_new/A14_cal_dts.hdf'
main_dir='/mnt/A3-Data1/Data/CoP/A-30/DTS/DTS_Calibrated/A30_cal_dts'


out_folder='/mnt/A1-Data1/Data/BP/A14/Vintage-DTS-DAS-Case-Study-from-the-North-Sea/DTS/2014/BP_A14_BLExC1_AVG1_'

cmap_lims=[-2.0,2.0]
colormap='jet'

# optional, set only if using hdf
#hdf_group='Merged'
hdf_group='Alldata'
#hdf_group='BP_A14_BLExC1_AVG1_'
trace_num=1
depth_num=1

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
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from mayavi import mlab


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
                        small_list=[]
                        small_list.append(float(line.split("\t")[0]))
                        small_list.append(float(line.split("\t")[1]))
                        trace.append(small_list)
    
                
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

temp_diff=[]
time=[]

depth=data[0][1][0][::depth_num]

for i,d in enumerate(data[::trace_num]):           

    if not all(np.array(d[1][1])==0):
        print np.array(d[1][1]) ,all(np.array(d[1][1])==0)
#        trace=[]
#        for j in range(0,len(d[1][1]),depth_num):
#            trace.append(data[i-1][1][1][j])

        temp_diff.append(d[1][1])
        time.append(mdates.date2num(d[0]))


#for i,d in enumerate(data[::trace_num]):           
#    if i==0:
#        init_trace=d[1][1]        
#    else:
#        
#        if not all(np.array(d[1][1])==0):
#            print np.array(d[1][1]) ,all(np.array(d[1][1])==0)
#            trace=[]
#            for j in range(0,len(d[1][1]),depth_num):
#                trace.append(data[i-1][1][1][j]-init_trace[j])
#            temp_diff.append(trace)
#            time.append(mdates.date2num(d[0]))



#ax = fig.gca(projection='3d')

x,y=np.meshgrid(depth,time)

a=mlab.surf(temp_diff,warp_scale='auto')

mlab.scalarbar(a, title='scale', orientation=None, nb_labels=None, nb_colors=None, label_fmt=None)
a.actor.actor.scale = (3.0, 1.0, 10.0)

#ax.plot_surface(x,y, temp_diff, cmap=colormap, rstride=1, cstride=1, alpha=1,linewidth=0, antialiased=False)
#cset = ax.contour(x,y, temp_diff, zdir='z', offset=-5, cmap=cm.coolwarm)
#cset = ax.contour(x,y, temp_diff, zdir='x', offset=-100, cmap=cm.coolwarm)
#cset = ax.contour(x,y, temp_diff, zdir='y', offset=time[-1]+1.0, cmap=cm.coolwarm)

#date_format = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
#ax.yaxis_date()
#ax.yaxis.set_major_formatter(date_format)
#ax.set_xlabel('Depth, m')
#ax.set_zlabel('Temperature difference, degC')

#ax.view_init(elev=60., azim=275)
#plt.show()

#for ii in xrange(0,360,10):
#        ax.view_init(elev=60., azim=ii)
#        fig.savefig(os.path.join(out_folder,'3d_plot_angle' +str(ii)+".png"))
    
    
