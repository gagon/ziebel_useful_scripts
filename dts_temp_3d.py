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
main_dir='/mnt/A4-Data1/Data/Daleel/Case_Study_Oman/BR_13/Poster_Case-Study_BR13_DALEEL/DTS/Calibrated/BR-13_cal_dts/A14_dts_merged.hdf'

plot_type="temp_diff"

# optional, set only if using hdf
hdf_group='Merged'


"""===========================END==========================="""
"""========================================================="""







import os
import sys
import datetime
import numpy as np
import h5py
import matplotlib.dates as mdates
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


depth=data[0][1][0]

if plot_type=="temp":
	
	temp=[]
	time=[]

	for i,d in enumerate(data):           
		if not all(np.array(d[1][1])==0):
			if i==0:
				init_time=mdates.date2num(d[0])
				time.append(0.0)            
			else:            
				time.append(mdates.date2num(d[0])-init_time)
			temp.append(d[1][1])

elif plot_type=="temp_diff":
			
	temp=[]
	time=[]


	for i,d in enumerate(data):           
		if not all(np.array(d[1][1])==0):
			if i==0:
				init_time=mdates.date2num(d[0])
				time.append(0.0)     
				temp_init=d[1][1]
				temp.append(np.zeros(len(temp_init)))
				       
			else:            
				trace=[]
				for x,t in enumerate(d[1][1]):
					trace.append(t-temp_init[x])
				time.append(mdates.date2num(d[0])-init_time)
				temp.append(trace)

print np.array(temp).shape,np.array(time).shape,np.array(depth).shape
		
		
x,y=np.meshgrid(time,depth)
print x.shape,y.shape


fig = mlab.figure(size=(1000,800))

myplot=mlab.surf(x.T,y.T,np.flipud(temp),extent = [0,1,0,1,0,0.3])

cb=mlab.scalarbar(myplot, title='Temperature', orientation='vertical', nb_labels=None, nb_colors=None, label_fmt='%.1f')

ax=mlab.axes(xlabel='time,days',ylabel='depth,mMD',nb_labels=5,x_axis_visibility=True,y_axis_visibility=False,z_axis_visibility=True,\
    ranges = [np.amax(np.array(time)),np.amin(np.array(time)),np.amin(np.array(depth)), np.amax(np.array(depth)),np.amin(np.array(temp)), np.amax(np.array(temp))])

ax.axes.label_format = '%.1f'
ax.axes.font_factor=0.7
mlab.show()




