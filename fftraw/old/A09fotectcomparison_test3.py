import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import gc
import os
from scipy.integrate import simps, trapz
import matplotlib.gridspec as gridspec


#f = r'W:\Data\CoP\A-05\DAS\fft_test\proc1\2014.08.18.09.33.21.hdf'
f =  r'W:\Data\CoP\A-05\DAS\fft_test\proc1\2014.08.18.09.33.21.hdf'
plot_folder=r'W:\Data\CoP\A-05\DAS\fft_test\images6'

depth = 7835
time = 1199
freqs = 7501
prf = 5000 # PRF
numblock = 1024 # timeblockcount


Farr = np.array([i*(prf/2.0/freqs) for i in range(freqs)]) # frequencies

das_scale_min=0
das_scale_max=50
freq=5
d1=10
d2=100
d3=500

F = h5.File(f,'r')

#data=np.array(10.0*np.log10(np.array(F['data'][:,3000:,freq])))
#data=np.array(np.log(np.array(F['data'][:,3000:,freq])))
#data=np.array(F['data'][:,3000:,freq])

data=10.0*np.array(np.log10(np.array(F['data'][:,3000,:500])))


gs=gridspec.GridSpec(10,1)    
fig = plt.figure(figsize=(18, 8))
ax1 = plt.subplot()
#ax1 = plt.subplot(gs[:4,:])
#ax2 = plt.subplot(gs[4:,:], sharex=ax1)   


myplot1=ax1.imshow(np.array(np.transpose(data)),aspect='auto',vmin=das_scale_min,vmax=das_scale_max,cmap="jet", interpolation="none")
#myplot1=ax1.imshow(np.array(np.transpose(data)),aspect='auto',cmap="jet", interpolation="none")

#myplot2=ax2.plot([i for i in range(len(data[:,d1]))],data[:,d1])
#myplot2=ax2.plot([i for i in range(len(data[:,d2]))],data[:,d2])
#myplot2=ax2.plot([i for i in range(len(data[:,d3]))],data[:,d3])
plt.show()



#ax.set_position([0.001,0.001, 0.998, 0.997])
#fig.savefig(os.path.join(plot_folder,'sample_data.png'))     
#fig.clf()
#plt.close()
#gc.collect()

#chunk=10
#for j in range(0,time,chunk):
#    print j    
#    data=np.array(10.0*np.log10(F['data'][j:j+chunk,3000:,:500]))    
#    for i in range(chunk):    
#        fig, ax = plt.subplots(figsize=(10, 8),dpi=50)
#        myplot=ax.imshow(data[i,:,:],interpolation='none',aspect='auto',vmin=10,vmax=50)  
#        ax.set_position([0.001,0.001, 0.998, 0.997])
#        fig.savefig(os.path.join(plot_folder,str(j+i)+'.png'))     
#        fig.clf()
#        plt.close()
#        gc.collect()



    
F.close()


