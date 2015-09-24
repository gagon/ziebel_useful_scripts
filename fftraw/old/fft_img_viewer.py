# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 09:58:02 2015

@author: bolatzh
"""

import os
import Image
import matplotlib.pyplot as plt

plot_folder=r'Y:\Data\US\CoP\Buck_Federal_17-5H\DAS\DAS_fftraw\fftraw_plots\images4'
depth=5000


fig = plt.figure(figsize=(18, 8))
#ax1 = plt.subplot(gs[:7,:])
ax1 = plt.subplot()

for root, dirs, files in os.walk(plot_folder):
    for f in files:
        if f.endswith('.png'):
            head,ext=os.path.splitext(f)
            t=int(head.split('_')[0])
            d=int(head.split('_')[1])
            if d==depth:
                print 'plotting %s' % f
                im=Image.open(os.path.join(root,f))            
                extent=[t,t+1,1,0]
                ax1.imshow(im,origin='upper',extent=extent,aspect='auto')

plt.show()