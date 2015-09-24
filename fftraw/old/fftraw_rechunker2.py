# -*- coding: utf-8 -*-
"""
Created on Wed Sep 09 14:42:36 2015

@author: bolatzh
"""



""" =============================HEADER============================================ """


fftrawout_file =  r'Z:\Data\Ziebel_test_data\RODTESTS\fftraw_processed\ZROD_2015.07.20.10.54.54.hdf'
rechunked_file =  r'Z:\Data\Ziebel_test_data\RODTESTS\fftraw_processed\ZROD_2015.07.20.10.54.54_rechunk_nodenoise.hdf'

# for tf and df data
freq_lim=[0,500]
depth_lim=-1
time_lim=[0,500]

time_chunk_size=500
depth_chunk_size=221
freq_chunk_size=1

time_rechunk_size=100
depth_rechunk_size=100
freq_rechunk_size=100

#denoise=[7000,7050]
denoise=None




""" =============================END============================================== """




import h5py
import numpy as np
import gc
from numpy import zeros, newaxis

#dummy_file=r'D:\COP_A05\dummy.hdf'
#dummy_hdf=h5py.File(dummy_file, 'w-')
#d=np.random.rand(100,100,100)
#dummy_hdf.create_dataset('/data',data=d,chunks=(10,10,10))
#dummy_hdf.close()


original_hdf = h5py.File(fftrawout_file,'r')
rechunked_hdf=h5py.File(rechunked_file, 'w-')


def chunking(lim,chunk_size):
    chunks=(lim[1]-lim[0])//chunk_size
    chunks_tail=(lim[1]-lim[0])%chunk_size
    if chunks_tail>0:
        total_chunks=chunks+1
    else:
        total_chunks=chunks
    return [chunks,chunks_tail,total_chunks,lim,chunk_size]
    


def rechunk(global_cnt,x_par,y_par,z_par):

    x_chunks=x_par[0]
    x_chunks_tail=x_par[1]
    total_x_chunks=x_par[2]
    x_lim=x_par[3]
    x_chunk_size=x_par[4]

    y_chunks=y_par[0]
    y_chunks_tail=y_par[1]
    total_y_chunks=y_par[2]
    y_lim=y_par[3]
    y_chunk_size=y_par[4]

    z_chunks=z_par[0]
    z_chunks_tail=z_par[1]
    total_z_chunks=z_par[2]
    z_lim=z_par[3]
    z_chunk_size=z_par[4]

    
    if time_lim!=-1:
        shape_time=time_lim[1]-time_lim[0]
    else:
        shape_time=original_hdf['/data'].shape[0]
    if depth_lim!=-1:
        shape_depth=depth_lim[1]-depth_lim[0]
    else:
        shape_depth=original_hdf['/data'].shape[1]
    if freq_lim!=-1:
        shape_freq=freq_lim[1]-freq_lim[0]
    else:
        shape_freq=original_hdf['/data'].shape[2]
        
    ds_cnt=0

    # x dimension loop        
    for x in range(total_x_chunks):    
        from_x_idx=x_lim[0]+x*x_chunk_size
        if x==x_chunks:
            to_x_idx=from_x_idx+x_chunks_tail
        else:
            to_x_idx=from_x_idx+x_chunk_size
            
        # y dimension loop
        for y in range(total_y_chunks):                                      
            from_y_idx=y_lim[0]+y*y_chunk_size
            if y==y_chunks:
                to_y_idx=from_y_idx+y_chunks_tail
            else:
                to_y_idx=from_y_idx+y_chunk_size
            
            # define noise floor is applied
            if denoise:
                noise_floor=10.0*np.log10(np.mean(\
                                        original_hdf['data']\
                                        [from_x_idx:to_x_idx, from_y_idx:to_y_idx, denoise[0]:denoise[1]],\
                                        axis=2))[:,:,newaxis]
                            
                print noise_floor.shape, 'denoise'

            # z dimension loop
            for z in range(total_z_chunks):                                      
                from_z_idx=z_lim[0]+z*z_chunk_size
                if z==z_chunks:
                    to_z_idx=from_z_idx+z_chunks_tail
                else:
                    to_z_idx=from_z_idx+z_chunk_size

                print '%i/%i chunks / x(%s,%s) / y(%s,%s) / x(%s,%s)' % \
                            (global_cnt+1,total_cnt,from_x_idx,to_x_idx,from_y_idx,to_y_idx,from_z_idx,to_z_idx)
             
                data=original_hdf['data'][from_x_idx:to_x_idx, from_y_idx:to_y_idx, from_z_idx:to_z_idx]

                if denoise:
                    data=np.array(np.rint(10.0*np.log10(np.array(data))-noise_floor),dtype='int8')
                else:
                    data=np.array(np.rint(10.0*np.log10(np.array(data))),dtype='int8')
                    
                if ds_cnt==0:
                    rechunked_hdf.create_dataset('/data',data=data,\
                                            chunks=(time_rechunk_size,depth_rechunk_size,freq_rechunk_size),\
                                            maxshape=(None, None, None))
                    rechunked_hdf['/data'].resize((shape_time,shape_depth,shape_freq))
                else:                    
                    rechunked_hdf['/data'][from_x_idx:to_x_idx, from_y_idx:to_y_idx, from_z_idx:to_z_idx]=data
                    
                ds_cnt+=1
                global_cnt+=1
                
                # clear memory
                gc.collect()
                del gc.garbage[:]

    return global_cnt








    
    
depth_hdf = int(original_hdf['data'].shape[1])
time_hdf = int(original_hdf['data'].shape[0])
freq_hdf = int(original_hdf['data'].shape[2])

print 'hdf dataset shape=', original_hdf['data'].shape

if depth_lim==-1:
    depth_lim=[0,depth_hdf]
if freq_lim==-1:
    freq_lim=[0,freq_hdf]
if time_lim==-1:
    time_lim=[0,time_hdf]

# define chunks
depth_chunk_par=chunking(depth_lim,depth_chunk_size)
time_chunk_par=chunking(time_lim,time_chunk_size)
freq_chunk_par=chunking(freq_lim,freq_chunk_size)    



# number of images to produce
total_cnt=time_chunk_par[2]*freq_chunk_par[2]*depth_chunk_par[2]

# counter for images produced
global_cnt=0

global_cnt=rechunk(global_cnt,time_chunk_par,depth_chunk_par,freq_chunk_par)
                
                
                






                


