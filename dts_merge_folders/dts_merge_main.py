

###############################################################################
# INPUT HEADER ################################################################

well_name='A14'

# if using Windows put 'r' in front of directory path, example: r'W:\Data\CoP\A-02\DTS'
#dts_path=r'/mnt/A1-Data1/Data/BP/A14/Vintage-DTS-DAS-Case-Study-from-the-North-Sea/DTS/2014/A14_cal_dts_hdf.hdf'
dts_path=r'/mnt/A4-Data1/Data/Daleel/Case_Study_Oman/BR_13/Poster_Case-Study_BR13_DALEEL/DTS/Calibrated/BR-13_cal_dts/BR-13_cal_dts_hdf.hdf'


# END OF INPUT HEADER #########################################################
###############################################################################




import dts_import_hdf
import dts_interpolation
import dts_utils
import dts_ziebel_format
import os


def data_processing():
        
    dts_import_hdf.create_merged_hdf(dts_merged_path)
    
    dts_import_hdf.import_hdf_data(dts_path,root_gr,dts_merged_path) 

    dts_utils.define_averaging(dts_merged_path)

    dts_utils.round_time_to_mins(dts_merged_path)
    
    # interpolate_traces(dts_processed_hdf_path, interpolate_all=True, interpolate_btw=True)
    # interpolate_all=True -> interpolate anything between all traces
    # interpolate_btw=True -> interpolate locally between only given two traces, if False -> clones traces
    # recommended -> False, False
    # set maximum time delta between traces where you mask gaps by closing, recommended max_delta=5
    # max_delta=5 means if there is gap of less than 5 mins then mask the gap with latest actual trace
    dts_interpolation.interpolate_traces(dts_merged_path,False,False,max_delta=5) 
    
    dts_ziebel_format.convert_to_ziebel_format(dts_merged_path,dts_ziebel_merged_path)


if __name__=="__main__":
    
    dts_dir,dts_file=os.path.split(dts_path)
    dts_merged_path=os.path.join(dts_dir,well_name+'_dts_merge_log.hdf')
    dts_ziebel_merged_path=os.path.join(dts_dir,well_name+'_dts_merged.hdf')
    root_gr='Data/Calibrated_DTS/DTS'

    data_processing()
    
    
    

    

