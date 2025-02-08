"""Graph sump pit activity."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import time
import numpy as np
import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
from raspisump import config_values

rcParams.update({"figure.autolayout": True})


configs = config_values.configuration()


def graph(csv_file, filename):
    """Create a line graph from a two column csv file."""

    unit = configs["unit"]

    date, value = np.loadtxt(
        csv_file,
        delimiter=",",
        unpack=True,
        converters={0: lambda x: mdates.datestr2num(x.decode("utf8"))},
    )

    fig = plt.figure(figsize=(10, 3.5))

    fig.add_subplot(111, facecolor="white", frameon=False)

    rcParams.update({"font.size": 9})

    plt.plot(
        date,
        value,
        ls="solid",
        linewidth=2,
        color="#" + configs["line_color"],
        marker="",
    )

    # Format the x-axis to use the specified formats and interval
    ax = plt.gca()
    hours = mdates.HourLocator(interval=2)
    fmt = mdates.DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(fmt)

    title = f"Water Level {time.strftime('%Y-%m-%d %H:%M')}"
    title_set = plt.title(title)
    title_set.set_fontsize(20.0)
    title_set.set_y(1.09)
    plt.subplots_adjust(top=0.86)

    if unit == "imperial":
        plt.ylabel("inches", fontsize=16)
    if unit == "metric":
        plt.ylabel("centimeters", fontsize=16)

    plt.xlabel("Time of Day", fontsize=16)
    plt.xticks(rotation=30)
    plt.grid(True, color="#ECE5DE", linestyle="solid")
    plt.tick_params(axis="x", bottom=False, top=False)
    plt.tick_params(axis="y", left=False, right=False)
    plt.savefig(filename, transparent=True, dpi=72)
