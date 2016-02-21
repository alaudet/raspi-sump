'''Create charts for viewing on Raspberry Pi Web Server.'''

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.htmlimport os

import os
import subprocess
import time
from raspisump import todaychart


def create_folders(year, month, homedir):
    '''Check if folders exist in charts folder and create them if they don't'''
    if not os.path.isdir('{}charts/{}/'.format(homedir, year)):
        _year = 'mkdir {}charts/{}'.format(homedir, year)
        create_year = _year.split(' ')
        subprocess.call(create_year)

    if not os.path.isdir('{}charts/{}/{}/'.format(homedir, year, month)):
        _month = 'mkdir {}charts/{}/{}'.format(homedir, year, month)
        create_month = _month.split(' ')
        subprocess.call(create_month)


def create_chart(homedir):
    '''Create a chart of sump pit activity and save to web folder'''
    csv_file = '{}csv/waterlevel-{}.csv'.format(
        homedir, time.strftime('%Y%m%d')
        )
    filename = '{}charts/today.png'.format(homedir)
    bytes2str = todaychart.bytesdate2str('%H:%M:%S')
    todaychart.graph(csv_file, filename, bytes2str)


def copy_chart(year, month, today, homedir):
    '''Copy today.png to year/month/day folder for web viewing'''
    copy_cmd = 'cp {}charts/today.png {}charts/{}/{}/{}.png'.format(
        homedir, homedir, year, month, today
        )
    copy_file = copy_cmd.split(' ')
    subprocess.call(copy_file)
