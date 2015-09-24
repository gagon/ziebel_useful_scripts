# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 11:27:12 2014

@author: bolat
"""

"""========================================================================================="""
"""========================================================================================="""
""" Input header """

# input files
dts_fullpath= r'M:\Data\KiM_DTS_Investigation\Test3_new_sensornet_calibration\Calibrated\calibrated_dts_files'      # folder with .dts files
memgauge_fullpath= r'M:\Data\KiM_DTS_Investigation\Test3_new_sensornet_calibration\US00015.txt'
pt_fullpath = r'M:\Data\KiM_DTS_Investigation\Test3_new_sensornet_calibration\PT-100.txt'


# settings for plot
# dts trace index interval to average and compare with memgauge 
# -1 means last, -5 5th from bottom
trace_index=[-5948,-5962] # [bottom_index,upper_index] 
time_shift=0 # time difference between dts and memgauge in hours
plot_title='DTS Investigation'

"""========================================================================================="""
"""========================================================================================="""




import h5py
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

def read_from_hdf(dts_path):
    print 'reading from hdf file..'
    print trace_index 
    
    # open hdf
    dts_hdf = h5py.File(dts_path,'r')
        
    #get list of dts groups  
    dts_group_list=[] 
    dts_key_list=dts_hdf['Data/Calibrated_DTS/DTS/'].keys() 
    for gr in dts_key_list:
        dts_group_list.append('Data/Calibrated_DTS/DTS/'+gr)
        
    # iterate through groups
    dts=pd.DataFrame() # empty table
    for gr in dts_group_list:
        
        # get timestamps
        timestamps=dts_hdf[gr+'/axis2'][...]
        timestamps_mt=[]    
        for t in timestamps:
            timestamps_mt.append(matplotlib.dates.date2num(datetime.datetime.strptime(t, "%Y/%m/%d %H:%M:%S")))
        timestamps_mt=np.array(timestamps_mt)
        # get temperature and cut it to index range specified
        temp_arr=np.transpose(np.transpose(dts_hdf[gr+'/block0_values'][...])[1][trace_index[1]:trace_index[0]])
        # average the index range temperature values in to 1 value
        temperature=[]
        for temp in temp_arr:
            temperature.append(np.average(np.array(temp)))
        temperature=np.array(temperature)
        # append to pd table
        dts=dts.append(pd.DataFrame({'timestamps':timestamps_mt,'temperature':temperature}))

    # sort table on timestamp
    dts=dts.sort(['timestamps'])
    dts_hdf.close()
        
    return dts

def read_from_dtsext(dts_path):
    print 'reading from .dts files..'
    print trace_index    
    
    timestamp=[]
    temperature=[]
    for root, dirs, files in os.walk(dts_path):
        for f in files:
            if f.endswith('.dts'):

                # get file and folder names
                head, ext = os.path.splitext(f)
                dts_file=os.path.join(root, f)
                file=open(dts_file,'r')
                
                # iterate through lines to get timestamp and the trace 
                trace=[]                
                for ind,line in enumerate(file):
                    if "TIMESTAMP" in line:
                        timestamp.append(matplotlib.dates.date2num(
                                datetime.datetime.strptime(" ".join(line.split(' ')[1:3]), "%Y/%m/%d %H:%M:%S")))
                    if ind>12: # assumption that trace starts from line 13
                        trace.append([float(line.split('\t')[0]),                  # depth
                                      float(line.split('\t')[1].split('\n')[0])])  # temperature                
                trace=np.transpose(np.array(trace))
                trace=pd.DataFrame({'depth':trace[0],'temperature':trace[1]})
                
                # sort trace on depth
                trace=trace.sort(['depth'])
                
                # take index interval and average
                temperature.append(np.average(trace.iloc[trace_index[1]:trace_index[0]]['temperature']))
    
    # put into table and sort
    dts=pd.DataFrame({'timestamps':timestamp,'temperature':temperature})   
    dts=dts.sort(['timestamps'])
    
    return dts


def readmemgauge(mem_gau_file):
    print 'Reading Memory gauge file...'
    
    UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0)
    
    timestamps = []
    seconds = []
    pressure = []
    temperature = []

    with open(mem_gau_file, 'rb') as csvfile:
        print mem_gau_file
        dataflag = 0
        headerlct = 0
        for idx,line in enumerate(csvfile):
            if line == '\r\n': #when a blank line is reached col seperator is changed
                dataflag = 1
                continue
            if dataflag == 1:
                d = line.split()
                headerlct += 1
                if headerlct > 3:
                    d = line.split()
                    if idx<20:
                        print d
                    timestamps.append(matplotlib.dates.date2num(
                        datetime.datetime.strptime(d[0] + ' ' + d[1], '%Y.%m.%d %H:%M:%S')))
                    seconds.append((datetime.datetime.strptime(d[0] + ' ' + d[1], '%Y.%m.%d %H:%M:%S') - UNIX_EPOCH).total_seconds())
                    pressure.append(float(d[3].replace(",",".")))
                    temperature.append(float(d[4].replace(",",".")))
    
    mem=pd.DataFrame({'timestamps':timestamps,'temperature':temperature})   
    mem=mem.sort(['timestamps'])
    
    return mem



if __name__=="__main__":
    
    if '.hdf' in dts_fullpath:    
        dts=read_from_hdf(dts_fullpath)
    else:
        dts=read_from_dtsext(dts_fullpath)
        
    mem=readmemgauge(memgauge_fullpath)
    mem2=readmemgauge(pt_fullpath)
    #print mem2
    # test by ploting data
    fig, ax = plt.subplots(figsize=(18, 8))        
    ax.plot(dts['timestamps'],dts['temperature'],'.',label='DTS')
    ax.plot(mem['timestamps'],mem['temperature'],'.',label='Memory gauge')    
    ax.plot(mem2['timestamps'],mem2['temperature'],'r.',label='pt gauge')
    plt.legend()
    ax.set_ylabel('Temperature (degC)',fontsize=16)    
    ax.set_title(plot_title,fontsize=18)

    #ax.set_ylim([50,60])
    
    ax.xaxis_date()
    date_format = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()
    
    plt.show()
    
