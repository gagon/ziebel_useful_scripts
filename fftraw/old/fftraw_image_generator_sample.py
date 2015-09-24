

""" =============================HEADER============================================ """


f =  r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_fftraw\2015.08.06.00.12.02.hdf'
plot_folder=r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_fftraw\fftraw_plots\images3'

depth = 5781
time = 4642
freqs = 2501
prf = 5000

depth_top_idx=4000
depth_bot_idx=4050
freq_top_idx=0
freq_bot_idx=10


""" =============================END============================================== """




import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import gc
import os




F = h5.File(f,'r')

   

bs=100
d=5000
from_freq=0
to_freq=200

for j in range(40):

    print j 
    data=np.array(10.0*np.log10(np.array(F['data'][j*bs:(j+1)*bs,d,from_freq:to_freq]).T))  
    fig, ax = plt.subplots(figsize=(10, 8),dpi=60)
    myplot=ax.imshow(data,interpolation='none',aspect='auto',vmin=10,vmax=50)  
    ax.set_position([0.001,0.001, 0.998, 0.997])
    fig.savefig(os.path.join(plot_folder,str(j)+'_'+str(d)+'.png'))     
    fig.clf()
    plt.close()
    gc.collect()

#plt.show()
F.close()


