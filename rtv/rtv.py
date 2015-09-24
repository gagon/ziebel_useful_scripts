# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 09:42:14 2015

@author: bolatzh
"""

#import matplotlib.pyplot as plt
#import numpy as np
#import time
#import datetime
#
#for i in range(10):
#    data_stream=np.array([np.arange(100),np.random.rand(100)])
#    print data_stream[0][0],' / ',data_stream[1][0]
#    time.sleep(5)





import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


fig = plt.figure()

tr=1
data=np.random.rand(1000,tr)
data_trace_cnt=data.shape[1]
dummy_data=np.zeros((1000,100-data_trace_cnt))
plot_data=np.append(dummy_data,data,1)




im = plt.imshow(plot_data,aspect='auto')
plt.xlim(100,0)




def updatefig(*args):
    
    global tr
    if tr<100:
        tr+=1
        data=np.random.rand(1000,tr)
        data_trace_cnt=data.shape[1]
        dummy_data=np.zeros((1000,100-data_trace_cnt))
        plot_data=np.append(data,dummy_data,1)
    
        im.set_array(plot_data)


    return im,

ani = animation.FuncAnimation(fig, updatefig, interval=500000, blit=True)
plt.show()

