Automated Install
=================
Disclaimer: You could damage your raspberry pi if you do not insert a voltage divider between the echo pin on the sensor and the GPIO pin on the Raspberry Pi.
If you choose to do this you do it at your own risk.

Reduce RAM used by the GPU
==========================

Raspi-Sump is a dedicated device that will not be used for intensive graphical related tasks.  You can minimize the amount of RAM used by the GPU to allow your pi to have more RAM for other tasks.

To do so set the amount of RAM for the GPU to 32MB instead of the default 128MB

    sudo raspi-config

This will present you with a menu system for various options.  Using your arrow key go down the list and select Advanced Options

Now select A3 Memory Split from the menu.
Enter 32 and select OK
Select Finish
Select OK to reboot your pi

Once rebooted you can check the amount of free memory by running the following command.

    free -m

You should see Mem total as 469.  This is good.  We just freed up 96MB of memory for use by other applications.  That's just under a 20% increase.
	

Install Dependancies
====================

If you want to create graphs of sump pit activity install Matplotlib and Numpy
as follows;

    sudo apt-get install python-matplotlib
    sudo apt-get install python-numpy

Also Requires the hcsr04sensor and RPi.GPIO module (see Install Raspi-Sump)

If pip package manager is not installed you can get the latest version at the
following site. (preferred)

    http://pip.readthedocs.org/en/latest/installing.html


Alternately you can install the packaged version with apt-get.


    sudo apt-get install python-pip



Install Raspi-Sump
==================

The following will automatically install hcsr04sensor and RPi.GPIO if it is not already
installed on your Pi.

    sudo pip install raspisump

This will copy all the files you need into /home/pi/raspi-sump


Navigate to /home/pi/raspi-sump/ and move the sample config file
to this directory.

    mv sample_config/raspisump.conf .

The /home/pi/raspi-sump folder is setup as follows on install;

* raspi-sump/sample_config/raspisump.conf (all configurations for raspisump).
* raspi-sump/csv (location of waterlevel readings to csv file)
* raspi-sump/charts (location of charts if using rsumpchart.py)
* raspi-sump/logs (location of rsumpmonitor.py logs if using raspisump as acontinuous process)


**Note take care with your raspisump.conf file if you are using Gmail or any other mail system that requires authentication.  Your username and password will be viewable in the file. You should change the default pi and root passwords on your RaspberryPi.


Edit raspisump.conf 
====================

All configurations are recorded in /home/pi/raspi-sump/raspisump.conf

See the configuration file for explanations of variables.  You can choose to
take imperial (inches) or metric (centimeters) water level readings.


Hardware
========

Setup hardware (Please make sure you understand GPIO information on your pi).

You must use two resistors to create a voltage divider from the Sensor to the Pi.  There are various combinations of resistors that you can use, a google search for Voltage Divider Calculator will allow you to calculate which combination you can use to bring the voltage down from the echo pin to 3.3V.  I used a 470 Ohm and 1K Ohm resistor to bring the voltage down on the GPIO pin to 3.4 which is within a tolerable 5% level. I could have also use a 1K and 2K resistor to give me 3.333V. 


Four wires connected as follows from the sensor to the pi (note, this will require some soldering).  A floppy disk power connector fits nicely on the sensor. 

1-VCC pin to 5V pin on Pi (pin 2)

2-Ground pin to Ground on Pi (pin 6) 

3-Trig pin to GPIO

4-Echo pin to GPIO (need 470R resistor and 1K resistor to create a voltage divider.) In short, the 470 Ohm and 1K Ohm resistor are connected to one another with the Echo wire soldered between both of them to the GPIO pin.  The other end of the 1K resistor is then soldered to the Ground wire.

see http://www.linuxnorth.org/raspi-sump/ for information on pins I used.

Google soldering resistors for good information on how to do this if you have never done it.


Starting Raspi-Sump
===================
To start raspi-sump manually issue the command;

    sudo rsump.py

To run raspisump at 1 minute intervals enter the following line in crontab as follows;

1 - crontab -e

2 - enter line in crontab as follows;

    1 * * * * sudo /usr/local/bin/rsump.py

3 - Save crontab

(See cron documentation for questions on configuring crontab)


4) To monitor the log file in the csv folder while raspi-sump is running;

    tail -f 'csvlogfilename'

If running as a continuous process 
==================================

1) set reading_interval in raspisump.conf to desired interval in seconds (e.g.
reading_interval = 30). The default setting is 0 which will not run rsump.py as
a continuous process.

2) Add rsumpmonitor.py to crontab (see next section)

3) To start Raspi-Sump on bootup add the following line at the end of /etc/rc.local just before the line 'exit 0'

    /usr/local/bin/rsump.py &

5) Reboot your Raspberry Pi or run the following command.  Your pi will run
Raspi-Sump on boot from now on.

    sudo rsump.py &

Note*** Do not forget the ampersand '&' as this will run the script as a background process.

6) To stop Raspi-Sump:

    sudo killall 09 rsump.py

7) To monitor the log file in the csv folder while raspi-sump is running;

    tail -f 'csvlogfilename'

Health check with rsumpmonitor.py. If checking level more than once per minute only.
================================================================================

To check for the health of the rsump.py process run the rsumpmonitor.py script as
root. 
Add to pi user crontab as follows;

1 - crontab -e

2 - enter line in crontab as follows;

    5 * * * * sudo /usr/local/bin/rsumpmonitor.py

3 - Save crontab

This will check the rsump.py process every 5 minutes and restart it if it is stopped.


Making Line Charts of Sump Activity
===================================

You can make a daily chart of sump pump activity by using rsumpchart.py.

1 - From the command line run;

    rsumpchart.py


This will create a line chart of sump pump activity.  You can easily modify the file to save to a different location with another name.
Combined with a scheduled cron job it is an easy way to see the latest activity graphically.

**Note that this requires matplotlib and numpy on your RaspberryPi which can be
installed with the apt-get command.  See the Install Dependancies section at the
beginning of this file.

You can also use the move_file.sh script provided as an example of how you
transfer files offsite to a webserver or save historal chart information.


Optional - Setting Up a Local Web Server for easy Charts Viewing
=================================================================


Setting Up The Local Webserver on the Pi

Purpose
=======

The following instructions allow you to configure your raspberry pi to view
graphs of sump pit activity through your web browser.  This is accomplished by
configuring a local webserver on your pi.

Once complete you will be able to view sump pump activity by connecting to
http://ip_address_of_your_pi

Preperation
===========

If you have not done so in a while run the following command to update your Pi.
This command updates repository information and then upgrades packages that are
installed on your Pi.

    sudo apt-get -y update && sudo apt-get -y upgrade


Getting Started
===============

These instructions will do the following
- install the Apache Webserver
- configure apache for low resource usage
- configure cron to launch script to create for graphs of sump pump activity
- link charts to web folder to view charts


Install Apache Web Server
=========================

At this point many people will tell you that you are better off using Nginx or Lighttpd as they are lower 
resource usage webservers.  They are both fine webservers and if you prefer them, then by all means use 
those.

To install Lighttpd for example simply enter the following:

    sudo apt-get install -y lighttpd

Navigate to http://ip_of_your_pi and view the welcome screen.  There are plenty of resources on the internet
for configuring and using it.

I personally prefer using Apache and configuring it for low resource servers, so that is what I will be
concentrating on in this install.  Apache is the most widely used webserver software on the internet and
has the best resources for information on a multitude of configurations. 

To install Apache:

    sudo apt-get install -y apache2

Configure apache for low resource usage
=======================================

In order to configure the Apache Webserver for low resource systems such as the Raspberry Pi, 
we need to make a few changes to the /etc/apache2/apache2.conf file.  This file is where
we configure the settings of our webserver.

Open the file in a text editor as follows;

    cd /etc/apache2
    sudo nano apache2.conf

Scroll down the file and change the following values;

    Timeout 60
    KeepAliveTimeout 2

Change setting in the mpm_prefork_module and mpm_worker_module as follows


    <IfModule mpm_prefork_module>
        StartServers          1
        MinSpareServers       1
        MaxSpareServers       3
        MaxClients           10
        MaxRequestsPerChild 3000
    </IfModule>
 
    <IfModule mpm_worker_module>
        StartServers          1
        MinSpareThreads       5
        MaxSpareThreads      15 
        ThreadLimit          25
        ThreadsPerChild       5
        MaxClients           25
        MaxRequestsPerChild 200
    </IfModule>


Save and close the apache2.conf file.

Copy the provided html files to your webserver root as follows;

    cp -R /home/pi/raspi-sump/web /var/www

Restart the apache webserver as follows

    sudo /etc/init.d/apache2 restart



Link the charts folder to your web root.

    cd /var/www

    ln -s /home/pi/raspi-sump/charts charts


Setup Cron to generate charts hourly and archive past days
==========================================================

1 - crontab -e

2 - enter line in crontab as follows; 

    59 * * * * sudo /usr/local/bin/rsumpchart.py

(note: provide a script to chart and archive)
3 - Save crontab

(See cron documentation for questions on configuring crontab)


4 - To view sump pit activity navigate to http://ip_of_your_pi
