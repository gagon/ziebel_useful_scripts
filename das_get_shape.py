# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 15:46:14 2014

@author: bolatzh
"""

import h5py
import os

folders= [\
r"Y:\Data\US\BHP\B5H\DAS\Donnell\B5H\Run.1\SEQ.PRO1\ZNsAsDATE\octavebands",
r"Y:\Data\US\BHP\B5H\DAS\Donnell\B5H\Run.1\SEQ.PRO2\1\ZNsAsDATE\octavebands",
r"Y:\Data\US\BHP\B5H\DAS\Donnell\B5H\Run.1\SEQ.PRO2\2\ZNsAsDATE\octavebands",
r"Y:\Data\US\BHP\B5H\DAS\Donnell\B5H\Run.1\SEQ.PRO2\3\ZNsAsDATE\octavebands",
r"Y:\Data\US\BHP\B5H\DAS\Donnell\B5H\Run.1\SEQ.PRO2\4\ZNsAsDATE\octavebands",
r"Y:\Data\US\BHP\B5H\DAS\Donnell\B5H\Run.1\SEQ.PRO3\ZNsAsDATE\octavebands",
r"Y:\Data\US\BHP\B5H\DAS\Donnell\B5H\Run.1\SEQ.SI1\ZNsAsDATE\octavebands",
r"Y:\Data\US\BHP\B5H\DAS\Donnell\B5H\Run.1\SEQ.SI2\ZNsAsDATE\octavebands"
]

processing="new"

for folder in folders:
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith(".hdf"):               
                hdf_file=os.path.join(root,f)
                hdf=h5py.File(hdf_file, "r")
                if processing=="old":                                        
                    shape=hdf["/OUTdata/DASdata/OCTdata/13Octaves/13Octaves"].shape
                elif processing=="new":
                    shape=hdf['data'].shape
                    
                print os.path.join(root,f),"->",shape
                hdf.close()


