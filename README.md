New Version 0.8.0
=================

See the changelog for changes to all versions.

Note if upgrading from version 0.5.x
====================================

You will need to add variables to your raspisump.conf file.  Copy the new conf file located in the /home/pi/raspi-sump/conf folder to
/home/pi/raspi-sump.  Re-enter all of your variables.  Older info has been saved in
/home/pi/raspi-sump/raspisump.conf.save

Simply upgrading from version 0.5.x will break your current install of Raspi-Sump
unless you take some time to fix your configuration file.

I recommend you keep using v0.5.3 if you don't want to do this.

To roll back to v0.5.3 simply do the following;

    sudo pip uninstall raspisump
    sudo pip install https://pypi.python.org/packages/source/r/raspisump/raspisump-0.5.3.tar.gz#md5=91aed30a087c35e12ae36fe7a9523945


If you are running version 0.6.0 or later you need not change anything.

QUICK INSTALL
=============
Install the pip package manager (if not present on your pi).

    sudo apt-get install python-pip


Install Raspi-Sump.

    sudo pip install raspisump

Upgrading an existing version


    sudo pip install -U raspisump

This will also install the [HCSR04sensor](https://github.com/alaudet/hcsr04sensor) and  RPi.GPIO modules if not present on your Pi.

If you want to use charts install maplotlib and numpy

    sudo apt-get install python-matplotlib

    sudo apt-get install python-numpy

Read the configuration docs copied during setup on your pi at the following location;

    /home/pi/raspi-sump/docs

They are also available on github https://github.com/alaudet/raspi-sump/blob/master/docs/install.md


Description
===========
Raspi-sump is a sump pit water level monitoring system using a Raspberry Pi and an 
Ultrasonic Sensor (HC-SR04)


![alt tag](http://www.linuxnorth.org/raspi-sump/images/raspi-chart.png)


Currently the system monitors the water level in your pit at defined intervals. It sends
email sms alerts if the water reaches a critical level, indicating a possible sump pump failure.

See the changelog for the latest features.

More Info
=========
Further details provided at http://www.linuxnorth.org/raspi-sump/

An hourly updating graph is available for view.
http://www.linuxnorth.org/raspi-sump/raspi-sump-today.html

Disclaimer
==========
You are welcome to use Raspi-Sump but there is no guarantee it will work. Your house may still flood if your sump pump fails. This software comes with no warranty. See License details.

This is not a replacement for remaining vigilant in maintaining your water pumping system. It is one tool you can use to give yourself extra piece-of-mind.

Best practices should also include:

* A backup pump that triggers at a slightly higher water level than your main pump.
* The secondary pump should be connected to a seperate dedicated electrical breaker. 
* You should also have a generator that can provide power should you have an extended outage during the spring or other unseasonally wet time of year.
* if you are building a new home, pay attention to the grade of your property, as you may even be able to let gravity empty your pit for you.  That would be the best approach with a backup pump just in case. 

Once you have done all of these things, then consider using a monitoring system like Raspi-Sump.

License
=======
MIT License.  I want you to do whatever you want with Raspi-Sump.  If you
improve it please let me know.

Contributing
============
If you add a useful feature please consider forking Raspi-Sump and contributing
back by issuing a Pull Request.   Use the devel branch for adding new features
and if it works I will merge them into Master.
