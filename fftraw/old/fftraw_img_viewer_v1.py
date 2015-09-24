# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 09:58:02 2015

@author: bolatzh
"""



""" =============================HEADER============================================ """

hdf_file=r'D:\img_out\img_file_test_2.hdf'

plt_depths=[50,100]
plt_times=[50,100]
plt_freqs=0



""" =============================END============================================== """




import os
import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import h5py as h5
import numpy as np


fig = plt.figure(figsize=(18, 8))
gs=gridspec.GridSpec(30,40)
#ax = plt.subplot(gs[:,:])
ax1 = plt.subplot(gs[:,:5])
ax2 = plt.subplot(gs[:,5:10])
ax3 = plt.subplot(gs[:,10:15])
ax4 = plt.subplot(gs[:,15:29])
ax5 = plt.subplot(gs[:9,30:])
ax6 = plt.subplot(gs[11:19,30:],sharex=ax5,sharey=ax5)
ax7 = plt.subplot(gs[21:,30:],sharex=ax5,sharey=ax5)

#ax5 = plt.subplot(gs[:9,:])
#ax6 = plt.subplot(gs[11:19,:],sharex=ax5,sharey=ax5)
#ax7 = plt.subplot(gs[21:,:],sharex=ax5,sharey=ax5)
#ax_tf=[ax5]
ax_td=[ax1,ax2,ax3]
ax_tf=[ax5,ax6,ax7]



hdf=h5.File(hdf_file,'r')

    
for i,d in enumerate(plt_depths):

    grs=[] 
    keys=hdf['/tf/%s' % str(d)].keys() 
    for key in keys:
        grs.append('/tf/%s/%s' % (str(d),key))

    freq_min=1e6
    freq_max=0
    time_min=1e6
    time_max=0

    for gr in grs:
    
        print gr
        img_arr=hdf[gr][...]   
        depth=hdf[gr].attrs['depth']
        times=hdf[gr].attrs['times']    
        freqs=hdf[gr].attrs['freqs']  
    
        if freqs[0]<freq_min:
            freq_min=freqs[0]
        if freqs[1]>freq_max:
            freq_max=freqs[1]
        if times[0]<time_min:
            time_min=times[0]
        if times[1]>time_max:
            time_max=times[1]        
    
    
            
        extent = [times[0],times[1],freqs[0],freqs[1]]        
        myplot=ax_tf[i].imshow(img_arr,aspect='auto',interpolation='none',extent=extent)  
#        extent = [times[0],times[1],freqs[1],freqs[0]]        
#        myplot=ax_tf[i].imshow(img_arr,aspect='auto',interpolation='none',extent=extent,vmin=0,vmax=40)
    ax_tf[i].set_xlim(time_min,time_max)
    ax_tf[i].set_ylim(freq_min,freq_max)
    
    

for i,t in enumerate(plt_times):
        
    grs=[] 
    keys=hdf['/td'].keys() 
    for key in keys:
        grs.append('/td/%s' % (key))

    depth_min=1e6
    depth_max=0
    time_min=1e6
    time_max=0

    for gr in grs:
    
        print gr
        img_arr=hdf[gr][...]   
        time=hdf[gr].attrs['time']
        depths=hdf[gr].attrs['depths']    
        freqs=hdf[gr].attrs['freqs']  
    
        if depths[0]<depth_min:
            depth_min=depths[0]
        if depths[1]>depth_max:
            depth_max=depths[1]
        if times[0]<time_min:
            time_min=times[0]
        if times[1]>time_max:
            time_max=times[1]        
    
    
            
#        extent = [times[0],times[1],depths[0],depths[1]]        
#        myplot=ax_td[i].imshow(img_arr,aspect='auto',interpolation='none',extent=extent)  
        extent = [times[0],times[1],depths[1],depths[0]]        
        myplot=ax_td[i].imshow(img_arr,aspect='auto',interpolation='none',extent=extent,vmin=0,vmax=40)
    ax_td[i].set_xlim(time_min,time_max)
    ax_td[i].set_ylim(depth_min,depth_max)
    





plt.show()
hdf.close()




