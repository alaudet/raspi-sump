Raspi-sump is a sump pit water level monitoring system using a Raspberry Pi and an Ultrasonic Sensor (HC-SR04).

![Chart](https://raspisump.linuxnorth.org/static/today.png)


Currently the system monitors the water level in your pit at defined intervals. It sends
email sms alerts if the water reaches a critical level, indicating a possible sump pump failure.

# What's New

See the [changelog](https://github.com/alaudet/raspi-sump/blob/master/changelog) for the latest information on Raspi-Sump features.

# Supported Versions of Raspbian / Raspberry Pi OS

Raspi-Sump is currently supported on Raspberry Pi OS (Bullseye) and Raspian (Buster)

# Discord Group

Discuss and get support from other users. Email (alaudet@linuxnorth.org) for an invite link.


# Install Dependencies

    sudo apt install python3-pip python3-rpi.gpio python3-matplotlib

# Install Raspi-Sump

Pip installs default to Wheels which omits some folder setup in setup.py.
Always use the '--no-binary :all:' option when installing or upgrading Raspi-Sump with pip.

    sudo pip3 install --no-binary :all: raspisump


# Upgrading Raspi-Sump 

Upgrading an existing version

    sudo pip3 install -U --no-binary :all: raspisump

This will also install the [HCSR04sensor](https://github.com/alaudet/hcsr04sensor) 


Read the configuration docs copied during setup on your pi at the following location;

    /home/username/raspi-sump/docs

They are also available on github https://github.com/alaudet/raspi-sump/blob/master/docs/install.md


# Python2 (End of Life was January 1, 2020)

Python2 installs of Raspi-Sump are no longer supported.


# More Info

Further details provided at https://www.linuxnorth.org/raspi-sump/

An example hourly updating graph is available for view.
https://www.linuxnorth.org/raspi-sump/raspi-sump-today.html

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
