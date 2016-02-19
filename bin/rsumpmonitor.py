#!/usr/bin/env python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

from raspisump import checkpid


def main():
    '''run checkpid.py module to restart Raspi-Sump if the rsump.py process is
    stopped or has spawned multiple processes.'''
    process = 'rsump.py'
    checkpid.check_pid(process)

if __name__ == "__main__":
    main()
