#!/usr/bin/python
# Check to make sure process raspi-sump is running and restart if required.

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

# Note
'''Only use checkpid.py with raspisump_alternate.py. This will monitor the
health of the raspisump process and restart it if it is stopped.
The only reason for using this file instead of cron is that cron is limited
to running processes every minute.  If you need to set your reading interval
to a lower value, like 30 seconds, this file will make sure the raspisump
process recovers from a failure.
'''

import subprocess
import time


def check_pid():
    '''Check status of raspisump_alternate.py process.'''
    cmdp1 = "ps aux"
    cmdp2 = "grep -v grep"
    cmdp3 = "grep -v sudo"
    cmdp4 = "grep -c /usr/local/bin/raspisump_alternate.py"
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
        log_restarts("Process stopped, restarting")
        restart()
    elif number_of_processes == 1:
        exit(0)
    else:
        log_restarts("Multiple processes...killing and restarting")
        kill_start()


def restart():
    '''Restart raspisump.py process.'''
    restart_cmd = "/usr/local/bin/raspisump_alternate.py &"
    restart_now = restart_cmd.split(' ')
    subprocess.Popen(restart_now)
    exit(0)


def kill_start():
    '''Kill all instances of raspisump.py process.'''
    kill_cmd = "killall 09 raspisump_alternate.py"
    kill_it = kill_cmd.split(' ')
    subprocess.call(kill_it)
    restart()


def log_restarts(reason):
    '''Log all process restarts'''
    logfile = open("/home/pi/raspi-sump/logs/process_log", 'a')
    logfile.write(time.strftime("%Y-%m-%d %H:%M:%S,")),
    logfile.write(reason),
    logfile.write("\n")
    logfile.close

if __name__ == "__main__":
    check_pid()
