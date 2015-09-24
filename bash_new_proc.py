# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 10:21:37 2015

@author: bolat
"""

import os
import datetime

folder="/media/ziebel/Disk 639/VALHALL"
octfolder="/mnt/A1-Data1/Data/BP/A10/DAS/DAS_Processed/oct_1sec_time_resolution"
tilesfolder="/mnt/A1-Data1/Data/BP/A10/DAS/DAS_Processed/tiles_1sec_time_resolution"
tilefile="bp_a10_tiles.hdf"
fftfolder=""
fftfile=""

blocksize=15000

lines=[]

for root, dirs, files in os.walk(folder):
    for f in files:
        if f.endswith('.fds'):
            
            line="mpirun -n 7 procrunner --filename "
            line+=os.path.join(root,f)                
            
            line+=" --blocksize "
            line+=str(blocksize)                
            line+=" --octout "

            try:
                dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[3])[0],"%Y.%m.%d.%H.%M.%S")
                line+=os.path.join(octfolder,os.path.splitext(os.path.basename(f).split('_')[3])[0]+".hdf")
                
            except:
                try:
                    dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[5])[0],"%Y.%m.%d.%H.%M.%S")
                    line+=os.path.join(octfolder,os.path.splitext(os.path.basename(f).split('_')[5])[0]+".hdf")

                except:
                    try:
                        dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[6])[0],"%Y.%m.%d.%H.%M.%S")
                        line+=os.path.join(octfolder,os.path.splitext(os.path.basename(f).split('_')[6])[0]+".hdf")

                    except:
                        try:
                            dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[7])[0],"%Y.%m.%d.%H.%M.%S")
                            line+=os.path.join(octfolder,os.path.splitext(os.path.basename(f).split('_')[7])[0]+".hdf")

                        except:                                
                            try:
                                dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[2])[0][10:],"%Y.%m.%d.%H.%M.%S")
                                line+=os.path.join(octfolder,os.path.splitext(os.path.basename(f).split('_')[2])[0][10:]+".hdf")

                            except:                                                                    
                                dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[4])[0],"%Y.%m.%d.%H.%M.%S")                                
                                line+=os.path.join(octfolder,os.path.splitext(os.path.basename(f).split('_')[4])[0]+".hdf")


            
            if tilesfolder!="":
                line+=" --tileout "
                line+=os.path.join(tilesfolder,tilefile)

            if fftfolder!="":
                line+=" --fftrawout "
                
                try:
                    dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[3])[0],"%Y.%m.%d.%H.%M.%S")
                    line+=os.path.join(fftfolder,os.path.splitext(os.path.basename(f).split('_')[3])[0]+".hdf")
                
                except:
                    try:
                        dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[5])[0],"%Y.%m.%d.%H.%M.%S")
                        line+=os.path.join(fftfolder,os.path.splitext(os.path.basename(f).split('_')[5])[0]+".hdf")
    
                    except:
                        try:
                            dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[6])[0],"%Y.%m.%d.%H.%M.%S")
                            line+=os.path.join(fftfolder,os.path.splitext(os.path.basename(f).split('_')[6])[0]+".hdf")
    
                        except:
                            try:
                                dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[7])[0],"%Y.%m.%d.%H.%M.%S")
                                line+=os.path.join(fftfolder,os.path.splitext(os.path.basename(f).split('_')[7])[0]+".hdf")
    
                            except:                                
                                try:
                                    dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[2])[0][10:],"%Y.%m.%d.%H.%M.%S")
                                    line+=os.path.join(fftfolder,os.path.splitext(os.path.basename(f).split('_')[2])[0][10:]+".hdf")
    
                                except:                                                                    
                                    dt=datetime.datetime.strptime(os.path.splitext(os.path.basename(f).split('_')[4])[0],"%Y.%m.%d.%H.%M.%S")                                
                                    line+=os.path.join(fftfolder,os.path.splitext(os.path.basename(f).split('_')[4])[0]+".hdf")



            
            lines.append([dt,line])
                
lines=sorted(lines,key=lambda x: x[0])

for line in lines:
    print line[1]
