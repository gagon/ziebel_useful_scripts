

""" =============================HEADER============================================ """


f =  r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_fftraw\2015.08.06.00.12.02.hdf'
plot_folder=r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_fftraw\fftraw_plots\images2'

depth = 5781
time = 4642
freqs = 2501
prf = 5000

depth_top_idx=4000
depth_bot_idx=depth
freq_top_idx=0
freq_bot_idx=500


""" =============================END============================================== """




import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import gc
import os




F = h5.File(f,'r')

chunk=10
for j in range(0,time,chunk):
#    print [j,j+chunk,depth_top_idx,depth_bot_idx,freq_top_idx,freq_bot_idx]
    print j    
    data=np.array(10.0*np.log10(F['data'][j:j+chunk,depth_top_idx:depth_bot_idx,freq_top_idx:freq_bot_idx]))    
    for i in range(chunk):    
        fig, ax = plt.subplots(figsize=(10, 8),dpi=600)
        myplot=ax.imshow(data[i,:,:],interpolation='none',aspect='auto',vmin=0,vmax=40)  
        ax.set_position([0.001,0.001, 0.998, 0.997])
        fig.savefig(os.path.join(plot_folder,str(j+i)+'.png'))     
        fig.clf()
        plt.close()
        gc.collect()
    
F.close()


