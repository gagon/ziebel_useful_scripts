# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 08:49:59 2015

@author: bolatzh
"""


"""===========================INPUT HEADER=================="""

main_dir=r'Y:\Data\US\CoP\Buck_Federal_17-5H\DTS\DTS_calibrated\calibrated_dts_files'
original_averaging=1
new_averaging=10
averaging_dir=r'Y:\Data\US\CoP\Buck_Federal_17-5H\DTS\DTS_calibrated\calibrated_dts_files'

"""===========================END---------=================="""


import os
import sys
import datetime
import numpy as np
import h5py

dt=datetime.datetime.strptime('2015/06/23 01:18:17',"%Y/%m/%d %H:%M:%S")

def write_to_dot_dts(data,i,averaging,average_trace):
    av_dts="%s_av_%s.dts" % (datetime.datetime.strftime(data[i][0],"%Y.%m.%d.%H.%M.%S"),str(averaging))
    
    textfile=open(os.path.join(os.path.join(averaging_dir,"average"),av_dts),'w')
    
    file_dt="TIMESTAMP: %s  \n" % datetime.datetime.strftime(data[i][0],"%Y/%m/%d %H:%M:%S")
    
    header=header1+file_dt+header2
    
    textfile.write("%s" % header)
    
    for line in average_trace:
        line=[str(j) for j in line]
        textfile.write("%s\n" % "\t".join(line))

def write_to_hdf(data_average,folder,averaging):
    
    traces=[]
    dt=[]    
    for data in data_average:
        dt.append(data[0])
        traces.append(data[1])
    
    copy_hdf=h5py.File(os.path.join(folder,"average_%smin.hdf" % str(averaging)), 'w-')
    
    copy_hdf.create_group('/Data/Calibrated_DTS/DTS/Averaged')
    
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['CLASS']='GROUP'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['TITLE']='GROUP'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['VERSION']='1.0'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['axis0_variety']='regular'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['axis1_variety']='regular'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['axis2_variety']='regular'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['block0_items_variety']='regular'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['encoding']='N.'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['nblocks']='1'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['ndim']='3'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['pandas_type']='wide'
    copy_hdf['/Data/Calibrated_DTS/DTS/Averaged'].attrs['pandas_version']='0.10.1'
    
    copy_hdf.create_dataset('/Data/Calibrated_DTS/DTS/Averaged/block0_values',data=traces)
    copy_hdf.create_dataset('/Data/Calibrated_DTS/DTS/Averaged/axis2',data=dt)
    copy_hdf.create_dataset('/Data/Calibrated_DTS/DTS/Averaged/axis0',data=dt)
    copy_hdf.create_dataset('/Data/Calibrated_DTS/DTS/Averaged/axis1',data=dt)
    copy_hdf.create_dataset('/Data/Calibrated_DTS/DTS/Averaged/block0_items',data=dt)
    copy_hdf.close()


if not new_averaging % original_averaging==0:
	print "orginal averaging is not divisible by averaging you want to apply. check your averaging! "    
	sys.exit()

averaging=new_averaging/original_averaging

data=[]

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
                    print dt,len(dt)
                    dt=datetime.datetime.strptime(dt,"%Y/%m/%d %H:%M:%S")
                    header_split=index

                if "~A" in line:                    
                    trace_start=index
                    header_end=index

                if index>trace_start:
                    small_list=[]
                    small_list.append(float(line.split("\t")[0]))
                    small_list.append(float(line.split("\t")[1][:-2]))
                    trace.append(small_list)
            
            trace=np.transpose(np.array(trace))            
            data.append([dt,trace])
            
            # get .dts file header
            dts_file=open(os.path.join(root,f),'r')
            lines=dts_file.readlines() 
            header1=""
            for i in range(header_split):
                header1+=lines[i]
            header2=""            
            for i in range(header_split+1,header_end+1):
                header2+=lines[i]

# sort fetched data by datetime
data=sorted(data, key=lambda x: x[0])

# make a folder for output
os.mkdir(os.path.join(averaging_dir,"average"))

data_average=[]

for i in range(0,len(data),averaging):
    
    if i+averaging<len(data):
        
        start_time=data[i][0]
        end_time=start_time+datetime.timedelta(minutes=averaging)
        prev_time=start_time-datetime.timedelta(minutes=averaging)
        delta_time_end=abs(data[i+averaging][0]-end_time).total_seconds()
        delta_time_prev=abs(data[i-averaging][0]-prev_time).total_seconds()
        
        print "=========="
        print "trace index: ", i
        print "averging period start time: ", start_time
        print "averging period calculated end time: ", end_time
        print "averging period actual end time: ", data[i+averaging][0]
        print "delta between actual and calculated: ",delta_time_end
        if i-averaging>=0:
            print "averging period calculated previous time: ", prev_time
            print "averging period actual previous time: ", data[i-averaging][0]
            print "delta between actual and calculated: ",delta_time_prev
        print "=========="
                
        if i-averaging>=0:
            print("first",delta_time_end,",",delta_time_prev,",",averaging)        
            if delta_time_end>60 or delta_time_prev>60:                
                print "something is wrong!!!"    
                print "delta_time is more than 60s"
                print "check your files"
                print start_time, 'here'
                sys.exit()            
        else:
            print("second",delta_time_end,",",delta_time_prev,",",averaging)
            if delta_time_end>60:                
                print "something is wrong!!!"    
                print "delta_time is more than 60s"
                print "check your files"
                print start_time
                sys.exit()
                
        average_trace=[]
    
        # looping through depth points
        for j in range(0,len(data[i][1][1])):	
            
            # looping through files in pile
            temps=[]
            for k in range(0,averaging):		
                temps.append(data[i+k][1][1][j])
            
            average_trace.append([data[i+k][1][0][j],np.mean(np.array(temps))])

        data_average.append([datetime.datetime.strftime(data[i][0],"%Y/%m/%d %H:%M:%S"),average_trace])
        
        write_to_dot_dts(data,i,averaging,average_trace)
         
    else:
        print "last pile of traces were less than averaging used, it was ignored"
        print "last pile traces start: %s" % str(data[i][0])
        print "last pile traces index: %s" % str(i)
        print "Total traces count: %s" % str(len(data))
        print "averaging used: %s" % str(new_averaging)


write_to_hdf(data_average,os.path.join(averaging_dir,"average"),averaging)

      

    
    
    
