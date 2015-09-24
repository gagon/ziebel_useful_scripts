# -*- coding: utf-8 -*-
"""
Created on Tue Jan 06 16:13:31 2015

@author: bolatzh
"""

import h5py
import matplotlib.dates as mdates
import numpy as np



def convert_to_ziebel_format(dts,dts_copy):
    print "converting to ziebel format.."
    orig_hdf=h5py.File(dts, 'r')
    
    data=orig_hdf['interp_traces/block0_values'][:]
    depths=orig_hdf['interp_traces/axis0'][:]
    dt_mt=orig_hdf['interp_traces/axis1'][:]
    
    dt=[]
    for t in dt_mt:
        dt.append(mdates.num2date(t).strftime('%Y/%m/%d %H:%M:%S'))

    dt=dt[:]
    
    new_data=[]
    for d in data:
        arr=[]
        for ind,a in enumerate(d):
            arr.append([depths[ind],a])
        new_data.append(arr)
    new_data=np.array(new_data)
    
    orig_hdf.close()
    
    copy_hdf=h5py.File(dts_copy, 'w-')
    copy_hdf.create_group('/Data/Calibrated_DTS/DTS/Merged')
    
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['CLASS']='GROUP'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['TITLE']='GROUP'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['VERSION']='1.0'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['axis0_variety']='regular'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['axis1_variety']='regular'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['axis2_variety']='regular'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['block0_items_variety']='regular'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['encoding']='N.'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['nblocks']='1'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['ndim']='3'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['pandas_type']='wide'
    copy_hdf['/Data/Calibrated_DTS/DTS/Merged'].attrs['pandas_version']='0.10.1'
    
    copy_hdf.create_dataset('/Data/Calibrated_DTS/DTS/Merged/block0_values',data=new_data)
    copy_hdf.create_dataset('/Data/Calibrated_DTS/DTS/Merged/axis2',data=dt)
    copy_hdf.create_dataset('/Data/Calibrated_DTS/DTS/Merged/axis0',data=dt)
    copy_hdf.create_dataset('/Data/Calibrated_DTS/DTS/Merged/axis1',data=dt)
    copy_hdf.create_dataset('/Data/Calibrated_DTS/DTS/Merged/block0_items',data=dt)
    copy_hdf.close()
    print "done! good job!"







