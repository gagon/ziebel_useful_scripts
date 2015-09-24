# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 11:27:12 2014

@author: bolat
"""

"""========================================================================================="""
"""========================================================================================="""
""" Input header """






dts_folder=r'L:\Data\Ziebel_test_data\KiM_DTS_Investigation\DTS_Test_20\DTS_Raw'  
memgauge_fullpath=r"L:\Data\Ziebel_test_data\KiM_DTS_Investigation\DTS_Test_20\US00015_calibration_test-20_Fixed.txt"
tref_str="T ext. ref 2"

figure_title="Test 20"







"""========================================================================================="""
"""========================================================================================="""




import os
import re
import datetime
import numpy as np
import matplotlib.pyplot as plt
import sys
import matplotlib.dates as mdates
import gc
import matplotlib.gridspec as gridspec
import getpass
import h5py
from matplotlib import cm
import matplotlib
import pandas as pd




def parse_ddfs(src_folder):
    ddfdata=[]
    temp_ref1=[]
    temp_ref2=[]
    temp_ref3=[]
       

    for root, dirs, files in os.walk(src_folder):        
        for f in files:            
            if f.endswith(".ddf"):                
                head, ext = os.path.splitext(f)
                ddf_file=os.path.join(root, f)                                   
                file=open(ddf_file,"r")                                                                        
                trace_datetime=[]
                trace_depth=[]
                trace_temperature=[]                
                for idx,line in enumerate(file):                    
                    text=re.split("\t|\r|\n",line) 
                    if idx==0:                    
                        for idx,t in enumerate(text):                            
                            if t=="date":  
                                trace_datetime=matplotlib.dates.date2num(datetime.datetime.strptime(text[idx+1]+" "+text[idx+3], "%Y/%m/%d %H:%M:%S") )  
                            if tref[0] in t:
                                temp_ref1.append([trace_datetime,float(text[idx+1])])
                            if tref[1] in t:
                                temp_ref2.append([trace_datetime,float(text[idx+1])])
                            if tref[2] in t:
                                temp_ref3.append([trace_datetime,float(text[idx+1])])
                    else:
                        trace_depth.append(float(text[0]))
                        trace_temperature.append(float(text[1]))                
                ddfdata.append([trace_datetime,trace_depth,trace_temperature,ddf_file])

    ddfdata=sorted(ddfdata,key=lambda x: x[0])      
    temp_ref1=sorted(temp_ref1,key=lambda x: x[0])      
    temp_ref2=sorted(temp_ref2,key=lambda x: x[0])          
    temp_ref3=sorted(temp_ref3,key=lambda x: x[0])      

        
    return ddfdata,[temp_ref1,temp_ref2,temp_ref3]


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
#                    if idx<20:
#                        print d
                    timestamps.append(matplotlib.dates.date2num(
                        datetime.datetime.strptime(d[0] + ' ' + d[1], '%Y.%m.%d %H:%M:%S')))
                    seconds.append((datetime.datetime.strptime(d[0] + ' ' + d[1], '%Y.%m.%d %H:%M:%S') - UNIX_EPOCH).total_seconds())
                    pressure.append(float(d[3].replace(",",".")))
                    temperature.append(float(d[4].replace(",",".")))
    
    mem=pd.DataFrame({'timestamps':timestamps,'temperature':temperature})   
    mem=mem.sort(['timestamps'])
    
    return mem

                    


if __name__=="__main__":
    tref=["T internal ref","T ext. ref 1","T ext. ref 2"]
    data,tref_temp=parse_ddfs(dts_folder)

    fig = plt.figure(figsize=(18, 8))
    ax = plt.subplot(111)
    
    
    ax.plot(data[0][1],data[0][2])
 
    plt.show()
    

        
    av_zone_min=float(raw_input("av zone, trace depth min (in meters): ")) # depth
    av_zone_max=float(raw_input("av zone, trace depth max (in meters): ")) # depth
    av_zone_min_idx=(np.abs(np.array(data[0][1])-av_zone_min)).argmin() # index
    av_zone_max_idx=(np.abs(np.array(data[0][1])-av_zone_max)).argmin() # index                


        
    
    if tref_str=="T internal ref":
        tref_data=np.array(tref_temp[0]).T
    elif tref_str=="T ext. ref 1":
        tref_data=np.array(tref_temp[1]).T
    elif tref_str=="T ext. ref 2":
        tref_data=np.array(tref_temp[2]).T

    dts_temp=[]            
    for d in data:
        dts_temp.append([d[0],np.mean(d[2][av_zone_min_idx:av_zone_max_idx])])
    dts_temp=np.array(dts_temp).T


    
    mem=readmemgauge(memgauge_fullpath)


    
    fig = plt.figure(figsize=(18, 8))
    ax = plt.subplot(111)

    
    ax.plot(dts_temp[0],dts_temp[1],'.',label='DTS')
    ax.plot(tref_data[0],tref_data[1],'.',label='DTS temp ref')
    ax.plot(mem['timestamps'],mem['temperature'],'.',label='Memory gauge')
    

    plt.legend()
    ax.set_ylabel('Temperature (degC)',fontsize=16)    
    ax.set_title(figure_title,fontsize=18)

    #ax.set_ylim([50,60])
    
    ax.xaxis_date()
    date_format = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

 
    plt.show()


    