#!/bin/sh

source=/home/pi/raspi-suimp/csv/*
dest=user@host:path/to/destination/folder

rsync -r -a -v -e "ssh -i /home/pi/.ssh/<identity file>" $source $dest
