#!/usr/bin/python

import time
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

csvfile = "/home/pi/raspi-sump/csv/waterlevel-%s.csv" % time.strftime('%Y%m%d')
filename = "/home/pi/raspi-sump/charts/today.png"


def graph(csvfile, filename):
    date, value = np.loadtxt(csvfile, delimiter=',', unpack=True,
                             converters={0: mdates.strpdate2num('%H:%M:%S')}
                             )
    fig = plt.figure(figsize=(10, 3.5))
    ax1 = fig.add_subplot(111, axisbg='white', frameon=False)
    rcParams.update({'font.size': 9})
    plt.plot_date(x=date, y=value, ls='solid', linewidth=2, color='#FB921D',
                  fmt=':'
                  )
    title = "Sump Pit Water Level %s" % time.strftime('%Y-%m-%d %H:%M')
    t = plt.title(title)
    t.set_y(1.09)
    plt.subplots_adjust(top=0.86)
    plt.ylabel('Centimeters')
    plt.xlabel('Time of Day')
    plt.xticks(rotation=30)
    plt.grid(True, color='#ECE5DE', linestyle='solid')
    plt.tick_params(axis='x', bottom='off', top='off')
    plt.tick_params(axis='y', left='off', right='off')
    plt.savefig(filename, dpi=72)

graph(csvfile, filename)
