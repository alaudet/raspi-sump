#!/usr/bin/python
# Check to make sure process raspi-sump is running and restart process if required.
# lots of duplicate code.  File working will cleanup later

import subprocess
import time

def check_pid():
    logfile = open("/home/pi/raspi-sump/process_log", 'a')
    cmdp1 = "ps aux"
    cmdp2 = "grep -v grep"
    cmdp3 = "grep -v sudo"
    cmdp4 = "grep -c /home/pi/raspi-sump/raspisump.py"
    cmdp1list = cmdp1.split(' ')
    cmdp2list = cmdp2.split(' ')
    cmdp3list = cmdp3.split(' ')
    cmdp4list = cmdp4.split(' ')
    part1 = subprocess.Popen(cmdp1list, stdout=subprocess.PIPE)
    part2 = subprocess.Popen(cmdp2list, stdin=part1.stdout, stdout=subprocess.PIPE)
    part1.stdout.close()
    part3 = subprocess.Popen(cmdp3list, stdin=part2.stdout,stdout=subprocess.PIPE)
    part2.stdout.close()
    part4 = subprocess.Popen(cmdp4list, stdin=part3.stdout,stdout=subprocess.PIPE)
    part3.stdout.close()
    x = int(part4.communicate()[0])
     
    if x == 0:
        logfile.write(time.strftime("%Y-%m-%d %H:%M:%S,")),
        logfile.write("Process stopped, Restarting"),
        logfile.write("\n")
        logfile.close
        restart()
    
    elif x == 1:
        logfile.write(time.strftime("%Y-%m-%d %H:%M:%S,")),
        logfile.write("Process Healthy...Exiting"),
        logfile.write("\n")
        logfile.close
        exit(0)
    
    else:
        logfile.write(time.strftime("%Y-%m-%d %H:%M:%S,")),
        logfile.write("Multiple Processes...Killing and Restarting"),
        logfile.write("\n")
        logfile.close
        kill_start()

        
def restart():
    print "Restarting Raspi-Sump"
    restart_cmd = "/home/pi/raspi-sump/raspisump.py &"
    restart_now = restart_cmd.split(' ')
    subprocess.Popen(restart_now)
    exit(0)

def kill_start():
    print "Killing Raspi-Sump"
    kill_cmd = "killall 09 raspisump.py"
    kill_it = kill_cmd.split(' ')
    subprocess.call(kill_it)
    restart()    
 
check_pid()
