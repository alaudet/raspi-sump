# Raspi-Sump Installation Instructions

Installation instructions assume Python3 on Raspberry Pi OS 11 (Bullseye) or Raspbian version 10 (Buster).

# Supported OS Versions

Raspberry Pi OS 11 (Bullseye)

Raspbian OS 10 (Buster)

Raspbian OS 9 (Stretch) - Support ended on June 30, 2022. Upgrade to Bullseye.

# Hardware

_Disclaimer: You could damage your raspberry pi if you do not insert a voltage divider between the echo pin on the sensor and the GPIO pin on the Raspberry Pi.
If you choose to do this you do it at your own risk. Please make sure you understand GPIO information on your pi._

Before installing Raspi-Sump you must setup your hardware.

Use two resistors to create a voltage divider from the Sensor to the
Pi. There are various combinations of resistors that you can use, a google
search for Voltage Divider Calculator will allow you to calculate which
combination you can use to bring the voltage down from the echo pin to 3.3V. I
used a 470 Ohm and 1K Ohm resistor to bring the voltage down on the GPIO pin to
3.4 which is within a tolerable 5% level. I could have also used a 1K and 2K resistor to give me 3.333V.

Four wires connected as follows from the sensor to the pi (note, this will
require some soldering). A floppy disk power connector fits nicely on the
sensor. If you are just testing then a breadboard works great for quick and easy
connections.

- VCC pin to 5V pin on Pi (pin 2)

- Ground pin to Ground on Pi (pin 6)

- Trig pin to GPIO

- Echo pin to GPIO (need 470R resistor and 1K resistor to create a voltage divider.) In short, the 470 Ohm and 1K Ohm resistor are connected to one another with the Echo wire soldered between both of them to the GPIO pin. The other end of the 1K resistor is then soldered to the Ground wire.

see https://www.linuxnorth.org/raspi-sump/ for information on pins I used and more details about the hardware setup.

Google soldering resistors for good information on how to do this if you have never done it.

# Install Dependencies

**Note**: Your account must have sudo access to install Raspi-Sump.

Now that your hardware is setup and properly connected to the gpio pins, login to your Raspberry Pi.

Check that your user account is a member of the gpio group. This is needed for accessing the gpio pins.

    groups

You should see all groups your account belongs to. If gpio is not listed run the following command (where `username` is your account name);

    sudo usermod -aG gpio `username`

Logout and log back into your account for the groups to take effect.

Install Pip, RPi.GPIO and Matplotlib

    sudo apt update && sudo apt -y upgrade
    sudo apt install python3-pip python3-rpi.gpio python3-matplotlib

RPi.GPIO is the library that controls the sensor.

Matplotlib is used to generate charts.

The Pip package manager is required to install Raspi-Sump in the next step.

# Install Raspi-Sump

The following will automatically install hcsr04sensor if it is not already installed on your Pi.

    sudo pip3 install --no-binary :all: raspisump

Navigate to /home/`username`/raspi-sump/ and move the sample config file
to this directory.

    cd /home/`username`/raspi-sump
    mv sample_config/raspisump.conf .

The /home/`username`/raspi-sump folder is setup as follows on install;

- raspi-sump/sample_config/raspisump.conf (all configurations for raspisump).
- raspi-sump/csv (location of waterlevel readings to csv file)
- raspi-sump/charts (location of charts if using rsumpchart.py)
- raspi-sump/logs (location of rsumpmonitor.py logs if using raspisump as a continuous process)
- raspi-sump/web (all files needed for the optional pi webserver install)
- "depracated" raspi-sump/cron (example crontab for scheduling readings)

  - NOTE that cron has been replaced with systemd.

\*\*Note take care with your raspisump.conf file if you are using Gmail or any
other mail system that requires authentication. Your `username` and password
will be viewable in the file. You should have a strong password on your account.. The installer also tightens file security on
the file automatically.

# Edit raspisump.conf

All configurations are recorded in /home/`username`/raspi-sump/raspisump.conf

See the configuration file for explanations of variables. You can choose to
take imperial (inches) or metric (centimetres) water level readings.

# Start Raspi-Sump with Systemd

To start Raspi-Sump you will need to enable it with systemd. The first time you install Raspi-Sump you will need to run this command for systemd to find the service files located in /home/`username`/.config/systemd/user

    systemctl --user daemon-reload

Start the raspisump service

    systemctl --user start raspisump

Configure raspisump to start after reboots

    systemctl --user enable raspisump

To monitor the log file in the csv folder while raspi-sump is running;

    tail -f 'waterlevel-20230523.csv'

## Extra systemd commands

If you ever need to stop raspisump

    systemctl --user stop raspisump

Prevent Raspi-Sump from running at boot time

    systemctl --user disable raspisump

If you make a change to the raspisump.conf file, you must restart raspisump

    systemctl --user restart raspisump

View the current status of the raspisump process

    systemctl --user status raspisump

# Generate Line Charts of Sump Activity

You can automate the creation of charts at 15 minute intervals with systemd for later viewing on the pi webserver which will be configured later in this document. The first time it runs your webchart folder directory will be automatically created.

    systemctl --user start rsumpwebchart.timer
    systemctl --user enable rsumpwebchart.timer

## Extra systemd commands

Prevent charts from being automatically created

    systemctl --user stop rsumwebchart.timer

Prevent charts from being activated at boot time

    systemctl --user disable rsumpwebchart.timer

View the current status of the chart timer

    systemctl --user status rsumpwebchart.timer

# Test Email Alerts

### On Demand Email Test

To test that emails are working run the command 'emailtest';

    emailtest

### Heartbeat Alerts

Raspi-Sump can send email tests at predefined intervals. See the raspisump.conf file option 'heartbeat' and 'heartbeat_interval'.

In /home/`username`/raspi-sump/raspisump.conf, this section configures the email heartbeat once per week.

    # Set a heartbeat sms or email interval in order to regularly test that your
    # notifications are working as intended.
    # 0 = No notifications
    # 1 = Send notifications
    heartbeat = 1

    # Set the frequency of the sms/email heartbeat notifications.
    # Values can be set to any number and are in minutes.
    # For reference;
    # daily   = 1439 minutes
    # weekly  = 10079 minutes
    # Monthly = 43199 minutes
    heartbeat_interval = 10079

# Set Up a Local Web Server for easy Charts Viewing

## Purpose

The following instructions allow you to configure your raspberry pi to view graphs of sump pit activity through your web browser. This is accomplished by configuring a local webserver on your pi.

Once complete you will be able to view sump pump activity by connecting to
http://ip_address_of_your_pi

# Preparation

If you have not done so in a while run the following command to update your Pi.
This command updates repository information and then upgrades packages that are
installed on your Pi. If you did this already earlier in the instructions then
it is not necessary to do again.

    sudo apt update && sudo apt -y upgrade

# Getting Started

These instructions will install the Lighttpd webserver on your Pi

Install the Lighttpd webserver on your
Raspberry Pi as follows.

    sudo apt install lighttpd

Change to the web server root folder at /var/www/html

    cd /var/www/html

Create the symlinks for your folders to be viewable with the web server. Replace `username` with your account name.

    sudo ln -s /home/`username`/raspi-sump/web/index.html index.html
    sudo ln -s /home/`username`/raspi-sump/web/css css
    sudo ln -s /home/`username`/raspi-sump/web/images images
    sudo ln -s /home/`username`/raspi-sump/charts charts

Enable directory listing for historical charts

    sudo lighttpd-enable-mod dir-listing

Restart the web server

    sudo systemctl restart lighttpd

Open a web browser to http://ip_of_your_pi. Having configured the rsumpwebchart.timer earlier, a new webchart will be created every 15 minutes for viewing.
This will also copy historical information that you can access
from the link in the web page.

# Support

For support open an issue on the Github Issue Tracker or consider joining our discord server.

For Discord simply send an email to alaudet@linuxnorth.org and request an invite link.
