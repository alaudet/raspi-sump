#!/usr/bin/python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/

import time
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

filename = "/home/pi/raspi-sump/charts/today.png" 

def graph(filename):
    csvfile = "/home/pi/raspi-sump/csv/waterlevel-%s.csv" % time.strftime('%Y%m%d')
    date, value = np.loadtxt(csvfile, delimiter=',', unpack=True,
            converters = {0:mdates.strpdate2num('%H:%M:%S')})

    fig = plt.figure(figsize=(8,3))        
    ax1 = fig.add_subplot(111, axisbg='white')

    plt.plot_date(x=date, y=value, ls='solid', color='green', fmt=':')
    title = "Sump Pit Water Level %s" % time.strftime('%Y-%m-%d %H:%M')
    plt.title(title)
    plt.ylabel('Water Level (centimeters)')
    plt.xlabel('Time of Day')
    plt.xticks(rotation=30)    
    plt.grid(True)
    plt.savefig(filename,dpi=72)

graph(filename)
