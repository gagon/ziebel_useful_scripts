# -*- coding: utf-8 -*-
"""
Created on Mon Sep 08 10:21:11 2014

@author: bolatzh
"""

#main_dir=r'W:\Data\Maersk\HDA-33\DAS\DISKS'
main_dir='/mnt/A1-Data1/Data/BP/G-21_2015/DAS/oct/Shut-in'

import os

for root, dirs, files in os.walk(main_dir):
    for f in files:
        if f.endswith('.hdf'):
#            print '"'+os.path.join(root,f)+'",',round(os.path.getsize(os.path.join(root,f))/(1024.0)**3,4)
            print '"'+os.path.join(root,f)+'",'



#for root, dirs, files in os.walk(main_dir):
#    for f in files:
#        if f.endswith('.json'):
#            print 'python main_logs.py '+os.path.join(root,f)
