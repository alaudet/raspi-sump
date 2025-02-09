# Raspi-Sump v1.10 Installation Instructions

Installation instructions assume Python3 on Raspberry Pi OS 12 (Bookworm)

# Supported OS Versions

Raspberry Pi OS 12 (Bookworm) and Raspberry Pi OS 11 (Bullseye)

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

Now that your hardware is setup and properly connected to the gpio pins, login to your Raspberry Pi.

Check that your user account is a member of the gpio group. This is needed for accessing the gpio pins.

    groups

You should see all groups your account belongs to. If gpio is not listed run the following command ($USER will be replaced with your account name);

    sudo usermod -aG gpio $USER

Logout and log back into your account for the groups to take effect.

Install Pip, RPi.GPIO, Matplotlib and Virtualenv

    sudo apt update && sudo apt -y upgrade

    sudo apt install python3-pip python3-rpi.gpio python3-matplotlib python3-virtualenv

RPi.GPIO is the library that controls the sensor.

Matplotlib is used to generate charts.

The Pip package manager is required to install Raspi-Sump in the next step.

Virtualenv is needed to install a virtual environment that will host the Raspi-Sump and hcsr04sensor libraries. This helps segragate custom libraries from the system wide python libraries which is a new requirement with the latest Python on Raspberry Pi OS 12 (Bookworm)

# Install Raspi-Sump

If you are running version 1.9 you must uninstall it first. You will not lose any of your configurations.

    sudo pip3 uninstall raspisump hcsr04sensor

Create a virtual environment called `raspi-sump` in the /opt folder. Raspi-sump will no longer install to the /usr/local/bin and python system folder areas. Everything will be contained within this new virtual environment. The environment will be using the system wide libraries for RPi.GPIO and Matplotlib as usual.

    cd /opt/
    sudo virtualenv --system-site-packages raspi-sump

Give your user write access to the new environment.

    sudo chown -R $USER raspi-sump

Switch to newly created virtualenv

    source raspi-sump/bin/activate

You will notice that your prompt now has the name of the raspi-sump virtualenv in it, which indicates that it is active.

`(raspi-sump) username@hostname~ $`

The following will automatically install hcsr04sensor if it is not already installed on your Pi. We are not using sudo here because we gave our user account permissions to install to the virtual environment.

    pip3 install --no-binary :all: raspisump

NOTE\*\*\* You will see some depracation warnings from pip, don't worry as these will be addressed in a future release. Proceed with configuration....

Once the install is complete you can deactivate the virtual environment as follows.

    deactivate

Your cursor will now return to normal and you may proceed with configuration.

`username@hostname:~ $`

## Add the newly created /opt/raspi-sump/bin folder to your Path.

This will be important for later to easily access other utilities related to support and email health check.

    nano ~/.bashrc

Scroll to the end of the file and add this command. Save and exit the .bashrc file.

    export PATH="/opt/raspi-sump/bin:$PATH"

Logout and back in to initiate the new path.

\*\* Note you can check your path by typing in the following command to verify that /opt/raspi-sump/bin is added;

    $PATH

## Configure Raspi-Sump

Navigate to /home/$USER/raspi-sump/ and move the sample config file
to this directory.

    cd /home/$USER/raspi-sump
    mv sample_config/raspisump.conf .

The /home/$USER/raspi-sump folder is setup as follows on install;

- raspi-sump/sample_config/raspisump.conf (all configurations for raspisump).
- raspi-sump/csv (location of waterlevel readings to csv file)
- raspi-sump/charts (location of charts if using rsumpchart.py)
- raspi-sump/logs (location of rsumpmonitor.py logs if using raspisump as a continuous process)
- raspi-sump/web (all files needed for the optional pi webserver install)
- "depracated" raspi-sump/cron (example crontab for scheduling readings)

  - NOTE that cron has been replaced with systemd.

\*\*Note take care with your raspisump.conf file if you are using Gmail or any
other mail system that requires authentication. Your username and password
will be viewable in the file. You should have a strong password on your account.. The installer also tightens file security on
the file automatically.

# Edit raspisump.conf

All configurations are recorded in /home/$USER/raspi-sump/raspisump.conf

See the configuration file for explanations of variables. You can choose to
take imperial (inches) or metric (centimetres) water level readings.

# Configure Raspi-Sump to use Systemd

Enable lingering. This will ensure the raspisump service you configure on the next step will remain running when you are logged out. This only needs to be done once.

    sudo loginctl enable-linger $USER

Reboot the pi to ensure logind has activated lingering.

        sudo reboot

To start Raspi-Sump you will need to enable it with systemd. The first time you install Raspi-Sump you will need to run this command for systemd to find the service files located in /home/$USER/.config/systemd/user

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

    ** If you did not add /opt/raspi-sump/bin to your path as mentioned earlier you can type the full location of the command

    /opt/raspi-sump/bin/emailtest

### Heartbeat Alerts

Raspi-Sump can send email tests at predefined intervals. See the raspisump.conf file option 'heartbeat' and 'heartbeat_interval'.

In /home/$USER/raspi-sump/raspisump.conf, this section configures the email heartbeat once per week.

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

Ensure that the web server can access your home folder location. Failing to do so could cause 403 Errors when trying to access the web page on the pi.

    chmod o+x /home/$USER

Create the symlinks for your folders to be viewable with the web server. $USER will be replaced with your account name.

    sudo ln -s /home/$USER/raspi-sump/web/index.html index.html
    sudo ln -s /home/$USER/raspi-sump/web/css css
    sudo ln -s /home/$USER/raspi-sump/web/images images
    sudo ln -s /home/$USER/raspi-sump/charts charts

Enable directory listing for historical charts

    sudo lighttpd-enable-mod dir-listing

Restart the web server

    sudo systemctl restart lighttpd

Open a web browser to http://ip_of_your_pi. Having configured the rsumpwebchart.timer earlier, a new webchart will be created every 15 minutes for viewing.
This will also copy historical information that you can access
from the link in the web page.

# Optional - Make it Easier to initiate systemd commands

If you find typing the systemctl commands cumbersome you can make it easier by creating aliases. An alias is shortcut you can type that will initiate a long command.

Aliases are added to the `.bash_aliases` file in your home folder as follows

        cd /home/$USER
        nano .bash_aliases

Copy and paste the following aliases for Raspi-Sump `systemd` commands in the file. Make sure there are no spaces at the beginning of each line after pasting.

        alias sumpstart="systemctl --user start raspisump && systemctl --user start rsumpwebchart.timer"
        alias sumpstop="systemctl --user stop raspisump && systemctl --user stop rsumpwebchart.timer"
        alias sumpstatus="systemctl --user status raspisump"
        alias sumpchartstatus="systemctl --user status rsumpwebchart.timer"
        alias sumpenable="systemctl --user enable raspisump && systemctl --user enable rsumpwebchart.timer"
        alias sumpdisable="systemctl --user disable raspisump && systemctl --user disable rsumpwebchart.timer"
        alias sumprestart="systemctl --user restart raspisump"

Save the file, logout and log back in to activate the new aliases.

- Start raspisump and rsumpwebchart.timer

        sumpstart

- Stop raspisump and rsumpwebchart.timer

        sumpstop

- Show status of the raspisump service

        sumpstatus

- Show status of the rsumpwebchart timer

        sumpchartstatus

- Enable raspisump and rsumpchart.timer on boot

        sumpenable

- Disable raspisump and rsumpchart.timer on boot

        sumpdisable

- Restart raspisump after making a `raspisump.conf` file change

        sumprestart

# Support

For help with any issues that may arise, run the following command;

    rsumpsupport

    ** If you did not add /opt/raspi-sump/bin to your path as mentioned earlier you can type the full location of the command

    /opt/raspi-sump/bin/rsumpsupport

This will create a file `support_date_time.txt` in the `/home/__username__/raspi-sump/support` directory that can be attached to a support request.

This text file will provide key information to diagnose any issues when requesting support. There is no sensitive information in the file except the name of the /home/user folder. If you are uncomfortable posting this info you can email it to me instead.

For support open an issue on the Github Issue Tracker or consider joining our discord server.

For Discord simply send an email to alaudet@linuxnorth.org and request an invite link.
