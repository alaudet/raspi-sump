Raspi-sump is a sump pit water level monitoring system using a Raspberry Pi and an Ultrasonic Sensor (HC-SR04).

![Chart](https://www.linuxnorth.org/raspi-sump/images/raspi-chart.png)


Currently the system monitors the water level in your pit at defined intervals. It sends
email sms alerts if the water reaches a critical level, indicating a possible sump pump failure.

# Supported Versions of Raspbian / Raspberry Pi OS

Raspi-Sump is currently supported on Raspberry Pi OS (Bullseye) and Raspian (Buster and Stretch).

Raspian 9 (Stretch) support will be discontinued in June 2022.  Please upgrade to Raspberry Pi OS 11 Bullseye if you are currently using Stretch.

# Discord Group

Discuss and get support from other users. Email (alaudet@linuxnorth.org) for an invite link.


# Installing with pip version 9 or greater


Pip versions > 7 default to Wheels which omits some folder setup in setup.py.
If using Raspbian Stretch or later versions install as follows;

    sudo pip3 install --no-binary :all: raspisump


# New in Version 1.3

Support for charts with Raspberry Pi OS 11 Bullseye.

# New in Version 1.2

Added improvements to SMS/Email Alerts

1 - Alerts now contain hostname to better identify which instance of Raspi-Sump is
reporting.

2 - Heartbeat SMS/Email notifications can be enabled to send at a user defined interval, to let you know
that alerts are working.  


Added to [Email] section of raspisump.conf

    heartbeat = 0 or 1 (disabled or enabled)
    heartbeat_interval = user defined number of minutes between notifications

If configuration items are not present in raspisump.conf the default is set to
off (no notifications)


For more information see [Issue 7](https://github.com/alaudet/raspi-sump/issues/7).

# QUICK INSTALL 


Install the pip package manager (if not present on your pi).

    sudo apt-get install python3-pip


Install Raspi-Sump.

    sudo pip3 install --no-binary :all: raspisump

Upgrading an existing version


    sudo pip3 install -U --no-binary :all: raspisump

This will also install the [HCSR04sensor](https://github.com/alaudet/hcsr04sensor) and  RPi.GPIO modules if not present on your Pi.

If you want to use charts install maplotlib.

    sudo apt-get install python3-matplotlib


Matplotlib should install Numpy.  If you need to install Numpy seperately;

    sudo apt-get install python3-numpy

Read the configuration docs copied during setup on your pi at the following location;

    /home/pi/raspi-sump/docs

They are also available on github https://github.com/alaudet/raspi-sump/blob/master/docs/install.md


# Upgrading from Python2 to Python3 (Raspbian Jessie)

    sudo pip uninstall raspisump
    sudo pip3 install --no-binary :all: raspisump


Your configuration file will be preserved in /home/pi/raspi-sump/


# Python2 install (End of Life is January 1, 2020)

Python2 installs of Raspi-Sump are no longer be supported.


# More Info

Further details provided at http://www.linuxnorth.org/raspi-sump/

An example hourly updating graph is available for view.
http://www.linuxnorth.org/raspi-sump/raspi-sump-today.html

# Disclaimer

You are welcome to use Raspi-Sump but there is no guarantee it will work. Your house may still flood if your sump pump fails. This software comes with no warranty. See License details.

This is not a replacement for a properly maintained water pumping system. It is one tool you can use to give yourself extra piece-of-mind.

Best practices should include:

* A backup pump that triggers at a slightly higher water level than your main pump.
* The secondary pump should be connected to a seperate dedicated electrical breaker. 
* You should also have a generator that can provide power should you have an extended outage during the spring or other unseasonally wet time of year.
* if you are building a new home, pay attention to the grade of your property, as you may be able to let gravity empty your pit for you.  That would be the best approach with a backup pump for added protection.

Once you have done all of these things, then consider using a monitoring system like Raspi-Sump.

# License

MIT License.  I want you to do whatever you want with Raspi-Sump.  If you
improve it please let me know.

# Contributing

Please refer to the [Contributing Guidelines](https://github.com/alaudet/raspi-sump/blob/master/CONTRIBUTING.md) before issuing a pull request.

# Donate

[Your Donation is Appreciated](https://www.linuxnorth.org/donate/)
