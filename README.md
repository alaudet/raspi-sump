GET ME TO THE ACTION - QUICK INSTALL
====================================
Install the pip package manager if not present on you pi at;

http://pip.readthedocs.org/en/latest/installing.html

Install Raspi-Sump

    sudo pip install raspisump

This will also install RPi.GPIO if not present on the system.

If you want to use charts install maplotlib and numpy

    sudo apt-get install python-matplotlib

    sudo apt-get install python-numpy

Read the configuration docs copied during setup on your pi at the following location;

    /home/pi/raspi-sump/docs


Description
===========
Raspi-sump is a sump pit water level monitoring system using a Raspberry Pi and an 
Ultrasonic Sensor (HC-SR04)

Currently the system monitors the water level in your pit at defined intervals. It sends
email sms alerts if the water reaches a critical level, indicating a possible sump pump failure.

The Raspberry Pi uses Linux (Raspbian) which is not a real time OS.  This has implications 
for this type of application as a multitasking OS like Linux will cause some small error
variance in the readings, as opposed to an Arduino that uses a RealTime OS. 

While the accuracy is fine for a home system, the problem is mitigated by taking a larger sorted sample of readings and using the median reading as the reported one.  In my testing so far I have a variance of about one centimeter which is acceptable for a residential monitoring system.  It would appear that using the median reading eliminates the infrequent fringe type readings that can give false positives.

Future versions will include;
- An offsite web component for viewing historical data, including graphs and water volume
- Proper push button shutdown to turn off the pi (raspi-atx)
- LCD panel to get a quick glance of the water level without opening the lid.

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
