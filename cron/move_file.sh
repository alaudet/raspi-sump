#!/bin/sh

# This file is an example of how you can move files offsite and save historical 
# charting information. It is not ready to use as is, as everyone has differents requirements.
# It is only meant as one way of doing things. 
# This file is meant to be called from cron at one hour intervals.


source=/home/pi/raspi-sump/csv/*
dest=user@host:path/to/destination/folder
chart_source=/home/pi/raspi-sump/charts/*
chart_dest=user@host:path/to/images/folder
today="$(date +%Y-%m-%d)".png
month="$(date +%m)"
year="$(date +%Y)"

# keep a history of charts
cp /home/pi/raspi-sump/charts/today.png /home/pi/raspi-sump/charts/$year/$month/$today

# move waterlevel files offsite
rsync -r -a -v -e "ssh -i /home/pi/.ssh/<identity file>" $source $dest
