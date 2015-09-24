# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 15:46:14 2014

@author: bolatzh
"""

import h5py
import os
import numpy as np
import matplotlib.pyplot as plt


hdf_file=os.path.normpath(raw_input("enter DAS file full path: "))
#hdf_file=r'Y:\Data\US\BHP\B5H\DAS\Donnell\B5H\Run.1\SEQ.PRO2\4\ZNsAsDATE\octavebands\2015.04.25.02.02.51.hdf'
#hdf_file=r'L:\Data\Daleel\BR-13\DAS\NEW_DAS_Processed\Oct\2013.07.07.14.45.47.hdf'
# processing ('new' or 'old')
#processing='new'
processing=raw_input("enter DAS processing type(old or new): ")

# intensity scales in dB
das_scale_min=10
das_scale_max=50

# DAS frequency
#freq=0
freq=int(raw_input("enter frequency band: "))
   
hdf_file=os.path.join(hdf_file)
hdf=h5py.File(hdf_file, 'r')
if processing=='old':
    data=hdf['/OUTdata/DASdata/OCTdata/13Octaves/13Octaves'][:,:,freq]
elif processing=='new':
    data=hdf['data'][:,:,freq]
myplot=plt.imshow(np.array(np.transpose(data)),aspect='auto',vmin=das_scale_min,vmax=das_scale_max)
plt.ylabel("Index")
plt.show()

index1=int(raw_input("enter index 1: "))
index1_depth=float(raw_input("enter index 1 depth to match (m): "))
index2=int(raw_input("enter index 2: "))
index2_depth=float(raw_input("enter index 2 depth to match (m): "))
depth_sampling_entered=float(raw_input("depth sampling? (calculate: 0, from hdf:1, fixed value:enter value): "))

if depth_sampling_entered==float(0):
    d=np.array([index1_depth,index2_depth])
    s=np.array([[index1,1],[index2,1]])
    result=np.linalg.solve(s,d)
    depth_sampling=result[0]
    offset1=result[1]
    print 'offset=%s, depth_sampling(calculated)=%s' % (str(offset1),str(depth_sampling))
elif depth_sampling_entered==float(1):
    if processing=='new':
        depth_sampling=float(hdf['data'].attrs.__getitem__('depthspacing'))
    elif processing=='old':
        depth_sampling=float(hdf['RAWdata/DASdata/FDSdata'].attrs.__getitem__('DataLocusSpacing_m'))
    offset1=index1_depth-depth_sampling*index1
    offset2=index2_depth-depth_sampling*index2
    print 'offset1=%s, depth_sampling(from hdf)=%s' % (str(offset1),str(depth_sampling))
    print 'offset2=%s, depth_sampling(from hdf)=%s' % (str(offset2),str(depth_sampling))
else:
    depth_sampling=depth_sampling_entered
    offset1=index1_depth-depth_sampling*index1
    offset2=index2_depth-depth_sampling*index2    
    print 'offset1=%s, depth_sampling(entered)=%s' % (str(offset1),str(depth_sampling))
    print 'offset2=%s, depth_sampling(entered)=%s' % (str(offset2),str(depth_sampling))

depth_start=offset1
depth_end=offset1+depth_sampling*len(data[0])

extent=[0,len(np.transpose(data)[0]),depth_end,depth_start]
myplot=plt.imshow(np.array(np.transpose(data)),extent=extent,aspect='auto',vmin=das_scale_min,vmax=das_scale_max)
if depth_sampling_entered==float(0):
    plt.title('offset=%s, depth_sampling(calculated)=%s' % (str(offset1),str(depth_sampling)))    
elif depth_sampling_entered==float(1):
    plt.title('offset1=%s, offset2=%s, depth_sampling(from hdf)=%s' % (str(offset1),str(offset2),str(depth_sampling)))
else:
    plt.title('offset1=%s, offset2=%s, depth_sampling(entered)=%s' % (str(offset1),str(offset2),str(depth_sampling)))
plt.ylabel("Depth m")
plt.show()

hdf.close()


