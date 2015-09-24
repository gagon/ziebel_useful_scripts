# -*- coding: utf-8 -*-
"""
Created on Tue Aug 04 14:11:39 2015

@author: bolatzh
"""


"""==========================================================================================="""
"""=================================HEADER===================================================="""
    


hdf_folder=r"O:\Data\BP\A10\DAS\DAS_Processed\oct_1sec_time_resolution"    
blocksize=15000



"""=================================END======================================================="""
"""==========================================================================================="""





import h5py
import os
import sys


for root, dirs, files in os.walk(hdf_folder):
    for f in files:
        if f.endswith('.hdf'):
            hdf_file=os.path.join(root,f)
            hdf=h5py.File(hdf_file, 'r')
            
            
            
            if int(float(hdf['data'].attrs.__getitem__('timecount'))/float(blocksize))!=int(hdf['data'].shape[0]):
                print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                print "file: %s" % os.path.join(root,f)
                print "timecount/blocksize= %i vs shape time count = %i" % \
                    (int(float(hdf['data'].attrs.__getitem__('timecount'))/ \
                    float(blocksize)), \
                    hdf['data'].shape[0])            
                print "blocksize=%s" % blocksize
                print "depthcount=%s" % hdf['data'].attrs.__getitem__('depthcount')
                print "depthspacing=%s" % hdf['data'].attrs.__getitem__('depthspacing')
                print "samplerate=%s" % hdf['data'].attrs.__getitem__('samplerate')
                print "timecount=%s" % hdf['data'].attrs.__getitem__('timecount')            
                print "processed data shape=%s" % str(hdf['data'].shape)
            else:
                print "file: %s -> ok" % os.path.join(root,f)

            
            hdf.close()