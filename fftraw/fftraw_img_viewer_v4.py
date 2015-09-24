# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 09:58:02 2015

@author: bolatzh
"""



""" =============================HEADER============================================ """


#hdf_file=r'Z:\Data\Ziebel_test_data\RODTESTS\fftraw_processed\test\img_file.hdf'
#hdf_file=r'Z:\Data\Ziebel_test_data\Tatiana\fftraw_processed\img_file.hdf'
hdf_file=r'Z:\Data\Ziebel_test_data\RODTESTS\fftraw_processed\img_file_denoise.hdf'
#hdf_file=r'Z:\Data\Ziebel_test_data\RODTESTS\fftraw_processed\img_file_nodenoise.hdf'


tf1_depth=157
tf2_depth=150
df_time=100
td_freq=100


img_type='int'
vmin=0
vmax=40
cmap='jet'

#plots='tf'
plots='all'



""" =============================END============================================== """




import os
import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import h5py as h5
import numpy as np

def make_plot(plot_type,ax,val):
    if type(val) is list:
        root_gr='/%s/%s_%s/' % (plot_type,str(val[0]),str(val[1]))
    elif val==None:
        return
    else:
        root_gr='/%s/%s/' % (plot_type,str(val))        
    grs=[] 
    keys=hdf[root_gr].keys() 
    for key in keys:
        grs.append(root_gr+key)
    
    y_min=1e6
    y_max=0
    x_min=1e6
    x_max=0
    
    for gr in grs:
    
        print gr
        img_arr=hdf[gr][...]   
        if plot_type=='tf':
            val=hdf[gr].attrs['depth']
            xs=hdf[gr].attrs['times']    
            ys=hdf[gr].attrs['freqs']
            ax.set_title('Freq vs Time (depth=%s)' % str(val))
        elif plot_type=='td':
            val=hdf[gr].attrs['freq']
            xs=hdf[gr].attrs['times']    
            ys=hdf[gr].attrs['depths'] 
            ax.set_title('Depth vs Time (freq=%s)' % str(val))
        elif plot_type=='df':
            val=hdf[gr].attrs['time']
            xs=hdf[gr].attrs['freqs']    
            ys=hdf[gr].attrs['depths'] 
            ax.set_title('Depth vs Freq (time=%s)' % str(val))            
    
        if ys[0]<y_min:
            y_min=ys[0]
        if ys[1]>y_max:
            y_max=ys[1]
        if xs[0]<x_min:
            x_min=xs[0]
        if xs[1]>x_max:
            x_max=xs[1]        
                    
        if img_type=='plt':
            extent = [xs[0],xs[1],ys[1],ys[0]]        
            ax.imshow(img_arr,aspect='auto',interpolation='none',extent=extent)   
        elif img_type=='int':
            extent = [xs[0],xs[1],ys[1],ys[0]]        
            ax.imshow(img_arr,aspect='auto',cmap=cmap,interpolation='none',extent=extent,vmin=vmin,vmax=vmax)             

    ax.set_xlim(x_min,x_max)    

    if plot_type=='tf':
        ax.set_ylim(y_min,y_max)
    elif plot_type=='td' or plot_type=='df':
        ax.set_ylim(y_max,y_min)            

hdf=h5.File(hdf_file,'r')


fig = plt.figure(figsize=(20, 10))
gs=gridspec.GridSpec(30,60)

if plots=='all':
    ax_df = plt.subplot(gs[:,:14])
    ax_td = plt.subplot(gs[:,15:40],sharey=ax_df)
    ax_tf1 = plt.subplot(gs[:14,44:])
    ax_tf2 = plt.subplot(gs[16:,44:],sharex=ax_tf1,sharey=ax_tf1)
    ax_tf=[ax_tf1,ax_tf2]

    make_plot('tf',ax_tf1,tf1_depth)
    make_plot('tf',ax_tf2,tf2_depth)
    make_plot('td',ax_td,td_freq)
    make_plot('df',ax_df,df_time)


    ax_td.get_yaxis().set_visible(False)
    ax_tf1.get_xaxis().set_visible(False)
    
    ax_df.set_xlabel('Frequency, Hz')
    ax_df.set_ylabel('Depth, m')
    ax_td.set_xlabel('Time, s')
    ax_tf1.set_ylabel('Frequency, Hz')
    ax_tf2.set_ylabel('Frequency, Hz')
    ax_tf2.set_xlabel('Time, s')




elif plots=='tf':
    ax_tf1 = plt.subplot(gs[:,:])
    
    make_plot('tf',ax_tf1,tf1_depth)

    ax_tf1.set_ylabel('Frequency, Hz')
    ax_tf1.set_xlabel('Time, s')






plt.show()
hdf.close()




