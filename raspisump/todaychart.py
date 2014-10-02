#!/usr/bin/python

"""
The MIT License (MIT)

Copyright (c) 2014 Al Audet

Permission is hereby granted, free of charge, to any person obtaining a copy
of Raspi-Sump and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included
    in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
"""

import time
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})


def graph(csv_file, filename):
    """Create a line graph from a two column csv file."""
    date, value = np.loadtxt(csv_file, delimiter=',', unpack=True,
                             converters={0: mdates.strpdate2num('%H:%M:%S')}
                             )
    fig = plt.figure(figsize=(10, 3.5))
    fig.add_subplot(111, axisbg='white', frameon=False)
    rcParams.update({'font.size': 9})
    plt.plot_date(x=date, y=value, ls='solid', linewidth=2, color='#FB921D',
                  fmt=':'
                  )
    title = "Sump Pit Water Level {}".format(time.strftime('%Y-%m-%d %H:%M'))
    title_set = plt.title(title)
    title_set.set_y(1.09)
    plt.subplots_adjust(top=0.86)
    plt.ylabel('Centimeters')
    plt.xlabel('Time of Day')
    plt.xticks(rotation=30)
    plt.grid(True, color='#ECE5DE', linestyle='solid')
    plt.tick_params(axis='x', bottom='off', top='off')
    plt.tick_params(axis='y', left='off', right='off')
    plt.savefig(filename, dpi=72)


def main():
    """Main function to initiate graph."""
    csv_file = "/home/pi/raspi-sump/csv/waterlevel-{}.csv".format(
        time.strftime('%Y%m%d')
        )
    filename = "/home/pi/raspi-sump/charts/today.png"
    graph(csv_file, filename)

if __name__ == "__main__":
    main()
