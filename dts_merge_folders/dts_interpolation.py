
import datetime
import numpy as np
import sys
from operator import itemgetter
import h5py
import dts_utils as utils
import pandas as pd
import os

  

def interpolate_traces(dts_merged_path,interpolate_all,interpolate_btw,max_delta):
    print 'start interpolation..'

    print 'fetching orig data..'

    dts_merged_hdf = h5py.File(dts_merged_path,'r+')
    
    timestamps_dt=utils.convert_from_mdate(dts_merged_hdf['orig_traces/axis1_rounded'][:])    
    traces=dts_merged_hdf['orig_traces/block0_values'][:]    
    averaging=dts_merged_hdf['orig_traces/averaging'][:]

    print 'doing interpolation..'
        
    interp_traces=[]
    interp_timestamps=[]
    interp_ind=0
    
    # put initial trace as orig
    interp_traces.append([traces[0].astype(np.float64),interp_ind])
    interp_timestamps.append([timestamps_dt[0],interp_ind,-1,'orig'])
    interp_ind=interp_ind+1    
       
    
    for i in xrange(1,len(timestamps_dt)):
        t0=timestamps_dt[i-1]
        t1=timestamps_dt[i]      
        delta=int((t1-t0).total_seconds()/60)
        clone_trace=traces[i].astype(np.float64)
        clone_averaging=int(averaging[i])
        trace_grad=(traces[i].astype(np.float64)-traces[i-1].astype(np.float64))/float(delta)

        if interpolate_all:                        
            if delta==1:
                interp_traces.append([clone_trace.tolist(),interp_ind])
                interp_timestamps.append([t1,interp_ind,clone_averaging,'orig'])
                interp_ind=interp_ind+1
            else:
                for t in xrange(delta):
                    if t==0:
                        interp_traces.append([clone_trace.tolist(),interp_ind])
                        interp_timestamps.append([t1,interp_ind,clone_averaging,'orig'])
                    else:
                        tr=clone_trace-trace_grad*t
                        interp_traces.append([tr.tolist(),interp_ind])
                        interp_timestamps.append([t1-datetime.timedelta(minutes=t),interp_ind,clone_averaging,'interp'])
                    interp_ind=interp_ind+1 
        else:
            if clone_averaging==-1:
                for t in xrange(delta):
                    if t==0:
                        interp_traces.append([clone_trace.tolist(),interp_ind])
                        interp_timestamps.append([t1,interp_ind,clone_averaging,'orig'])
                    else:
                        interp_traces.append([np.zeros(len(clone_trace)).tolist(),interp_ind])
                        interp_timestamps.append([t1-datetime.timedelta(minutes=t),interp_ind,-1,'dummy'])
                    interp_ind=interp_ind+1
            else:
                if delta==1:
                    interp_traces.append([clone_trace.tolist(),interp_ind])
                    interp_timestamps.append([t1,interp_ind,clone_averaging,'orig'])
                    interp_ind=interp_ind+1
                else:
                    if delta<max_delta:
                        for t in xrange(delta):
                            if t==0:
                                interp_traces.append([clone_trace.tolist(),interp_ind])
                                interp_timestamps.append([t1,interp_ind,clone_averaging,'orig'])
                            else:
                                interp_traces.append([clone_trace.tolist(),interp_ind])
                                interp_timestamps.append([t1-datetime.timedelta(minutes=t),interp_ind,clone_averaging,'clone'])
                            interp_ind=interp_ind+1
                    elif delta<=clone_averaging+1:
                        for t in xrange(delta):
                            if t==0:
                                interp_traces.append([clone_trace.tolist(),interp_ind])
                                interp_timestamps.append([t1,interp_ind,clone_averaging,'orig'])
                            else:
                                if interpolate_btw:
                                    tr=clone_trace-trace_grad*t
                                    interp_traces.append([tr.tolist(),interp_ind])
                                    interp_timestamps.append([t1-datetime.timedelta(minutes=t),interp_ind,clone_averaging,'interp'])
                                else:
                                    interp_traces.append([clone_trace.tolist(),interp_ind])
                                    interp_timestamps.append([t1-datetime.timedelta(minutes=t),interp_ind,clone_averaging,'clone'])
                            interp_ind=interp_ind+1
                    else: # delta>clone_averaging
                        for t in xrange(delta):
                            if t==0:
                                interp_traces.append([clone_trace.tolist(),interp_ind])
                                interp_timestamps.append([t1,interp_ind,clone_averaging,'orig'])
                            else:
                                if t<clone_averaging:
                                    interp_traces.append([clone_trace.tolist(),interp_ind])
                                    interp_timestamps.append([t1-datetime.timedelta(minutes=t),interp_ind,clone_averaging,'clone'])
                                else:
                                    interp_traces.append([np.zeros(len(clone_trace)).tolist(),interp_ind])
                                    interp_timestamps.append([t1-datetime.timedelta(minutes=t),interp_ind,-1,'dummy'])
                        interp_ind=interp_ind+1
    
    data=np.transpose(interp_traces)
    interp_traces=data[0].tolist()
    interp_traces_ind=data[1].tolist() # for QA
    
    data=np.transpose(interp_timestamps)
    interp_timestamps_mt=utils.convert_to_mdate(data[0])
    interp_timestamps_ind=data[1].tolist() # for QA
    interp_averaging=data[2].tolist()
    interp_trace_type=data[3].tolist()
    
    
    dts_merged_hdf.close() # have to close hdf to use df.to_hdf
    
    # QA of interpolation, check if traces index is equal to timestamp index
    for i in xrange(len(interp_traces_ind)):
        if interp_traces_ind[i]!=interp_timestamps_ind[i]:
            print 'something wrong!!!',t
            sys.exit()
    
    # QA of interpolation, check if every delta t is 1 min
    check=sorted(interp_timestamps,key=itemgetter(0))    
    for t in xrange(1,len(check)):
        if not check[t][0]-check[t-1][0]==datetime.timedelta(minutes=1):
            print 'something wrong!!!',t
            sys.exit()
    
    # put into processed_hdf
    df=pd.DataFrame(interp_traces,index=interp_timestamps_mt)
    df=df.sort_index()
    df.to_hdf(dts_merged_path,'interp_traces',mode='r+')
    
    # put averaging and trace_type
    dts_merged_hdf = h5py.File(dts_merged_path,'r+')
    
    dts_merged_hdf.create_dataset('interp_traces/averaging',(1,),maxshape=(None,))
    dts_merged_hdf['interp_traces/averaging'].shape=((len(interp_averaging),))
    dts_merged_hdf['interp_traces/averaging'][:]=interp_averaging
    
    dts_merged_hdf.create_dataset('interp_traces/trace_type',(1,),maxshape=(None,),dtype='S100')
    dts_merged_hdf['interp_traces/trace_type'].shape=((len(interp_trace_type),))
    dts_merged_hdf['interp_traces/trace_type'][:]=interp_trace_type
    
    # take depths from orig_traces and copy to interp_traces
    depths=dts_merged_hdf['orig_traces/axis0'][:]    

    # delete axis0 and recreate to put depths    
    del dts_merged_hdf['interp_traces/axis0']
    dts_merged_hdf.create_dataset('interp_traces/axis0',(1,),maxshape=(None,))
    dts_merged_hdf['interp_traces/axis0'].shape=((len(depths),))
    dts_merged_hdf['interp_traces/axis0'][:]=depths
    
    # close hdf file
    dts_merged_hdf.close()
    
    print 'interpolation done..'


    

if __name__=="__main__":

    # INPUT ====================================
    well_name='A04'    
    dts_path=r'/mnt/A0-Data1/Data/BP/WP/A04/DTS_cal_dts/A04_cal_dts.hdf'      
    # END ======================================
    
    dts_dir,dts_file=os.path.split(dts_path)
    dts_merged_path=os.path.join(dts_dir,well_name+'_dts_interpol.hdf')
    root_gr='Data/Calibrated_DTS/DTS'

    interpolate_traces(dts_merged_path,True,True)
    
