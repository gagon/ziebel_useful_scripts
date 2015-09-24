# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 11:27:12 2014

@author: bolat
"""

"""========================================================================================="""
"""========================================================================================="""
""" Input header """

# input files
#dts_folder=r'L:\Data\DTS-test\DTS_Test_16a,b\test'  
dts_folder=r'N:\Data\US\CoP\El-Jefe-WC_802H\test'

coil1=[-10000,100000]   
coil2=[0,0]


"""========================================================================================="""
"""========================================================================================="""




import h5py
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import re
import matplotlib.gridspec as gridspec

def read_from_dtsext(dts_path):
    
    date_time=[]
#    temp_ref=[]
    data1=[]
    data2=[]
    
    for root, dirs, files in os.walk(dts_path):
        for f in files:
            if f.endswith('.ddf'):
                print f

                trace_depth1=[]
                trace_temp1=[]
                trace_depth2=[]
                trace_temp2=[]                
                
                # get file and folder names
                head, ext = os.path.splitext(f)
                dts_file=os.path.join(root, f)
                                   
                file=open(dts_file,'r')
                                    
                av=1
                test=1

                for ind,line in enumerate(file):                    
                    text=re.split('\t|\r|\n',line) 
                    if ind==0:                    
                        for ind,t in enumerate(text):
                            if t=='date':  
                                dt=matplotlib.dates.date2num(
                                                datetime.datetime.strptime(
                                                    text[ind+1]+' '+text[ind+3], 
                                                    '%Y/%m/%d %H:%M:%S'))
                                date_time.append(dt)
                            if "T ext. ref 2 (\xb0C)" in t:
                                temp_ref=float(text[ind+1])
                    else:
                        if float(text[0])>coil1[0] and float(text[0])<=coil1[1]:
                            if float(text[1])>200.0 or float(text[1])<0.0:
                                print dts_file
                            else:
                                trace_depth1.append(float(text[0]))
                                trace_temp1.append(float(text[1]))

                data1.append([dt,temp_ref,[trace_depth1,trace_temp1],av,test])

                
    data1=sorted(data1,key=lambda x: x[0])

    return data1,data2

                    


if __name__=="__main__":

    data1,data2=read_from_dtsext(dts_folder)
#    date_time,data1=read_from_dtsext(dts_folder)

    
    gs=gridspec.GridSpec(10,2)
    fig = plt.figure(figsize=(18, 8))
#    ax1 = plt.subplot(gs[:,:])
    ax1 = plt.subplot()
#    ax2 = plt.subplot(gs[0:5,1],sharey=ax1)
#    ax3 = plt.subplot(gs[6:,:])
    
    dt=[]
    temp_ref=[]
    for data in data1:
        ax1.plot(data[2][0],data[2][1])
        dt.append(data[0])
        temp_ref.append(data[1])
      
#    for data in data2:
#        ax2.plot(data[2][0],data[2][1])
#    
#    ax3.plot(dt,temp_ref)
#    plt.xticks(rotation=30,ha='right')
              
    ax1.set_ylim(37,43)
    ax1.set_title('Coil 1')
#    ax2.set_title('Coil 2')
#    ax3.set_title('T ext. ref 2 (\xb0C)')

    ax1.set_ylabel('Temperature degC')    
    ax1.set_xlabel('Fiber length')  

#    ax2.set_xlabel('Fiber lenght') 

#    ax3.xaxis_date()
#    date_format = matplotlib.dates.DateFormatter('%b.%d %H:%M')
#    ax3.xaxis.set_major_formatter(date_format)
#    fig.autofmt_xdate()
  
    plt.show()
    