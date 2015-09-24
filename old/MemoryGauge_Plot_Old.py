import sys
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import numpy as np
import datetime
import time
import matplotlib.ticker
import matplotlib.dates
import csv
import os
import matplotlib.dates as mdates


"""
Usage example:

	The script assumes that the header in the input file follows the pattern:

	Time                ,    BP_A16_BN (psiA),       BP_A16_BN (C)

	--

	Default usage:
	--------------
	python MemoryGauge.py /Path/US00039_Job2.csv


	Optional usage #1:
	------------------
	The start and end time/dates can be given as 3rd and 4th command line arguments:

	python MemoryGauge.py /Path/US00039_Job2.csv '02/04/2014 13:43:25' '02/04/2014 13:44:25'


	Optional usage #2:
	------------------
	The temperature and pressure y-limits given as 5th-8th command line argumens (lower_temp, upper_temp, lower_press, upper_press):

	python MemoryGauge.py /Path/US00039_Job2.csv '02/04/2014 13:43:25' '02/04/2014 13:44:25' 0 50 0 1000

"""




convertfunc = lambda x: time.strptime(x, "%Y.%m.%d %H:%M:%S")

#Handel command line args
inputFile = sys.argv[1]
if len(sys.argv) > 2:
	xlimLeft = sys.argv[2]  
	xlimRight = sys.argv[3] 
	
if len(sys.argv) > 4:
	ylimLT = float(sys.argv[4])
	ylimUT = float(sys.argv[5])
	ylimLP = float(sys.argv[6])
	ylimUP = float(sys.argv[7])
	

Time = []
Pressure = []
Temperature = []

#Load csv file
with open(inputFile, 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',')
	for idx, row in enumerate(spamreader):
		if idx == 0:
			titleInfo = ' '.join(row[1].strip().split(' ')[0].split('_'))
		if idx > 0:
			#Time.append(time.mktime(convertfunc(row[0])))
			Time.append(mdates.date2num(datetime.datetime.strptime(row[0],"%Y.%m.%d %H:%M:%S")))
			Pressure.append(float(row[1])*0.0689475729) #Multiplying by 6.89475729 to convert to kPa. Oman clients;)
			print row[0],row[2]			
			Temperature.append(float(row[2]))
			


print Time[5:100]
print Temperature[5:100]
#def dates(x, pos):
#	'The two args are the value and tick position'
#	return datetime.datetime.utcfromtimestamp(round(x)).strftime('%Y-%m-%d %H:%M:%S')	
#	#return datetime.datetime.utcfromtimestamp(round(x)).strftime('%Y-%m-%d %H:%M:%S')



	
#formatter = matplotlib.ticker.FuncFormatter(dates)

fig, ax = plt.subplots(2, sharex=True, sharey=False)

#ax[0].xaxis.set_major_formatter(formatter)
fig.autofmt_xdate(bottom=0.2, rotation=30,ha='right')

ax[1].set_xlabel('Time & Date')

#if len(sys.argv) > 2:
#	ax.set_xlim([time.mktime(convertfunc(xlimLeft)),time.mktime(convertfunc(xlimRight))])

ax[0].scatter(Time, Temperature, color='r', marker='+', label = 'Temperature')
ax[1].scatter(Time, Pressure, color='b', marker='+', label = 'Pressure')
ax[0].set_title('Temperature and pressure: A04') #(' + titleInfo +  ')')    
ax[0].set_ylabel('BHA Temperature ($^\circ$C)')
ax[1].set_ylabel('BHA Pressure (bar)')

lines, labels = ax[0].get_legend_handles_labels()
lines2, labels2 = ax[1].get_legend_handles_labels()
ax[1].legend(lines + lines2, labels + labels2, loc=0,prop={'size':10})
ax[0].grid()
ax[1].grid()

if len(sys.argv) > 4:
	ax.set_ylim([ylimLT,ylimUT])
	ax[1].set_ylim([ylimLP,ylimUP])

plt.xticks(rotation=30,ha='right')
ax[1].xaxis_date()
date_format = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
ax[1].xaxis.set_major_formatter(date_format)
	
plt.tight_layout()
plt.savefig(os.path.splitext(sys.argv[1])[0] + ".png",dpi=fig.dpi)
plt.show()
