# -*- coding: utf-8 -*-
"""
Created on Fri Jan 23 14:25:34 2015

@author: bolat
"""


#=======================================================================================
# INPUT ================================================================================

# full path of dts hdf file
# if using Windows put 'r' in front of directory path, example: r'W:\Data\CoP\A-02\DTS'
hdf_fullpath=r'Y:\Data\US\BHP\B5H\DTS\DTS_calibrated\Run2\B5H_cal_dts\B5H_cal_dts_hdf.hdf'

# Chosing data to average:
# "trace_indices" list should be "group, [from index,to index]". Look up from and to timestamps in "axis2" dataset of hdf file. Put their indices in "trace_indices"  
# make sure traces are cronologically in order (1st trace earliest and last latest in time)
# NOTE: delete comma at the end of last item of the list

trace_indices= [
['Donnell_B5H_Run1_SEQPRO2_4_AVG1M',[250,251]],
['Donnell_B5H_Run1_SEQSI2_AVG1M',[924,925]]  
#['PDO_FAHUD_F539PROD_PRO_AVG5M',[0,10]]
]



#=======================================================================================
#=======================================================================================


import h5py
import datetime
import numpy as np
import pandas as pd
import numpy
import matplotlib
import os
import shutil



def copy_object(infilename, outfilename, name):
    # Open files
    infile_id  = h5py.h5f.open(infilename,  h5py.h5f.ACC_RDONLY)
    outfile_id = h5py.h5f.create(outfilename, h5py.h5f.ACC_TRUNC)
    infile_root  = h5py.h5g.open(infile_id,  "/")
    outfile_root = h5py.h5g.open(outfile_id, "/")
    obj_id   = h5py.h5o.open(infile_root, name)
    obj_type = h5py.h5i.get_type(obj_id)
    if obj_type == h5py.h5i.GROUP:
        # If its a group, make corresponding group in the output file
        # (use h5ocopy because that would copy the contents too)
#        print "Make group  : ",name
        h5py.h5o.copy(infile_root, name, outfile_root, name)
    infile_id.close()
    outfile_id.close()


def dts_make_av(hdf_path, trace_indices):
    print 'importing data from ziebel hdf format..'
     
    path,f=os.path.split(hdf_path)
    f_name,ext=os.path.splitext(f)

    new_hdf_path=os.path.join(path,f_name+'_av'+ext)
    copy_object(hdf_path, new_hdf_path, 'Data')    
    
    
    dts_hdf = h5py.File(new_hdf_path,'r+')

    new_data=[]
    dt=[]
    dt_ranges=[]
    for trace in trace_indices:

        data=dts_hdf['Data/Calibrated_DTS/DTS/'+trace[0]+'/block0_values'][trace[1][0]:trace[1][1],:,:]
        print trace[0]
        data_traces=data[:,:,1]
        print data.shape
        data_depths=data[0,:,0]
        tr=np.transpose(data_traces)
        av_tr=[]
        for t in tr:
            av_tr.append(np.mean(t))
        new_data_tr=np.transpose([data_depths,av_tr])
        print new_data_tr.shape
        new_data.append(new_data_tr)
        dt.append(dts_hdf['Data/Calibrated_DTS/DTS/'+trace[0]+'/axis2'][trace[1][0]])
        dt_ranges.append(dts_hdf['Data/Calibrated_DTS/DTS/'+trace[0]+'/axis2'][trace[1][0]]+'_'+
                        dts_hdf['Data/Calibrated_DTS/DTS/'+trace[0]+'/axis2'][trace[1][1]])
    new_data=np.array(new_data)


    
    dts_hdf.create_group('/Data/Calibrated_DTS/DTS/av_traces')
    
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['CLASS']='GROUP'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['TITLE']='GROUP'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['VERSION']='1.0'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['axis0_variety']='regular'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['axis1_variety']='regular'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['axis2_variety']='regular'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['block0_items_variety']='regular'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['encoding']='N.'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['nblocks']='1'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['ndim']='3'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['pandas_type']='wide'
    dts_hdf['/Data/Calibrated_DTS/DTS/av_traces'].attrs['pandas_version']='0.10.1'
    
    dts_hdf.create_dataset('/Data/Calibrated_DTS/DTS/av_traces/block0_values',data=new_data)
    dts_hdf.create_dataset('/Data/Calibrated_DTS/DTS/av_traces/axis2',data=dt)
    dts_hdf.create_dataset('/Data/Calibrated_DTS/DTS/av_traces/axis0',data=dt)
    dts_hdf.create_dataset('/Data/Calibrated_DTS/DTS/av_traces/axis1',data=dt)
    dts_hdf.create_dataset('/Data/Calibrated_DTS/DTS/av_traces/block0_items',data=dt)
    dts_hdf.create_dataset('/Data/Calibrated_DTS/DTS/av_traces/dt_ranges',data=dt_ranges)
        


    dts_hdf.close()
    print 'finished averaging..'
    
if __name__=='__main__':
    dts_make_av(hdf_fullpath,trace_indices)
