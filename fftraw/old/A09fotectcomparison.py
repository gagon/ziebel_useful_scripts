import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import gc
import os
from scipy.integrate import simps, trapz


#f = r'W:\Data\CoP\A-05\DAS\fft_test\proc1\2014.08.18.09.33.21.hdf'
f =  r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_fftraw\2015.08.06.00.12.02.hdf'
plot_folder=r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_fftraw\fftraw_plots\images1'

depth = 5782
time = 4642
freqs = 2501
prf = 5000 # PRF
numblock = 1024 # timeblockcount

depth_top_idx=0
depth_bot_idx=depth


Farr = np.array([i*(prf/2.0/freqs) for i in range(freqs)]) # frequencies




F = h5.File(f,'r')

#data=np.array(10.0*np.log10(np.sum(np.array(F['data'][:,3000:,10:20]),axis=2)))
#fig, ax = plt.subplots(figsize=(10, 8),dpi=50)
#myplot=ax.imshow(data.T,interpolation='none',aspect='auto',vmin=10,vmax=50)  
#ax.set_position([0.001,0.001, 0.998, 0.997])
#fig.savefig(os.path.join(plot_folder,'sample_data.png'))     
#fig.clf()
#plt.close()
#gc.collect()

chunk=10
for j in range(0,time,chunk):
    print j    
    data=np.array(10.0*np.log10(F['data'][j:j+chunk,3000:,:500]))    
    for i in range(chunk):    
        fig, ax = plt.subplots(figsize=(10, 8),dpi=50)
        myplot=ax.imshow(data[i,:,:],interpolation='none',aspect='auto',vmin=10,vmax=50)  
        ax.set_position([0.001,0.001, 0.998, 0.997])
        fig.savefig(os.path.join(plot_folder,str(j+i)+'.png'))     
        fig.clf()
        plt.close()
        gc.collect()



    
F.close()


