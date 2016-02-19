'''Monitor the health of a process and restart it if it has stopped
or if it has spawned multiple processes.'''

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

import subprocess
from raspisump import log

def check_pid(process):
    '''Check status of process.'''
    cmdp1 = 'ps aux'
    cmdp2 = 'grep -v grep'
    cmdp3 = 'grep -v sudo'
    cmdp4 = 'grep -c ' + process
    cmdp1list = cmdp1.split(' ')
    cmdp2list = cmdp2.split(' ')
    cmdp3list = cmdp3.split(' ')
    cmdp4list = cmdp4.split(' ')
    part1 = subprocess.Popen(cmdp1list, stdout=subprocess.PIPE)
    part2 = subprocess.Popen(cmdp2list, stdin=part1.stdout,
                             stdout=subprocess.PIPE
                             )
    part1.stdout.close()
    part3 = subprocess.Popen(cmdp3list, stdin=part2.stdout,
                             stdout=subprocess.PIPE
                             )
    part2.stdout.close()
    part4 = subprocess.Popen(cmdp4list, stdin=part3.stdout,
                             stdout=subprocess.PIPE
                             )
    part3.stdout.close()
    number_of_processes = int(part4.communicate()[0])
    if number_of_processes == 0:
        log.log_restarts('Process stopped, restarting')
        restart(process)
    elif number_of_processes == 1:
        exit(0)
    else:
        log.log_restarts('Multiple processes...killing and restarting')
        kill_start(process)


def restart(process):
    '''Restart process'''
    restart_cmd = process + ' &'
    restart_now = restart_cmd.split(' ')
    subprocess.Popen(restart_now)
    exit(0)


def kill_start(process):
    '''Kill all instances of process and initiate restart.'''
    kill_cmd = 'killall 09 ' + process
    kill_it = kill_cmd.split(' ')
    subprocess.call(kill_it)
    restart(process)
