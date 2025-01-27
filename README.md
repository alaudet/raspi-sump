Raspi-sump is a sump pit water level monitoring system that uses a Raspberry Pi and an Ultrasonic Sensor (HC-SR04).

![MobileScreenshot](https://www.linuxnorth.org/raspi-sump/images/rsump_mobile_1.9.jpg)

Currently the system monitors the water level in your pit at defined intervals. It sends
email sms alerts if the water reaches a critical level, indicating a possible sump pump failure.

# What's New

Verison 1.10 - Raspi-Sump is now installed in a virtual environment that uses Python3-virtualenv. This will require an uninstall of version 1.9 and a reinstall of Raspi-Sump with new [install instructions](https://github.com/alaudet/raspi-sump/blob/master/docs/install.md). You will not lose any of your configuration settings.

See the [changelog](https://github.com/alaudet/raspi-sump/blob/master/changelog) for the latest information on Raspi-Sump features.

# Supported Versions of Raspberry Pi OS

Raspi-Sump now supports Raspberry Pi OS 12 (Bookworm) and Raspberry Pi OS 11 (Bullseye) as of version 1.10 which installs Raspi-Sump in a Python3 virtual environment.

Raspi-Sump version 1.9.4 is still supported on Raspberry Pi OS 11 (Bullseye) but is now depracated in favour of version 1.10. No new features will be added to version 1.9.

Support for Raspberry Pi OS 11 (Bullseye) ends on August 31st, 2026.

Old versions of Raspbian OS (10 and below) are no longer supported.

Raspi-Sump follows the Debian release schedule published on the [Debian Linux Wiki](https://wiki.debian.org/DebianReleases)

# Discord Group

Discuss and get support from other users. Email (alaudet@linuxnorth.org) for an invite link.

# Install Raspi-Sump

Full install instructions are located at https://github.com/alaudet/raspi-sump/blob/master/docs/install.md

# Upgrade Raspi-Sump

Upgrade an existing version

    source /opt/raspi-sump/bin/activate
    pip3 install -U --no-binary :all: raspisump
    deactivate

# More Info

Further details provided at https://www.linuxnorth.org/raspi-sump/

# Disclaimer

You are welcome to use Raspi-Sump but there is no guarantee it will work. Your house may still flood if your sump pump fails. This software comes with no warranty. See License details.

This is not a replacement for a properly maintained water pumping system. It is a passive monitoring tool to give yourself extra peace-of-mind.

Best practices include:

- A backup pump that triggers at a slightly higher water level than your main pump.
- The secondary pump should be connected to a seperate dedicated electrical breaker.
- You should also have an alternate power source (generator or sump battery backup) that can provide power to your pump should you have an extended outage during the spring or other unseasonally wet time of year.
- if you are building a new home, pay attention to the grade of your property, as you may be able to let gravity empty your pit for you. That would be the best approach with a sump pump for backup protection against pipe clogs and Raspi-Sump for monitoring.

# License

Raspi-Sump is released under the [MIT License](https://github.com/alaudet/raspi-sump/blob/master/LICENSE).

# Contribute

Please refer to the [Contributing Guidelines](https://github.com/alaudet/raspi-sump/blob/master/CONTRIBUTING.md) before issuing a pull request.

# Donate

[Your Donation is Appreciated](https://www.linuxnorth.org/donate/)
