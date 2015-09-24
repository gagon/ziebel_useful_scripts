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



""" =========================================================== """
""" ========================= INPUT HEADER ==================== """

well='G-21'

merged_file=r'O:\Data\BP\G-21_2015\ASEP\G21_merged_tvd.txt'

plot_depth_unit='meter'
plot_pressure_unit='psi'
plot_temperature_unit='celsius'


""" =========================================================== """
""" ================== DO NOT EDIT CODE BELOW ================= """




convertfunc = lambda x: time.strptime(x, "%d/%m/%Y %H:%M:%S")

#Handel command line args
#inputFile = sys.argv[1]
#if len(sys.argv) > 2:
#	xlimLeft = sys.argv[2]  
#	xlimRight = sys.argv[3] 
#	
#if len(sys.argv) > 4:
#	ylimLT = float(sys.argv[4])
#	ylimUT = float(sys.argv[5])
#	ylimLP = float(sys.argv[6])
#	ylimUP = float(sys.argv[7])
	

Time = []
Depth = []
Pressure = []
Temperature = []

#Load csv file
with open(merged_file, 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',')
	for idx, row in enumerate(spamreader):
		if idx == 0:
			titleInfo = ' '.join(row[1].strip().split(' ')[0].split('_'))
		if idx > 0:
			Time.append(time.mktime(convertfunc(row[0])))
			Depth.append(float(row[2])) 
			Temperature.append(float(row[3]))
			Pressure.append(float(row[4])) 

if plot_depth_unit=='ft':
	Depth=np.array(Depth)*3.2808
if plot_pressure_unit=='bar':
	Pressure=np.array(Pressure)*0.0689475729
elif plot_depth_unit=='kpa':
	Pressure=np.array(Pressure)*6.89475729
if plot_temperature_unit=='fahrenheit':
	Temperature=np.array(Temperature)*9/5+32
			
print Time[5:100]

def dates(x, pos):
	'The two args are the value and tick position'
	return datetime.datetime.utcfromtimestamp(round(x)).strftime('%Y-%m-%d %H:%M:%S')	


fig, ax = plt.subplots(1, 2, sharey=True)


chop_off = np.divide(len(Depth), 2)
chop_off = 65000 #specific depth 

if len(sys.argv) > 2:
	ax.set_xlim([time.mktime(convertfunc(xlimLeft)),time.mktime(convertfunc(xlimRight))])


	
ax[0].scatter(Temperature[chop_off:], Depth[chop_off:], color='b', marker='+', label = 'Temperature POOH')
ax[1].scatter(Pressure[chop_off:], Depth[chop_off:], color='b', marker='+', label = 'Pressure POOH')

ax[1].scatter(Pressure[:chop_off], Depth[:chop_off], color='r', marker='+', label = 'Pressure RIH')
ax[0].scatter(Temperature[:chop_off], Depth[:chop_off], color='r', marker='+', label = 'Temperature RIH')

ax[0].set_title('Temperature and pressure: Well %s' % well) 
ax[0].set_ylabel('Depth %s TVDKB' % plot_depth_unit)
if plot_temperature_unit=='celsius':
	ax[0].set_xlabel('BHA Temperature ($^\circ$C)')
elif plot_temperature_unit=='fahrenheit':	
	ax[0].set_xlabel('BHA Temperature ($^\circ$F)')
ax[1].set_xlabel('BHA Pressure (%s)' % plot_pressure_unit)

lines, labels = ax[0].get_legend_handles_labels()
lines2, labels2 = ax[1].get_legend_handles_labels()
ax[1].legend(lines + lines2, labels + labels2, loc=0,prop={'size':10})
ax[0].grid()
ax[1].grid()

if len(sys.argv) > 4:
	ax.set_ylim([ylimLT,ylimUT])
	ax[1].set_ylim([ylimLP,ylimUP])

plt.gca().invert_yaxis()
plt.tight_layout()
#plt.savefig(os.path.splitext(sys.argv[1])[0] + ".png",dpi=fig.dpi)
plt.show()
