

""" =============================HEADER============================================ """


#fftrawout_file =  r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_fftraw\2015.08.06.00.12.02.hdf'
fftrawout_file =  r'D:\2015.08.06.00.12.02.hdf'
img_file =  r'D:\img_out\img_file.hdf'

prf = 5000

# depth points for tf data
depths=[1000]

# for tf and df data
freq_lim=[0,1000]
depth_lim=-1
time_lim=[0,1000]

# colormap lims
vmin=0.0
vmax=40.0
img_type='plt'
img_dpi_defac=1



""" =============================END============================================== """



import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import colors
import gc
import os
import sys
from PIL import Image
import datetime


def chunking(lim,chunk_size):
    chunks=(lim[1]-lim[0])//chunk_size
    chunks_tail=(lim[1]-lim[0])%chunk_size
    if chunks_tail>0:
        total_chunks=chunks+1
    else:
        total_chunks=chunks
    return chunks,chunks_tail,total_chunks
    
    

time_chunk_size=500
depth_chunk_size=500
freq_chunk_size=500


start_time=datetime.datetime.now()
    

img_file_folder = os.path.dirname(img_file)

F = h5.File(fftrawout_file,'r')
img_hdf=h5.File(img_file, 'w-')


depth_hdf = int(F['data'].shape[1])
time_hdf = int(F['data'].shape[0])
freq_hdf = int(F['data'].shape[2])

print 'hdf dataset shape=', F['data'].shape

if depth_lim==-1:
    depth_lim=[0,depth_hdf]

if freq_lim==-1:
    freq_lim=[0,freq_hdf]

if time_lim==-1:
    time_lim=[0,time_hdf]


depth_chunks,depth_chunks_tail,total_depth_chunks=chunking(depth_lim,depth_chunk_size)
time_chunks,time_chunks_tail,total_time_chunks=chunking(time_lim,time_chunk_size)
freq_chunks,freq_chunks_tail,total_freq_chunks=chunking(freq_lim,freq_chunk_size)
total_img_cnt=total_time_chunks*total_freq_chunks*len(depths)

#################### tf plots
img_hdf.create_group('/tf')



global_cnt=0    

# loop depth chunks
for d in depths:

    img_hdf.create_group('/tf/%i' % d)    
    ds_cnt=0
    # loop time chunks
    for t in range(time_chunks+1):

        from_time_idx=time_lim[0]+t*time_chunk_size
        if t==time_chunks:      
            if time_chunks_tail==0:
                break     
            else:            
                to_time_idx=from_time_idx+time_chunks_tail  
        else:            
            to_time_idx=time_lim[0]+(t+1)*time_chunk_size  

        # loop frequency chunks
        for f in range(freq_chunks+1):   
            
            gc.collect()
            del gc.garbage[:]                     
            from_freq_idx=freq_lim[0]+f*freq_chunk_size                        
            if f==freq_chunks:
                if freq_chunks_tail==0:
                    break
                else:
                    to_freq_idx=from_freq_idx+freq_chunks_tail  
            else:            
                to_freq_idx=freq_lim[0]+(f+1)*freq_chunk_size            
            
            
            
            print '%i/%i imgs' % (global_cnt+1,total_img_cnt)," => ", \
                    'tf =>', \
                    'd=%s / ' % str(d), \
                    't=%s,%s / ' % (str(from_time_idx),str(to_time_idx)), \
                    'f=%s,%s ' % (str(from_freq_idx),str(to_freq_idx))                                            

            hdf_data=F['data'][from_time_idx:to_time_idx, d, from_freq_idx:to_freq_idx]
            data=np.array(np.rint(np.transpose(10.0*np.log10(np.array(hdf_data)))),dtype='int8')

#            if img_type=='plt':
#                fig = plt.figure(frameon=False)
#                fig.set_size_inches(1,1)
#                ax = plt.Axes(fig, [0., 0., 1., 1.])
#                ax.set_axis_off()
#                fig.add_axes(ax)            
#                myplot=ax.imshow(data,aspect='auto',interpolation='none',vmin=vmin,vmax=vmax)
#                ax.invert_yaxis()   
#                fig.savefig(os.path.join(img_file_folder,'buffer.png'),dpi=int(np.mean([time_chunk_size,freq_chunk_size])/img_dpi_defac))             
#                fig.clf()
#                plt.close()                        
#                img_pil=Image.open(os.path.join(img_file_folder,'buffer.png'))
#                img_arr=np.asarray(img_pil)
#                
#            elif img_type=='cm':            
#                normalizer = colors.Normalize(vmin=vmin, vmax=vmax, clip=True)
#                colormap = cm.get_cmap(name='jet')
#                colormap.set_bad('k', 1.0) # sets black color for NaN etc
#                sm = cm.ScalarMappable(norm=normalizer, cmap=colormap)
#                img_arr = sm.to_rgba(data, bytes=False)


            
#            if f==0 and t==0 and global_cnt==0: # see if cmap is good, if not stop
#
#                fig = plt.figure(figsize=(18, 8))                
#                ax1 = plt.subplot(121)
#                ax2 = plt.subplot(122)
#                myplot1=ax1.imshow(data,aspect='auto',interpolation='none',vmin=vmin,vmax=vmax)
#                if img_type=='plt':                
#                    test_img=Image.fromarray(np.uint8(img_arr))                    
#                    myplot2=ax2.imshow(test_img,aspect='auto',interpolation='none')  
#                    ax1.invert_yaxis()                                   
#                elif img_type=='cm':                 
#                    myplot2=ax2.imshow(img_arr,aspect='auto',interpolation='none')                    
#                    ax2.invert_yaxis()                     
#                plt.show()
#                fig.clf()
#                plt.close()
#                good=raw_input('good? (y/n):')
#                if good=='n':
#                    sys.exit()                    
            
            # create dataset and put numpy array image there
            ds_str='/tf/'+str(d)+'/'+str(ds_cnt)
#            img_hdf.create_dataset(ds_str,data=img_arr)
            img_hdf.create_dataset(ds_str,data=data)
            img_hdf[ds_str].attrs['depth']=d
            img_hdf[ds_str].attrs['freqs']=[from_freq_idx,to_freq_idx]
            img_hdf[ds_str].attrs['times']=[from_time_idx,to_time_idx]
            ds_cnt+=1
            global_cnt+=1
            
            # clear memory
            gc.collect()
            del gc.garbage[:]

            
            

 
 
##################### df plots 
#img_hdf.create_group('/df')
#
#ds_cnt=0  
#for t in range(time_lim[0],time_lim[1],1):
#
#    for d in range(depth_chunks+1):
#
#        from_depth_idx=depth_lim[0]+d*depth_chunk_size
#        if d==depth_chunks and depth_chunks_tail>0:      
#            if depth_chunks_tail>0:
#                to_depth_idx=from_depth_idx+depth_chunks_tail  
#            else:
#                break 
#        else:            
#            to_depth_idx=depth_lim[0]+(d+1)*depth_chunk_size            
#            
#        for f in range(freq_chunks+1):
#        
#            from_freq_idx=freq_lim[0]+f*freq_chunk_size                        
#            if f==freq_chunks:
#                if freq_chunks_tail>0:
#                    to_freq_idx=from_freq_idx+freq_chunks_tail  
#                else:
#                    break
#            else:            
#                to_freq_idx=freq_lim[0]+(f+1)*freq_chunk_size
#                
#            print 'df plots=>','d=',from_depth_idx,to_depth_idx,' / ', 'f=',from_freq_idx,to_freq_idx
#            print '%i img out of %i imgs' % (ds_cnt,depth_chunks*freq_chunks*(time_lim[1]-time_lim[0]))
#                            
#            data=np.array(10.0*np.log10(\
#                    np.array(\
#                        F['data']\
#                                [t,\
#                                from_depth_idx:to_depth_idx,\
#                                from_freq_idx:to_freq_idx]\
#                    ).T))  
#
#            fig, ax = plt.subplots(figsize=(10, 8),dpi=100)
#            myplot=ax.imshow(data,interpolation='none',aspect='auto',vmin=vmin,vmax=vmax)
#            ax.invert_yaxis()
#            ax.set_position([0.001,0.001, 0.998, 0.997])
#                    
#            img_arr=np.asarray(fig2img(fig))            
#            img_hdf.create_dataset('/df/'+str(ds_cnt),data=img_arr)
#            img_hdf['/df/'+str(ds_cnt)].attrs['time']=d
#            img_hdf['/df/'+str(ds_cnt)].attrs['freqs']=[from_freq_idx,to_freq_idx]
#            img_hdf['/df/'+str(ds_cnt)].attrs['depths']=[from_depth_idx,to_depth_idx]            
#
#            fig.clf()
#            plt.close()
#            gc.collect()
#            ds_cnt+=1


img_hdf.close()
F.close()

print 'started - ', start_time
print 'finished - ', datetime.datetime.now()


