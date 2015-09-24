
import os
import numpy as np
import time

folder=r"C:\Users\bolatzh\Documents\testing"

i=0
while True:
    print str(i)+".txt"
    new_data=np.array([np.arange(10),np.random.rand(10)])
    np.savetxt(os.path.join(folder,str(i)+".txt"),new_data,delimiter=",")    
    i+=1
    time.sleep(3)
    
