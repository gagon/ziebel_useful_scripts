

""" =============================HEADER============================================ """


fftrawout_file =  r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_fftraw\2015.08.06.00.12.02.hdf'
img_file =  r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_fftraw\img_file1.hdf'



prf = 5000

# depth points for tf data
depths=[1000,4000,5000]

# for tf and df data
freq_lim=[0,50]
depth_lim=-1
time_lim=-1


# colormap lims
vmin=0
vmax=40

test=False


""" =============================END============================================== """


import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import gc
import os
import sys
import Image
import scipy




time_chunk_size=200
depth_chunk_size=200
freq_chunk_size=100



    

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


depth_chunks=(depth_lim[1]-depth_lim[0])//depth_chunk_size
depth_chunks_tail=(depth_lim[1]-depth_lim[0])%depth_chunk_size

time_chunks=(time_lim[1]-time_lim[0])//time_chunk_size
time_chunks_tail=(time_lim[1]-time_lim[0])%time_chunk_size

freq_chunks=(freq_lim[1]-freq_lim[0])//freq_chunk_size
freq_chunks_tail=(freq_lim[1]-freq_lim[0])%freq_chunk_size





#################### tf plots
img_hdf.create_group('/tf')



ds_cnt=0    

# loop depth chunks
for d in depths:
    
    # loop time chunks
    for t in range(time_chunks+1):

        from_time_idx=time_lim[0]+t*time_chunk_size

        if t==time_chunks and time_chunks_tail>0:      
            if time_chunks_tail>0:
                to_time_idx=from_time_idx+time_chunks_tail  
            else:
                break 
        else:            
            to_time_idx=time_lim[0]+(t+1)*time_chunk_size            
        
        # loop frequency chunks
        for f in range(freq_chunks+1):        

            from_freq_idx=freq_lim[0]+f*freq_chunk_size                        

            if f==freq_chunks:
                if freq_chunks_tail>0:
                    to_freq_idx=from_freq_idx+freq_chunks_tail  
                else:
                    break
            else:            
                to_freq_idx=freq_lim[0]+(f+1)*freq_chunk_size
               
            print '%i img out of %i imgs' % (ds_cnt,time_chunks*(freq_chunks+1)*len(depths))," => ",\
                    'tf plots=>','t=',from_time_idx,to_time_idx,' / ', 'f=',from_freq_idx,to_freq_idx                                              

            data=np.array(10.0*np.log10(\
                    np.array(\
                        F['data']\
                                [from_time_idx:to_time_idx,\
                                d,\
                                from_freq_idx:to_freq_idx]\
                    ).T))  

#            img_pil=scipy.misc.toimage(data, cmin=vmin, cmax=vmax)
#            print img_pil

            fig = plt.figure(frameon=False)
            fig.set_size_inches(10,8)
            ax = plt.Axes(fig, [0., 0., 1., 1.])
            ax.set_axis_off()
            fig.add_axes(ax)

            myplot=ax.imshow(data,interpolation='none',aspect='auto',vmin=vmin,vmax=vmax)
            ax.invert_yaxis()
#            ax.set_position([0.001,0.001, 0.998, 0.997])

            if ds_cnt==0:
                plt.show()
                good=raw_input('good? (y/n):')
                if good=='n':
                    sys.exit()                    
            
            fig.savefig(os.path.join(img_file_folder,'buffer.png'))


                                                          
            img_arr_png=Image.open(os.path.join(img_file_folder,'buffer.png'))
            
            img_arr=np.asarray(img_arr_png)                      
            
            
            img_hdf.create_dataset('/tf/'+str(ds_cnt),data=img_arr)
            img_hdf['/tf/'+str(ds_cnt)].attrs['depth']=d
            img_hdf['/tf/'+str(ds_cnt)].attrs['freqs']=[from_freq_idx,to_freq_idx]
            img_hdf['/tf/'+str(ds_cnt)].attrs['times']=[from_time_idx,to_time_idx]


            # for testing      
            if test:
                new_img_png=Image.fromarray(img_arr)      
                fig, ax = plt.subplots(figsize=(10, 8),dpi=100)            
                myplot=ax.imshow(new_img_png,aspect='auto')
                ax.set_position([0.001,0.001, 0.998, 0.997])            
                plt.show()
                sys.exit()

            ds_cnt+=1
            
            del img_arr
            del img_arr_png
            fig.clf()
            fig.clear()
            plt.cla()
            plt.clf()
            plt.close() 
            gc.collect()
            

 
 
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


