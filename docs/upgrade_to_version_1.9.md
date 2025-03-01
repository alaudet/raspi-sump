# **_ These Instructions are now deprecated in favour of version 1.10. _**

You should be installing version 1.10 at this point, but I will leave these instructions here for historical purposes for the next while.

# Upgrade to Raspi-Sump Version 1.9 instructions.

These instructions are for upgrading versions 1.8 and lower to version 1.9. If you are doing a new install, disregard these instructions and use the [Raspi-Sump New Install Instructions](https://github.com/alaudet/raspi-sump/blob/master/docs/install.md) instead.

# Upgrade Raspi-Sump to use Systemd

Raspi-Sump version 1.9 and later use `systemd` to manage the services related to sump monitoring and chart creation.

`Systemd` replaces cron scheduling for taking readings and creating charts on a schedule. It also replaces `rsumpmonitor.py` for monitoring the status of the raspisump process when taking more than one reading per minute.

`Systemd` will automatically restart the Raspi-Sump process if it stops and is a more robust way to handle failed processes than `rsumpmonitor.py`.

## If you currently take readings once per minute or more

If you currently call `rsump.py` with cron every minute or more and are happy with this approach you can continue doing this. Nothing changes for you. However `systemd` makes it easier to stop and start processes. Some people are militant about deprecating cron in favour of systemd but cron is proven and works well in this situation. Nothing wrong with continuing to use as is.

e.g. If `reading_interval = 0` in your `raspisump.conf` file and you use cron to call rsump.py every minute or more, you do not need to use `systemd`. It is an option to switch but Raspi-Sump will continue working as normal fine with cron when only taking one reading and exiting.

# Setting up Systemd

## Upgrade to the latest version

Upgrade to the latest version of Raspi-Sump

    sudo pip3 install -U --no-binary :all: raspisump

## Disable cron entries

Remove any entries from your crontab

    crontab -e

Add a `#` before each entry that calls a raspisump process.

    # */1 * * * * /usr/local/bin/rsump.py &> /dev/null
    # 59 * * * * /usr/local/bin/rsumpwebchart.py &> /dev/

    # */5 * * * * /usr/local/bin/rsumpmonitor.py &> /dev/null

Save the crontab

## Configure Systemd

Enable lingering. This will ensure the raspisump service you configure on the next step will remain running when you are logged out. This only needs to be done once.

    sudo loginctl enable-linger $USER

Reboot the pi to ensure logind has activated lingering.

    sudo reboot

In your `raspisump.conf` file, set the `reading_interval` time to the interval in seconds that Raspi-Sump should take a reading.

    reading_interval = 60

Save the `raspisump.conf` file

One time only \*\* - Activate the services

        systemctl --user daemon-reload

### Starting and Enabling Services

- Start the raspisump service

        systemctl --user start raspisump

- Force the raspisump service to activate after a reboot

        systemctl --user enable raspisump

- Start the chart generation timer. Charts will generate every 15 minutes.

        systemctl --user start rsumpwebchart.timer

- Force the timer to activate after a reboot

        systemctl --user enable rsumpwebchart.timer

### Stopping and Disabling Services

There are times you may want to stop the raspisump service or the rsumpwebchart.timer.

- Stopping the services

        systemctl --user stop raspisump
        systemctl --user stop rsumpwebchart.timer

- Disabling the services to prevent their startup after a reboot

        systemctl --user disable raspisump
        systemctl --user disable rsumpmonitor.timer

### Restarting the raspisump service

When you make changes to the `raspisump.conf` file you must restart the raspisump service

        systemctl --user restart raspisump

### Check the status of the services

You can check the status of the raspisump service and rsumpwebchart timer as follows;

        systemctl --user status raspisump
        systemctl --user status rsumpwebchart.timer

# Making it easier to call systemctl

If you find typing the systemctl commands cumbersome you can make it easier by creating aliases. An alias is shortcut you can type that will initiate a long command.

Aliases are added to the `.bash_aliases` file in your home folder as follows

        cd /home/__username__
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

This will create a file `support_date_time.txt` in the `/home/__username__/raspi-sump/support` directory that can be attached to a support request.

For support open an issue on the Github Issue Tracker or consider joining our discord server.

For Discord simply send an email to alaudet@linuxnorth.org and request an invite link.
