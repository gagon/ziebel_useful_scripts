import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import gc
import os

f = r'W:\Data\CoP\A-05\DAS\fft_test\proc1\2014.08.18.09.33.21.hdf'


depth = 7835
time = 1199
freqs = 7501
s = 5000 # PRF
n = 1024 # timeblockcount
Fstart = 1000   #Hz Filter begin frequency
Fend   = 1500 #Hz Filter end frequency


    
#F = np.array([i*(s/n) for i in np.arange(freqs)]) # frequencies
#F = np.array([i for i in np.arange(freqs)]) # frequencies


F = h5.File(f,'r')

for t in range(10):


    D = F['data'][t,5000:7000,:]

    fig, ax = plt.subplots(figsize=(20, 16),dpi=600)
    vmin=0
    vmax=50    
    ax.imshow(D.T,interpolation='none',aspect='auto',vmin=vmin,vmax=vmax)    
    fig.savefig(os.path.join(r'W:\Data\CoP\A-05\DAS\fft_test\images','t%s_cm%s-%s_n%s.png' % (t,vmin,vmax)))    
    
    fig.clf()
    plt.close()
    gc.collect()

F.close()
