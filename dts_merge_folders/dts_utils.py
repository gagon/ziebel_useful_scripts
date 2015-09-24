
import datetime
import numpy as np
import h5py
import matplotlib
import os
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter



def convert_from_mdate(timestamps_mt):
    timestamps_dt=[]    
    for t in timestamps_mt:
        timestamps_dt.append(matplotlib.dates.num2date(t).replace(tzinfo=None))
    return timestamps_dt

def convert_to_mdate(timestamps_dt):
    timestamps_mt=[]    
    for t in timestamps_dt:
        timestamps_mt.append(matplotlib.dates.date2num(t))
    return timestamps_mt


def define_averaging(dts_merged_path):
    print 'defining averaging of traces..'    

    dts_merged_dir,dts_merged_file=os.path.split(dts_merged_path)
    head, ext = os.path.splitext(dts_merged_file)    
    
    # get datetimes from hdf
    dts_merged_hdf = h5py.File(dts_merged_path,'r+')
    timestamps_mt=dts_merged_hdf['orig_traces/axis1'][:]  
    
    # convert to python datetime
    timestamps_dt=convert_from_mdate(timestamps_mt)

    # get delta time between timestamps
    dt=[]
    for i in range(1,len(timestamps_dt)):
        dt.append((timestamps_dt[i]-timestamps_dt[i-1]).total_seconds())
    
    # define averaging from delta time
    av=[]
    for i in range(len(timestamps_dt)-1): # 1,5,10,30 min averaging only (+/- 10s range)
        if dt[i]>50 and dt[i]<70:
            av.append(1)
        elif dt[i]>290 and dt[i]<310:
            av.append(5)
        elif dt[i]>590 and dt[i]<610:
            av.append(10)
        elif dt[i]>1790 and dt[i]<1810:
            av.append(30)
        else:
            # check previous delta time for proper averaging (third condition to avoid dt[-1] in case i=0)
            if dt[i-1]>50 and dt[i-1]<70 and i-1>-1:
                av.append(1)
            elif dt[i-1]>290 and dt[i-1]<310 and i-1>-1:
                av.append(5)
            elif dt[i-1]>590 and dt[i-1]<610 and i-1>-1:
                av.append(10)
            elif dt[i-1]>1790 and dt[i-1]<1810 and i-1>-1:
                av.append(30)
            else:
                av.append(-1)
    av.append(av[-1]) # make last timestamp averaging same as previous
    
    # create dataset and put datetimes
    dts_merged_hdf.create_dataset('orig_traces/averaging',(1,),maxshape=(None,))
    dts_merged_hdf['orig_traces/averaging'].shape=((len(av),))
    dts_merged_hdf['orig_traces/averaging'][:]=av
    
    # plot averaging over time / testing
#    fig, ax = plt.subplots()
#    ax.plot(timestamps_dt,av)
#    ax.set_ylim([-2,6])
#    ax.xaxis.set_major_formatter( DateFormatter('%d.%m %H:%M') )
#    ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
#    fig.autofmt_xdate()
#    plt.savefig(os.path.join(dts_merged_dir,head+'.png'))    

    dts_merged_hdf.close()


def round_time_to_mins(dts_merged_path,roundTo=60):
    print 'rounding time to minutes..'
    
    # get datetimes from hdf
    dts_merged_hdf = h5py.File(dts_merged_path,'r+')
    timestamps_mt=dts_merged_hdf['orig_traces/axis1'][:] 
    
    # convert to python datetime
    timestamps_dt=convert_from_mdate(timestamps_mt)

    # make rounding
    new_timestamps_dt=[]
    for time in timestamps_dt:
        seconds = (time - time.min).seconds
        rounding = (seconds+roundTo/2) // roundTo * roundTo
        newdt=time + datetime.timedelta(0,rounding-seconds,-time.microsecond)
        new_timestamps_dt.append(newdt)
    
    # convert to matplotlib datetime
    new_timestamps_mt=convert_to_mdate(new_timestamps_dt)
    
    # create dataset and put datetimes
    dts_merged_hdf.create_dataset('orig_traces/axis1_rounded',(1,),maxshape=(None,),dtype=np.float64)
    dts_merged_hdf['orig_traces/axis1_rounded'].shape=((len(new_timestamps_mt),))
    dts_merged_hdf['orig_traces/axis1_rounded'][...]=new_timestamps_mt

    dts_merged_hdf.flush()
    dts_merged_hdf.close()
    


if __name__=="__main__":

    # INPUT ====================================
    well_name='A02'    
    dts_path=r'W:\Data\CoP\A-02\DTS\DTS_Calibrated\Integrity\A02_cal_dts_hdf_copy.hdf'      
    # END ======================================
    
    dts_dir,dts_file=os.path.split(dts_path)
    dts_merged_path=os.path.join(dts_dir,well_name+'_dts_merged.hdf')
    root_gr='Data/Calibrated_DTS/DTS'
         
    define_averaging(dts_merged_path)
    round_time_to_mins(dts_merged_path)

