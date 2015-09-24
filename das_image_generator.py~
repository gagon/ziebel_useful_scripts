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
import gc

folders= [\
[r'/mnt/A0-Data1/Data/BP/G-21_2015/DAS/1sec-Time-Resolution/oct',-106.24,1]
#[r'/mnt/A4-Data1/Data/Daleel/BR-13/DAS/NEW_DAS_Processed/Oct/1275',1561,1]
#[r'Y:\Data\MAERSK\Maersk_Feb_2015\HDA-17\DAS\DISK744\DAS\HDA-17\A\INJ',-95.6,1],
#[r'Y:\Data\MAERSK\Maersk_Feb_2015\HDA-17\DAS\DISK747\DAS\HDA-17\A\INJ',-95.6,1],
#[r'Y:\Data\MAERSK\Maersk_Feb_2015\HDA-17\DAS\DISK747\DAS\HDA-17\A\INJ2',-95.6,1],
#[r'Y:\Data\MAERSK\Maersk_Feb_2015\HDA-17\DAS\DISK282\DAS\HDA-17\A\INJ2',-95.6,1],
#[r'Y:\Data\MAERSK\Maersk_Feb_2015\HDA-17\DAS\DISK616\DAS\HDA-17\A',-95.6,1],
#[r'Y:\Data\MAERSK\Maersk_Feb_2015\HDA-17\DAS\DISK545\DAS\HDA-17\A',-95.6,1],
#[r'Y:\Data\MAERSK\Maersk_Feb_2015\HDA-17\DAS\DISK565\DAS\HDA-17\A',-95.6,1],
#[r'Y:\Data\MAERSK\Maersk_Feb_2015\HDA-17\DAS\DISK482\DAS\HDA-17\A',-95.6,1]
]


plot_folder=r'/mnt/A0-Data1/Data/BP/G-21_2015/DAS/1sec-Time-Resolution/Plots'



# processing ('new' or 'old')
processing='new'
# intensity scales in dB
das_scale_min=10
das_scale_max=50
# DAS file attrs
numblocks=9.7656
das_timeshift=2

dpi=500

f_num=[25]
#f_num=[0]
#f_num=[20]


def read_gnu(gnu_fp):
    file=open(gnu_fp,'r')
    for ind,line in enumerate(file):
        if 'd_offset_das' in line:
            d_offset_das=line.split()[2]
        if 'd_scale_das' in line:
            d_scale_das=line.split()[2]
        if 't_offset_das' in line:
            t_offset_das = line.split()[2]
        if 't_scale_das' in line:
            t_scale_das = line.split()[2]
    return [float(d_scale_das),float(d_offset_das),float(t_scale_das),float(t_offset_das)]


def getDASdataMod2(hdffile,numblocks,depth_offset):

    blocklength = 1024
    depth_start=0
    time_offset=0

    depth_resol_m = float(hdffile['data'].attrs.__getitem__('depthspacing'))
    fsampling = float(hdffile['data'].attrs.__getitem__('samplerate'))
    time_resol_sec = (blocklength*numblocks)/fsampling

    return (time_resol_sec,time_offset,depth_resol_m,depth_offset,depth_start)


def getDASdataMod(hdffile,numblocks,depth_offset):

    blocklength = 1024
    depth_start=0
    time_offset=0

    depth_resol_m = float(hdffile['RAWdata/DASdata/FDSdata'].attrs.__getitem__('DataLocusSpacing_m'))
    fsampling = float(hdffile['RAWdata/DASdata/FDSdata'].attrs.__getitem__('TimeStepFrequency_Hz'))
    time_resol_sec = (blocklength*numblocks)/fsampling

    return (time_resol_sec,time_offset,depth_resol_m,depth_offset,depth_start)


for item in folders:
    hdf_folder=item[0]
    das_offset=item[1]
    for root, dirs, files in os.walk(hdf_folder):
        for f in files:
            if f.endswith('.hdf'):
                print f
                check_time_start_dt=datetime.datetime.strptime(os.path.splitext(f)[0],'%Y.%m.%d.%H.%M.%S')+datetime.timedelta(hours=das_timeshift)
                check=datetime.datetime.strftime(check_time_start_dt,'%Y.%m.%d.%H.%M.%S')
                breaker1=False
                breaker2=False
    #            for root2, dirs2, files2 in os.walk(plot_folder):
    #                for f2 in files2:
    #                    if check in f2:                        
    #                        print 'breaker1'
    #                        breaker1=True
    #                        break
    #                if breaker1:
    #                    print 'breaker2'
    #                    breaker2=True
    #                    break
                if breaker2:
                    print 'skip',f
    #                break
                else:
    #                continue
    
                    hdf_file=os.path.join(root,f)
                    hdf=h5py.File(hdf_file, 'r')
                    if processing=='old':
                        hdf_attrs=getDASdataMod(hdf,numblocks,das_offset)
                        data=hdf['/OUTdata/DASdata/OCTdata/13Octaves/13Octaves'][:,:,:]
                    elif processing=='new':
                        hdf_attrs=getDASdataMod2(hdf,numblocks,das_offset)
                        data=hdf['data'][:,:,:]
                    time_resol_sec=hdf_attrs[0]
                    time_offset=hdf_attrs[1]
                    time_start=os.path.splitext(os.path.split(hdf_file)[1])[0]
                    if item[2]!=1:
                        depth_resol_m=item[2]
                    else:
                        depth_resol_m=hdf_attrs[2]
                    depth_offset=hdf_attrs[3]
                    depth_start=hdf_attrs[4]
                    trace_depth=np.array([i*depth_resol_m+das_offset for i in range(len(data[0]))])    
                    
        
                    time_start_dt=datetime.datetime.strptime(time_start,'%Y.%m.%d.%H.%M.%S')+datetime.timedelta(hours=das_timeshift)
                    dt=str(round(len(data)*float(time_resol_sec),3))
                    d_start=str(round(trace_depth[0],3))
                    d_end=str(round(trace_depth[-1],3))
        
                    file_name=datetime.datetime.strftime(time_start_dt,'%Y.%m.%d.%H.%M.%S')+'_'+dt+'_'+d_start+'_'+d_end
                    
    #                if os.path.exists(os.path.join(plot_folder,str(0)+'_'+file_name+'.png')):
    #                    print f,'exits! skipping'
    #                    break
                    
    #                for freq in range(len(data[0,0,:])):
                    
                    for freq in f_num:
                        print f+' => '+' freq='+str(freq)
                        fig, ax = plt.subplots(figsize=(20, 20),dpi=dpi)
#                        if freq==33:
#                            myplot=plt.imshow(np.array(np.transpose(data[:,:,freq])),aspect='auto',vmin=35,vmax=65)
#                        else:
#                            myplot=plt.imshow(np.array(np.transpose(data[:,:,freq])),aspect='auto',vmin=das_scale_min,vmax=das_scale_max)
                        
#                        myplot=plt.imshow(np.array(np.transpose(data[:,:,freq])),aspect='auto',vmin=das_scale_min,vmax=das_scale_max)
#                        myplot=plt.imshow(np.array(np.transpose(data[:,5056:7056,freq])),aspect='auto',vmin=das_scale_min,vmax=das_scale_max)                        
                        myplot=plt.imshow(np.array(np.transpose(data[:,:,freq])),aspect='auto',vmin=das_scale_min,vmax=das_scale_max)                        

                        
                        ax.set_position([0.001,0.001, 0.998, 0.997])
                        fig.savefig(os.path.join(plot_folder,str(freq)+'_'+file_name+'.png')) 

                        
                        fig.clf()
                        plt.close()
                        gc.collect()
                    del data
                    gc.collect()                
                    
                    hdf.close()
        #            sys.exit()

