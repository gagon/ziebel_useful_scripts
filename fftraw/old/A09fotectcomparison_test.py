import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import os
import gc

f = r'W:\Data\CoP\A-05\DAS\fft_test\proc1\2014.08.18.09.33.21.hdf'


depth = 7835
time = 1199
freqs = 7501
s = 5000 # PRF
n = 1024 # timeblockcount
Fstart = 1000   #Hz Filter begin frequency
Fend   = 1500 #Hz Filter end frequency

#F = np.array([i*(s/n) for i in np.arange(freqs)]) # frequencies
F = np.array([i*(s/n) for i in np.arange(freqs)]) # frequencies
bw = Fend - Fstart # Bandwidth
Fs_idx = np.argmin(np.abs(F - Fstart))
Fe_idx = np.argmin(np.abs(F - Fend))
bc = Fe_idx - Fs_idx

print(Fs_idx,Fe_idx)
print(bc,bw)


alldata=[]
for t in range(time):
    
    F = h5.File(f,'r')
    D = F['data'][t,5000:7000,:]
    
    fig, ax = plt.subplots(figsize=(20, 16),dpi=600)
#    Fdata = 10*np.log10(np.sum(np.array(D)**2/1e1**2, axis=2))

    noise=100
    Fdata = 10*np.log10(np.array(D)/float(noise)**2)

    
    vmin=0
    vmax=50
    ax.imshow(Fdata.T,interpolation='none',aspect='auto',vmin=vmin,vmax=vmax)
    fig.savefig(os.path.join(r'W:\Data\CoP\A-05\DAS\fft_test\images\%s' % str(noise),'t%s_cm%s-%s_n%s.png' % (t,vmin,vmax,noise)))
    
    fig.clf()
    plt.close()
    gc.collect()

#    plt.show()
    
F.close()
