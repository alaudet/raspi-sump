Raspi-sump is a sump pit water level monitoring system that uses a Raspberry Pi and an Ultrasonic Sensor (HC-SR04).

![MobileScreenshot](https://www.linuxnorth.org/raspi-sump/images/rsump_mobile_1.9.jpg)

Currently the system monitors the water level in your pit at defined intervals. It sends
email sms alerts if the water reaches a critical level, indicating a possible sump pump failure.

# What's New

Version 1.9 - `Systemd` now replaces `rsumpmonitor.py`/`checkpid.py`. Control all Raspi-Sump services and Chart creation timers with `Systemd`.

See the [changelog](https://github.com/alaudet/raspi-sump/blob/master/changelog) for the latest information on Raspi-Sump features.

# Supported Versions of Raspbian / Raspberry Pi OS

Raspi-Sump is currently supported on Raspberry Pi OS (Bullseye) and Raspian (Buster)

# Discord Group

Discuss and get support from other users. Email (alaudet@linuxnorth.org) for an invite link.

# Install Raspi-Sump

Full install instructions are located at https://github.com/alaudet/raspi-sump/blob/master/docs/install.md

# Upgrade Raspi-Sump

Upgrade an existing version

    sudo pip3 install -U --no-binary :all: raspisump

If upgrading from version 1.8 or lower to version 1.9 see the [1.9 Upgrade Instructions](https://github.com/alaudet/raspi-sump/blob/master/docs/upgrade_to_version_1.9.md)

# More Info

Further details provided at https://www.linuxnorth.org/raspi-sump/

# Disclaimer

You are welcome to use Raspi-Sump but there is no guarantee it will work. Your house may still flood if your sump pump fails. This software comes with no warranty. See License details.

This is not a replacement for a properly maintained water pumping system. It is one tool you can use to give yourself extra piece-of-mind.

Best practices should include:

- A backup pump that triggers at a slightly higher water level than your main pump.
- The secondary pump should be connected to a seperate dedicated electrical breaker.
- You should also have a generator that can provide power should you have an extended outage during the spring or other unseasonally wet time of year.
- if you are building a new home, pay attention to the grade of your property, as you may be able to let gravity empty your pit for you. That would be the best approach with a backup pump for added protection.

Once you have done all of these things, then consider using a monitoring system like Raspi-Sump.

# License

Raspi-Sump is released under the [MIT License](https://github.com/alaudet/raspi-sump/blob/master/LICENSE).

# Contribute

Please refer to the [Contributing Guidelines](https://github.com/alaudet/raspi-sump/blob/master/CONTRIBUTING.md) before issuing a pull request.

# Donate

[Your Donation is Appreciated](https://www.linuxnorth.org/donate/)
