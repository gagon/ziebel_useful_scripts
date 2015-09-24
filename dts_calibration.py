# -*- coding: utf-8 -*-
"""
Created on Mon Jun 08 13:33:56 2015

@author: bolatzh
"""

import os
import re
import datetime
import numpy as np
import matplotlib.pyplot as plt
import sys
import matplotlib.dates as mdates
import gc
import matplotlib.gridspec as gridspec
import getpass
import h5py
from matplotlib import cm



# CONSTANT PARAMETERS
tref=["T internal ref","T ext. ref 1","T ext. ref 2"]
TRACES_DELTA_TIME_GAP_MAX=3600.0 # in seconds, maximum time gap size to continue calibration, if more then stop and split traces into folders 
TRACES_DELTA_TIME_GAP_TOL=10.0 # in seconds, tolerance for difference between delta_time and delta_time_reference to pass as no gaps

def ruler():
    print "---------------------------------------------------"

def parse_ddfs(src_folder,test):
    ddfdata=[]
    temp_ref1=[]
    temp_ref2=[]
    temp_ref3=[]
       
    cnt=0
    for root, dirs, files in os.walk(src_folder):
        for f in files:
            if f.endswith(".ddf"):
                cnt+=1
    cur_cnt=0
    for root, dirs, files in os.walk(src_folder):        
        for f in files:            
            if f.endswith(".ddf"):                
                if not test:
                    cur_cnt+=1
                    print "reading.. %s out of %s traces \r" % (cur_cnt,cnt),       
                head, ext = os.path.splitext(f)
                ddf_file=os.path.join(root, f)                                   
                file=open(ddf_file,"r")                                                                        
                trace_datetime=[]
                trace_depth=[]
                trace_temperature=[]                
                for idx,line in enumerate(file):                    
                    text=re.split("\t|\r|\n",line) 
                    if idx==0:                    
                        for idx,t in enumerate(text):                            
                            if t=="date":  
                                trace_datetime=datetime.datetime.strptime(text[idx+1]+" "+text[idx+3], "%Y/%m/%d %H:%M:%S")   
                            if tref[0] in t:
                                temp_ref1.append([trace_datetime,float(text[idx+1])])
                            if tref[1] in t:
                                temp_ref2.append([trace_datetime,float(text[idx+1])])
                            if tref[2] in t:
                                temp_ref3.append([trace_datetime,float(text[idx+1])])
                    else:
                        if test: 
                            break
                        else:
                            trace_depth.append(float(text[0]))
                            trace_temperature.append(float(text[1]))                
                ddfdata.append([trace_datetime,trace_depth,trace_temperature,ddf_file]) # ddf_file is only for test                

    ddfdata=sorted(ddfdata,key=lambda x: x[0])      
    temp_ref1=sorted(temp_ref1,key=lambda x: x[0])      
    temp_ref2=sorted(temp_ref2,key=lambda x: x[0])          
    temp_ref3=sorted(temp_ref3,key=lambda x: x[0])      
    
    if test:
        init_trace_file=ddfdata[0][3]
        file=open(init_trace_file,"r")                                                                        
        trace_depth=[]
        trace_temperature=[]                
        for idx,line in enumerate(file):
            text=re.split("\t|\r|\n",line)
            if idx>0:
                trace_depth.append(float(text[0]))
                trace_temperature.append(float(text[1]))
        ddfdata=[[ddfdata[0][0],trace_depth,trace_temperature,init_trace_file]]  # [[]] is stupid work around for test to use it further for depth calib           
    else:
        ddfdata=fill_gaps(ddfdata)     # fill gaps between traces with dummy traces

        
    return ddfdata,[temp_ref1,temp_ref2,temp_ref3]


def parse_mem_gauge(memory_gauge_file):
    ruler()
    print "fetching memory gauge data.."
    mem=open(memory_gauge_file,"r")
    mem_dt=[]    
    mem_temp=[]    
    for ind,line in enumerate(mem):
        if ind>20:
            d=line.split("\t")
            if len(d)>=4 and ":" in d[0]:
                mem_dt.append(mdates.date2num(datetime.datetime.strptime(d[0], "%Y.%m.%d %H:%M:%S")))
                mem_temp.append(float(d[3].replace(",",".")))            
    return [mem_dt,mem_temp]



def fill_gaps(data):
    ruler()
    print "filling in gaps in time between traces with dummy traces.."    
    new_data=[]
    for idx,ddftrace in enumerate(data):  
        if idx==0:
            new_data.append(ddftrace)
            # assuming first two traces are representative averaging   
            delta_time_ref=(data[1][0]-data[0][0]).total_seconds()          
        else:
            delta_time=(data[idx][0]-data[idx-1][0]).total_seconds()
            if delta_time>TRACES_DELTA_TIME_GAP_MAX:
                print "====="
                print "there is a big time gap between traces %s and %s" % (data[idx-1][0],data[idx][0])
                print "calibration stopped"
                sys.exit()
            if abs(delta_time-delta_time_ref)<=TRACES_DELTA_TIME_GAP_TOL:
                new_data.append(ddftrace)
            else:
                # number of dummy traces to put between traces
                dummy_trace_count=int(abs(delta_time-delta_time_ref)/delta_time_ref)+1                 
                for t in range(dummy_trace_count):
                    if t==0:
                        new_data.append(ddftrace)                        
                    else:
                        new_data.append([ddftrace[0]-datetime.timedelta(minutes=t*delta_time_ref/60.0), \
                                                            ddftrace[1],(np.zeros(len(ddftrace[2]))).tolist()])
    new_data=sorted(new_data,key=lambda x: x[0])   
    return new_data

   
    
def temp_calibration(data,mem_data,method):    
    ruler()
    print "temperature calibrating with method %s.." % method
    new_data=[]
    for idx,trace in enumerate(data):
        if not all(np.array(trace[2])==0): # if not dummy trace                
            if method==2:
                mem_temp=np.interp(mdates.date2num(trace[0]),mem_data[0],mem_data[1])
                dts_temp=np.mean(trace[2][average_zone_min_idx:average_zone_max_idx])
                coil1_temp=np.mean(trace[2][coil1_zone_min_idx:coil1_zone_max_idx])                
                coil1_zone_midpoint=(coil1_zone_min+coil1_zone_max)/2.0
                average_zone_midpoint=(average_zone_min+average_zone_max)/2.0
                grad1=(dts_temp-coil1_temp)/(average_zone_midpoint-coil1_zone_midpoint)
                grad2=(mem_temp-coil1_temp)/((average_zone_min+average_zone_max)/2.0-(coil1_zone_min+coil1_zone_max)/2.0)
                
                new_trace=[]
                for idx,t in enumerate(trace[2]):
                    if idx==0:
                        new_trace.append(t)
                    else:
                        new_trace.append(t+(trace[1][idx]-coil1_zone_midpoint)*(grad2-grad1))                    
                new_data.append([trace[0],trace[1],new_trace])
                
            elif method==1:                
                mem_temp=np.interp(mdates.date2num(trace[0]),mem_data[0],mem_data[1])
                dts_temp=np.mean(trace[2][average_zone_min_idx:average_zone_max_idx])
                delta_temperature=dts_temp-mem_temp
                new_data.append([trace[0],trace[1],(np.array(trace[2])-delta_temperature).tolist()])
            
            elif method==0:
                new_data=data
                break
                
        else:
            new_data.append(trace)
                
    new_data=sorted(new_data,key=lambda x: x[0])
    print "finished temperature calibrating.."
    return new_data


def depth_calibration(data):
    ruler()
    print "depth calibrating.."        
    bottom_cut=fiber_length
    top_cut=fiber_length-(HM1-HM2+ref_to_zero_distance/overstuff)
    bottom_cut_idx=(np.abs(np.array(data[0][1])-bottom_cut)).argmin()
    top_cut_idx=(np.abs(np.array(data[0][1])-top_cut)).argmin()
    
    new_data=[]
    for idx,trace in enumerate(data):        
        # top_cut, bottom_cut, zero depths from top and apply overstuff
        depths=(np.array(trace[1][top_cut_idx:bottom_cut_idx])-top_cut)*overstuff 
        # add to new data list
        new_data.append([trace[0],depths,trace[2][top_cut_idx:bottom_cut_idx]])
    
    print "finished depth calibrating.."    
    return new_data



def pre_temp_cal_qc_plot(data,mem_data,temp_refs):
    ruler()
    print "plotting pre temperature calibration QC plots.."
        
    # uncalibrated traces    
    fig, ax = plt.subplots(figsize=(10,6))
    if len(data)>50:
        slicing=len(data)/5
    else:
        slicing=1
    for trace in data[::slicing]:
        if not all(np.array(trace[2])==0):
            ax.plot(trace[2],trace[1])
    ax.set_title("Raw DTS traces - symmetry")
    ax.set_ylabel("Fiber length (m)")
    ax.set_xlabel("Temperature (degC)")
#    ax.grid(True)
    ax.invert_yaxis()
    plt.show()
    ax.set_xlim(ax.get_xlim())
    ax.set_ylim(ax.get_ylim())    
    fig.savefig(os.path.join(output_folder,"uncalibrated.png"))
    fig.clf()
    plt.close()
    gc.collect()

    # all_traces showing avering overview    
    fig, ax = plt.subplots(figsize=(6,1))
    for trace in data:
        if not all(np.array(trace[2])==0):
            ax.plot([trace[0],trace[0]],[0,1],"g")
    plt.xticks(rotation=30,ha="right")   
    ax.set_title("DTS traces averaging")
    ax.xaxis_date()
    date_format = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")
    ax.xaxis.set_major_formatter(date_format)
    ax.axes.get_yaxis().set_visible(False)
    ax.set_xlim((ax.get_xlim()[0]*(1.0-1e-10),ax.get_xlim()[1]*(1.0+1e-10))) # stupid work around for showing all traces (plot issue not showing first and last traces)
    fig.savefig(os.path.join(output_folder,"all_traces.png"),bbox_inches="tight")
    fig.clf()
    plt.close()
    gc.collect()
    
    # reference box temperatures QC plot   
    gs=gridspec.GridSpec(10,2)
    fig = plt.figure(figsize=(18, 8))
    ax1 = plt.subplot(gs[0:5,0])
    ax2 = plt.subplot(gs[0:5,1],sharey=ax1)
    ax3 = plt.subplot(gs[6:,:])
    if len(data)>50:
        slicing=len(data)/50
    else:
        slicing=1
    colors=list(iter(cm.jet(np.linspace(0,1,len(data[::slicing])))))
    for i,trace in enumerate(data[::slicing]):
        if not all(np.array(trace[2])==0):
            ax1.plot(trace[1][coil1_zone_min_idx-10:coil1_zone_max_idx+10], \
                    trace[2][coil1_zone_min_idx-10:coil1_zone_max_idx+10], \
                    color=colors[i]) # adding 10 more points to the sides
            ax2.plot(trace[1][coil2_zone_min_idx-10:coil2_zone_max_idx+10], \
                    trace[2][coil2_zone_min_idx-10:coil2_zone_max_idx+10], \
                    color=colors[i]) # adding 10 more points to the sides
    ax3.plot(np.array(temp_refs[0]).T[0],np.array(temp_refs[0]).T[1],label=tref[0])
    ax3.plot(np.array(temp_refs[1]).T[0],np.array(temp_refs[1]).T[1],label=tref[1])
    ax3.plot(np.array(temp_refs[2]).T[0],np.array(temp_refs[2]).T[1],label=tref[2])    
    ax3.legend()
    plt.xticks(rotation=30,ha="right")
    ax1.set_title("Coil 1")
    ax2.set_title("Coil 2")
    ax3.set_title("Temperature references")
    ax1.set_ylabel("Temperature degC")    
    ax2.set_ylabel("Temperature degC")
    ax3.set_ylabel("Temperature degC")    
    ax1.set_xlabel("Fiber length, m")  
    ax2.set_xlabel("Fiber length, m")     
    ax3.xaxis_date()
    date_format = mdates.DateFormatter("%b.%d %H:%M")
    ax3.xaxis.set_major_formatter(date_format)   
#    ax1.grid(True)
#    ax2.grid(True)
#    ax3.grid(True)
    plt.show()
    ax1.set_xlim(ax1.get_xlim())
    ax1.set_ylim(ax1.get_ylim()) 
    ax2.set_xlim(ax2.get_xlim())
    ax2.set_ylim(ax2.get_ylim())
    ax3.set_xlim(ax3.get_xlim())
    ax3.set_ylim(ax3.get_ylim())    
    fig.savefig(os.path.join(output_folder,"temperature_ref_QC.png"),bbox_inches="tight")
    fig.clf()
    plt.close()
    gc.collect()


    # plot averaging zone near splice
    if calibration_method==1 or calibration_method==2:           
        fig, ax = plt.subplots(figsize=(10,6))        
        ax.plot(data[0][1][average_zone_min_idx-10:average_zone_max_idx+10],data[0][2][average_zone_min_idx-10:average_zone_max_idx+10],"bo")
        ax.plot(data[0][1][average_zone_min_idx:average_zone_max_idx],data[0][2][average_zone_min_idx:average_zone_max_idx],"ro")
        ax.set_title("Averaging zone near the splice")
        ax.set_xlabel("Fiber length (m)")
        ax.set_ylabel("Temperature (degC)")   
#        ax.grid(True)             
        plt.show()
        ax.set_xlim(ax.get_xlim())
        ax.set_ylim(ax.get_ylim())    
        fig.savefig(os.path.join(output_folder,"averaging_zone.png"))
        fig.clf()
        plt.close()
        gc.collect()



def post_temp_cal_qc_plot(data,data_temp_cal,mem_data,temp_refs):
    ruler()
    print "plotting post temperature calibration QC plots.."
    # memory gauge vs DTS bullnose temperature
    if memory_gauge_file!="":
        calibrated_dts=[]
        uncalibrated_dts=[]
        for idx,trace in enumerate(data_temp_cal):
            if not all(np.array(trace[2])==0):
                calibrated_dts.append([mdates.date2num(data_temp_cal[idx][0]),np.mean(data_temp_cal[idx][2][average_zone_min_idx:average_zone_max_idx])])
                uncalibrated_dts.append([mdates.date2num(data[idx][0]),np.mean(data[idx][2][average_zone_min_idx:average_zone_max_idx])])
        fig = plt.figure(figsize=(18, 8))
        ax = plt.subplot()  
        ax.plot(mem_data[0],mem_data[1],label="Memory gauge temp")         
        ax.plot(np.array(calibrated_dts).T[0],np.array(calibrated_dts).T[1],".",label="calibrated DTS")
        ax.plot(np.array(uncalibrated_dts).T[0],np.array(uncalibrated_dts).T[1],".",label="uncalibrated DTS") 
        ax.legend()
        plt.xticks(rotation=30,ha="right")    
        ax.set_title("Memory gauge vs calibrated vs uncalibrated DTS temperature at bullnose")
        ax.set_ylabel("Temperature degC")        
        ax.xaxis_date()
        date_format = mdates.DateFormatter("%b.%d %H:%M")
        ax.xaxis.set_major_formatter(date_format)  
        ax.grid(True)
        plt.show()    
        ax.set_xlim(ax.get_xlim())
        ax.set_ylim(ax.get_ylim())    
        fig.savefig(os.path.join(output_folder,"DTS_vs_memory_gauge_temperature.png"),bbox_inches="tight")
        fig.clf()
        plt.close()
        gc.collect()
    
    # full lenght calibrated vs uncalibrated DTS traces, the very first trace in the dataset
    if memory_gauge_file!="":
        mem_temp=np.interp(mdates.date2num(data[0][0]),mem_data[0],mem_data[1])
        coil1_temp=np.mean(data[0][2][coil1_zone_min_idx:coil1_zone_max_idx])
        bottom_cut_idx=(np.abs(np.array(data[0][1])-fiber_length)).argmin()
        fig, ax = plt.subplots(figsize=(10,6))
        ax.plot(data_temp_cal[0][2][:bottom_cut_idx],data_temp_cal[0][1][:bottom_cut_idx],label="calibrated DTS")
        ax.plot(data[0][2][:bottom_cut_idx],data[0][1][:bottom_cut_idx],label="uncalibrated DTS") 
        ax.plot(np.array(data_temp_cal[0][2][:bottom_cut_idx])-np.array(data[0][2][:bottom_cut_idx]), \
                    data[0][1][:bottom_cut_idx],label="Temp diff applied") 
        ax.plot([mem_temp,mem_temp],[data[0][1][:bottom_cut_idx][0],data[0][1][:bottom_cut_idx][-1]],label="Memory gauge temp") 
        ax.plot([coil1_temp,coil1_temp],[data[0][1][:bottom_cut_idx][0],data[0][1][:bottom_cut_idx][-1]],label="Reference box temp")     
        ax.legend()
        ax.set_title("Temperature calibrated vs uncalibrated DTS traces")
        ax.set_ylabel("Fiber length (m)")
        ax.set_xlabel("Temperature (degC)")
        ax.invert_yaxis()
    #    ax.grid(True)
        plt.show()
        ax.set_xlim(ax.get_xlim())
        ax.set_ylim(ax.get_ylim())    
        fig.savefig(os.path.join(output_folder,"cal_vs_uncal_DTS_traces.png"))
        fig.clf()
        plt.close()
        gc.collect()



def test_depth_match():
    ruler()
    print "testing depth match.."    
    # fetch first trace and depth calibrate it
    data,temp_refs=parse_ddfs(raw_dts_folder,test=True)
    data_depth_cal=depth_calibration(data)
    # plot it to see
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(data_depth_cal[0][2],data_depth_cal[0][1])
    ax.set_title("Depth calibration test - see if depth match is good")
    ax.set_ylabel("Depth MD (m)")
    ax.set_xlabel("Temperature (degC)")
    ax.grid(True)
    ax.invert_yaxis()
    plt.show()
    fig.clf()
    plt.close()
    gc.collect() 
    # based on depth calibration, decide to continue or not
    continue_calibration=raw_input("Are you happy with depth match? (yes/no): ")
    if continue_calibration=="yes":
        return True
    else:
        return False
        

def export_data(data):
    ruler()    
    print "exporting data.."

    ruler()
    print "saving calibration parameters.."
    save_cal_parameters()

    ruler()    
    print "exporting to .dts"
    write_to_dot_dts(data)
    
    ruler()
    print "exporting to hdf"
    write_to_hdf(data)
    
    
    
def write_to_dot_dts(data):
    os.mkdir(os.path.join(output_folder,"calibrated_dts_files"))
    folder=os.path.join(output_folder,"calibrated_dts_files") 
    cur_cnt=0
    for trace in data:        
        cur_cnt+=1
        print "writing %s out of %s traces to .dts \r" % (cur_cnt,len(data)),
        if all(np.array(trace[2])==0):                                
            textfile=open(os.path.join(folder,datetime.datetime.strftime(trace[0],"%Y.%m.%d.%H.%M.%S")+"_dummy.dts"),"w")
        else:
            textfile=open(os.path.join(folder,datetime.datetime.strftime(trace[0],"%Y.%m.%d.%H.%M.%S")+".dts"),"w")            
        textfile.write("~Version Information \n")
        textfile.write("VERS.                      2.0: CWLS Log ASCII Standard - VERSION 2.0 \n")
        textfile.write("WRAP.                      NO: One line per depth step \n")
        textfile.write("~Well Information Block \n")
        textfile.write("STRT.m  %.4f \n" % trace[1][0])
        textfile.write("STOP.m  %.4f \n" % trace[1][-1])
        textfile.write("STEP.m  %.4f \n" % abs(trace[1][1]-trace[1][0]))
        textfile.write("NULL.           -999.2500: \n")
        textfile.write("TIMESTAMP: %s \n" % datetime.datetime.strftime(trace[0],"%Y/%m/%d %H:%M:%S"))
        textfile.write("~Curve Information Block \n")
        textfile.write("DEPTH.m \n")
        textfile.write("TEMP_DTS.degC \n")
        textfile.write("~A \n")        
        trace_T=np.array([trace[1],trace[2]]).T
        for line in trace_T:
            line=["%.4f" % line[0],"%.4f" % line[1]]
            textfile.write("%s\n" % "\t".join(line))
    return None
        
        

def write_to_hdf(data):    
    traces=[]
    dt=[]    
    cur_cnt=0
    for item in data:
        cur_cnt+=1
        print "preparing %s out of %s traces to hdf \r" % (cur_cnt,len(data)),
        dt.append(datetime.datetime.strftime(item[0],"%Y/%m/%d %H:%M:%S"))
        traces.append(np.array([item[1],item[2]]).T)    
    print "loading to %s.." % os.path.join(output_folder,"%s_cal_dts.hdf" % well_name)
    copy_hdf=h5py.File(os.path.join(output_folder,"%s_cal_dts.hdf" % well_name), "w")    
    # Replicating pandas hdf format, needs to be like that to plot using mergeplot scripts
    copy_hdf.create_group("/Data/Calibrated_DTS/DTS/Alldata")    
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["CLASS"]="GROUP"
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["TITLE"]="GROUP"
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["VERSION"]="1.0"
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["axis0_variety"]="regular"
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["axis1_variety"]="regular"
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["axis2_variety"]="regular"
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["block0_items_variety"]="regular"
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["encoding"]="N."
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["nblocks"]="1"
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["ndim"]="3"
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["pandas_type"]="wide"
    copy_hdf["/Data/Calibrated_DTS/DTS/Alldata"].attrs["pandas_version"]="0.10.1"    
    copy_hdf.create_dataset("/Data/Calibrated_DTS/DTS/Alldata/block0_values",data=traces)
    copy_hdf.create_dataset("/Data/Calibrated_DTS/DTS/Alldata/axis2",data=dt)
    copy_hdf.create_dataset("/Data/Calibrated_DTS/DTS/Alldata/axis0",data=dt)
    copy_hdf.create_dataset("/Data/Calibrated_DTS/DTS/Alldata/axis1",data=dt)
    copy_hdf.create_dataset("/Data/Calibrated_DTS/DTS/Alldata/block0_items",data=dt)
    copy_hdf.close()
    return None


def parse_input_file(input_file):
    ruler()    
    print "parsing input file.." 
    with open(input_file) as f:
        lines=f.readlines()    
    
    input_parameters={}
    with open(input_file) as f:
        for idx,line in enumerate(f):
            if "--" in line:
                input_parameters[line.replace("\n","").replace("--","").replace("\t","").replace("\r","").replace(" ","")]= \
                                    lines[idx+1].replace("\n","").replace("--","").replace("\t","").replace("\r","").replace(" ","")    
    return input_parameters


def save_cal_parameters():
    textfile=open(os.path.join(output_folder,"calibr_parameters.txt"),"w")    
    textfile.write("Calibration date: %s\n" % str(datetime.datetime.now()))    
    textfile.write("Calibrated by: %s\n" % getpass.getuser())
    textfile.write("Well: %s\n" % well_name)    
    textfile.write("Length of fiber (Loss at splice): %s (m)\n" % str(fiber_length))        
    textfile.write("Heat mark (HM1) with BHA at Zref Point: %s (m)\n" % str(HM1))        
    textfile.write("Heat mark (HM2) when BHA at HUD: %s (m)\n" % str(HM2))            
    textfile.write("Overstuff: %s\n" % str(overstuff))
    textfile.write("Minimum averaging depth (index): %s (m) (%s)\n" % (str(average_zone_min),str(average_zone_min_idx)))
    textfile.write("Maximum averaging depth (index): %s (m) (%s)\n" % (str(average_zone_max),str(average_zone_max_idx)))
    textfile.write("DTS raw folder: %s\n" % raw_dts_folder)
    textfile.write("Memory gauge file: %s\n" % memory_gauge_file)
    


def define_regions(data):
    ruler()
    print "defining regions for references.."
    fig, ax = plt.subplots(figsize=(10,6))    
    ax.plot(data[0][1],data[0][2])  
    ax.set_ylabel("Temperature (degC)")              
    ax.set_xlabel("Fiber length (m)")
    ax.set_title("Define averging, coil1 and coil2 zones, close figure and enter values")
    plt.show()       
    coil1_zone_min=float(raw_input("Coil1 zone, trace depth min (in meters): ")) # depth
    coil1_zone_max=float(raw_input("Coil1 zone, trace depth max (in meters): ")) # depth
    coil2_zone_min=float(raw_input("Coil2 zone, trace depth min (in meters): ")) # depth
    coil2_zone_max=float(raw_input("Coil2 zone, trace depth max (in meters): ")) # depth                                              
    coil1_zone_min_idx=(np.abs(np.array(data[0][1])-coil1_zone_min)).argmin() # index
    coil1_zone_max_idx=(np.abs(np.array(data[0][1])-coil1_zone_max)).argmin() # index                
    coil2_zone_min_idx=(np.abs(np.array(data[0][1])-coil2_zone_min)).argmin() # index
    coil2_zone_max_idx=(np.abs(np.array(data[0][1])-coil2_zone_max)).argmin() # index     
    if memory_gauge_file!="":        
        average_zone_min=float(raw_input("Averaging zone (left side of splice), trace depth min (in meters): ")) # depth
        average_zone_max=float(raw_input("Averaging zone (left side of splice), trace depth max (in meters): ")) # depth
        average_zone_min_idx=(np.abs(np.array(data[0][1])-average_zone_min)).argmin() # index
        average_zone_max_idx=(np.abs(np.array(data[0][1])-average_zone_max)).argmin() # index
    else:
        average_zone_min=0
        average_zone_max=0
        average_zone_min_idx=0
        average_zone_max_idx=0
#        print average_zone_min, \
#		average_zone_max, \
#		coil1_zone_min, \
#		coil1_zone_max, \
#		coil2_zone_min, \
#		coil2_zone_max, \
#		average_zone_min_idx, \
#		average_zone_max_idx, \
#		coil1_zone_min_idx, \
#		coil1_zone_max_idx, \
#		coil2_zone_min_idx, \
#		coil2_zone_max_idx
    return average_zone_min, \
    average_zone_max, \
    coil1_zone_min, \
    coil1_zone_max, \
    coil2_zone_min, \
    coil2_zone_max, \
    average_zone_min_idx, \
    average_zone_max_idx, \
    coil1_zone_min_idx, \
    coil1_zone_max_idx, \
    coil2_zone_min_idx, \
    coil2_zone_max_idx
  



if __name__=="__main__":
    
    input_file=os.path.abspath(raw_input("Input file fullpath: "))

    # input file parsing and getting calibration parameters   
    input_parameters=parse_input_file(input_file)
    well_name=input_parameters["well_name"]
    raw_dts_folder=         os.path.abspath(input_parameters["raw_dts_folder"])
    output_folder=          os.path.abspath(input_parameters["output_folder"])
    if input_parameters["memory_gauge_file"]=="":
        memory_gauge_file=""
    else:
        memory_gauge_file=      os.path.abspath(input_parameters["memory_gauge_file"])
    calibration_method=     int(input_parameters["calibration_method"])
    fiber_length=           float(input_parameters["fiber_length"])
    HM1=                    float(input_parameters["HM1"])
    HM2=                    float(input_parameters["HM2"])
    ref_to_zero_distance=   float(input_parameters["ref_to_zero_distance"])
    overstuff=              float(input_parameters["overstuff"])
    
    # test the depth match if it"s good or not, if not stop and revisit calibration
    continue_calibration=test_depth_match()
    if not continue_calibration:
        print "Revisit depth calibration parameters!!!"
        sys.exit()
    
    # fetch all data    
    if memory_gauge_file!="":
        mem_data=parse_mem_gauge(memory_gauge_file)                     # parses memory gauge temperature    
    else:
        mem_data=[]
        
    data,temp_refs=parse_ddfs(raw_dts_folder,test=False)            # parses ddfs and temp_refs, fills in time gaps 
    
    
    # define regions for references
    average_zone_min, \
    average_zone_max, \
    coil1_zone_min, \
    coil1_zone_max, \
    coil2_zone_min, \
    coil2_zone_max, \
    average_zone_min_idx, \
    average_zone_max_idx, \
    coil1_zone_min_idx, \
    coil1_zone_max_idx, \
    coil2_zone_min_idx, \
    coil2_zone_max_idx=define_regions(data)    
    
    # plotting for QC
    pre_temp_cal_qc_plot(data,mem_data,temp_refs)        

    # temperature calibration        
    data_temp_cal=temp_calibration(data,mem_data,calibration_method)   
    
    # plotting for QC
    post_temp_cal_qc_plot(data,data_temp_cal,mem_data,temp_refs)
    
    # no need for data and mem_data lists (saving memory space)
    del data
    del mem_data
    gc.collect()    
    
    # depth calibration
    data_temp_depth_cal=depth_calibration(data_temp_cal)
    
    # no need for data_temp_cal (saving memory space)  
    del data_temp_cal
    gc.collect()
    
    export_data(data_temp_depth_cal)
    
    ruler()
    print "Good job!!! You did it!!!"
