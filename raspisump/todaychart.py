"""Graph sump pit activity."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import time
import os
import numpy as np
import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams

rcParams.update({"figure.autolayout": True})
import configparser

config = configparser.RawConfigParser()
user = os.getlogin()
config.read("/home/" + user + "/raspi-sump/raspisump.conf")
configs = {"unit": config.get("pit", "unit")}

try:
    configs["line_color"] = config.get("charts", "line_color")
except configparser.NoSectionError:
    configs["line_color"] = "FB921D"


rcParams["date.autoformatter.minute"] = "%H:%M:%S"
rcParams["date.autoformatter.hour"] = "%H:%M:%S"


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
    plt.plot_date(
        x=date,
        y=value,
        ls="solid",
        linewidth=2,
        color="#" + configs["line_color"],
        fmt=":",
    )
    title = "Sump Pit Water Level {}".format(time.strftime("%Y-%m-%d %H:%M"))
    title_set = plt.title(title)
    title_set.set_y(1.09)
    plt.subplots_adjust(top=0.86)

    if unit == "imperial":
        plt.ylabel("inches")
    if unit == "metric":
        plt.ylabel("centimeters")

    plt.xlabel("Time of Day")
    plt.xticks(rotation=30)
    plt.grid(True, color="#ECE5DE", linestyle="solid")
    plt.tick_params(axis="x", bottom=False, top=False)
    plt.tick_params(axis="y", left=False, right=False)
    plt.savefig(filename, dpi=72)
