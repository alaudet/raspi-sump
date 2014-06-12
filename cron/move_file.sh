#!/bin/sh

ssh_key=~/.ssh/<private_key_name>
source=/home/pi/raspi-sump/csv/
dest=user@host:path/to/destination/folder

rsync -r -a -v -e "ssh -i $ssh_key" $source $dest
