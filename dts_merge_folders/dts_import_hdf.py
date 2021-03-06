
import h5py
import datetime
import numpy as np
import pandas as pd
import matplotlib
import os


def import_hdf_data(dts_path, root_gr, dts_merged_path):
    print 'importing data from ziebel hdf format..'
      
    """ open hdf file """
    dts_orig_hdf = h5py.File(dts_path,'r')

    """ get list of dts groups """   
    dts_group_list=[] 
    dts_key_list=dts_orig_hdf[root_gr].keys() 
    for gr in dts_key_list:
        dts_group_list.append(u'Data/Calibrated_DTS/DTS/'+gr)    
 
    """ get depths from hdf file """    
    block_values=dts_orig_hdf[dts_group_list[0]+'/block0_values'][...]
    depths=np.transpose(block_values[0])[0]

    df=pd.DataFrame()
    for gr in dts_group_list:
        timestamps=dts_orig_hdf[gr+'/axis2'][...]
        timestamps_mt=[]    
        for t in timestamps:
            timestamps_mt.append(matplotlib.dates.date2num(datetime.datetime.strptime(t, "%Y/%m/%d %H:%M:%S")))
        temperature=np.array(np.transpose(np.transpose(dts_orig_hdf[gr+'/block0_values'][...])[1]))
        df=pd.concat([df,pd.DataFrame(temperature,index=timestamps_mt)])   
    
    df=df.sort_index()
    df.to_hdf(dts_merged_path,'orig_traces')
    
    dts_merged_hdf=h5py.File(dts_merged_path,'r+')
    del dts_merged_hdf['orig_traces/axis0']
    dts_merged_hdf.create_dataset('orig_traces/axis0',(1,),maxshape=(None,))
    dts_merged_hdf['orig_traces/axis0'].shape=((len(depths),))
    dts_merged_hdf['orig_traces/axis0'][:]=depths
     
    dts_merged_hdf.close()
    dts_orig_hdf.close()
    print 'finished importing..'


def create_merged_hdf(dts_merged_path):
    dts_merged_hdf=h5py.File(dts_merged_path,'w-')  
    dts_merged_hdf.close()



if __name__=="__main__":
      
    # INPUT ====================================
    well_name='A04'    
    dts_path=r'/mnt/A0-Data1/Data/BP/WP/A04/DTS_cal_dts/A04_cal_dts.hdf'      
    # END ======================================
    
    dts_dir,dts_file=os.path.split(dts_path)
    dts_merged_path=os.path.join(dts_dir,well_name+'_dts_merged.hdf')
    root_gr='Data/Calibrated_DTS/DTS'

    create_merged_hdf(dts_merged_path)
    import_hdf_data(dts_path,root_gr,dts_merged_path) 
    
