

""" =============================HEADER============================================ """


fftrawout_file =  r'W:\Data\CoP\A-05\DAS\fft_test\proc1\2014.08.18.09.33.21.hdf_rechunked2.hdf'
img_file =  r'D:\COP_A05\img_file.hdf'

prf = 5000

# plots to make
tf_depths=[
            5224,5420,5857,6392
        ]

td_freqs=[
            [100,500]
        ]
        
df_times=[
            
            0
            
        ]


# for tf and df data
freq_lim=-1
depth_lim=[4000,7800]
time_lim=[0,500]

# colormap lims
vmin=0.0
vmax=40.0
img_type='int'
img_dpi_defac=1 # for plt only

time_chunk_size=100
depth_chunk_size=100
freq_chunk_size=100
default_dpi=100



""" =============================END============================================== """



import numpy as np
import h5py as h5
import gc
import os
import datetime




def chunking(lim,chunk_size):
    chunks=(lim[1]-lim[0])//chunk_size
    chunks_tail=(lim[1]-lim[0])%chunk_size
    if chunks_tail>0:
        total_chunks=chunks+1
    else:
        total_chunks=chunks
    return [chunks,chunks_tail,total_chunks,lim,chunk_size]
    


def make_imgs(plot_type,global_cnt,plot_vars,x_par,y_par,vmin,vmax,img_type):

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


    img_hdf.create_group('/%s' % plot_type)       
    
    for i in plot_vars:
        
        if type(i) is list:            
            img_hdf.create_group('/%s/%i_%i' % (plot_type,i[0],i[1]))            
        else:
            img_hdf.create_group('/%s/%i' % (plot_type,i))      

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

                print '%i/%i imgs / %s / x(%s,%s) / y(%s,%s)' % \
                            (global_cnt+1,total_img_cnt,plot_type,from_x_idx,to_x_idx,from_y_idx,to_y_idx)
 
                
                if type(i) is list:    
                                                                      
                    if plot_type=='tf':                               
                        hdf_data=F['data'][from_x_idx:to_x_idx, i[0]:i[1], from_y_idx:to_y_idx]
                        data=np.mean(hdf_data,axis=1).T
                    elif plot_type=='td':
                        hdf_data=F['data'][from_x_idx:to_x_idx, from_y_idx:to_y_idx, i[0]:i[1]]
                        data=np.mean(hdf_data,axis=2).T
                    elif plot_type=='df':
                        hdf_data=F['data'][i[0]:i[1],from_x_idx:to_x_idx, from_y_idx:to_y_idx]
                        data=np.mean(hdf_data,axis=0)
                        
                else:
                                             
                    if plot_type=='tf':                               
                        data=np.array(F['data'][from_x_idx:to_x_idx, i, from_y_idx:to_y_idx]).T
                    elif plot_type=='td':
                        data=np.array(F['data'][from_x_idx:to_x_idx, from_y_idx:to_y_idx, i]).T
                    elif plot_type=='df':
                        data=np.array(F['data'][i,from_x_idx:to_x_idx, from_y_idx:to_y_idx])
               

                
                # create dataset and put numpy array image there
                if type(i) is list: 
                    ds_str='/'+plot_type+'/'+str(i[0])+'_'+str(i[1])+'/'+str(ds_cnt)                
                else:
                    ds_str='/'+plot_type+'/'+str(i)+'/'+str(ds_cnt)                                    

                img_hdf.create_dataset(ds_str,data=data)
                
                if plot_type=='tf':                    
                    img_hdf[ds_str].attrs['depth']=i
                    img_hdf[ds_str].attrs['freqs']=[from_y_idx,to_y_idx]
                    img_hdf[ds_str].attrs['times']=[from_x_idx,to_x_idx]
                if plot_type=='td':
                    img_hdf[ds_str].attrs['freq']=i
                    img_hdf[ds_str].attrs['depths']=[from_y_idx,to_y_idx]
                    img_hdf[ds_str].attrs['times']=[from_x_idx,to_x_idx]
                if plot_type=='df':
                    img_hdf[ds_str].attrs['time']=i
                    img_hdf[ds_str].attrs['freqs']=[from_y_idx,to_y_idx]
                    img_hdf[ds_str].attrs['depths']=[from_x_idx,to_x_idx]                    
                    
                ds_cnt+=1
                global_cnt+=1
                
                # clear memory
                gc.collect()
                del gc.garbage[:]

    return global_cnt





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

# define chunks
depth_chunk_par=chunking(depth_lim,depth_chunk_size)
time_chunk_par=chunking(time_lim,time_chunk_size)
freq_chunk_par=chunking(freq_lim,freq_chunk_size)

#print depth_chunk_par
#print time_chunk_par
#print freq_chunk_par



# number of images to produce
total_img_cnt=time_chunk_par[2]*freq_chunk_par[2]*len(tf_depths)+\
                freq_chunk_par[2]*depth_chunk_par[2]*len(df_times)+\
                time_chunk_par[2]*depth_chunk_par[2]*len(td_freqs)

# counter for images produced
global_cnt=0 

############# tf plots
if len(tf_depths) != 0:
    global_cnt=make_imgs('tf',global_cnt,tf_depths,time_chunk_par,freq_chunk_par,vmin,vmax,img_type)

############# td plots
if len(td_freqs) != 0:
    global_cnt=make_imgs('td',global_cnt,td_freqs,time_chunk_par,depth_chunk_par,vmin,vmax,img_type)

############# df plots
if len(df_times) != 0:
    global_cnt=make_imgs('df',global_cnt,df_times,depth_chunk_par,freq_chunk_par,vmin,vmax,img_type)


img_hdf.close()
F.close()

print 'started - ', start_time
print 'finished - ', datetime.datetime.now()


