# Upgrade to Raspi-Sump Version 9 instructions.

These instructions are for upgrading versions 1.8 and lower to version 1.9. If you are doing a new install, disregard these instructions and use the [Raspi-Sump New Install Instructions](https://github.com/alaudet/raspi-sump/blob/master/docs/install.md) instead.

# Upgrade Raspi-Sump to use Systemd

Raspi-Sump version 1.9 and later use `systemd` to manage the services related to sump monitoring and chart creation.

`Systemd` replaces cron scheduling for taking readings and creating charts on a schedule. It also replaces `rsumpmonitor.py` for monitoring the status of the raspisump process when taking more than one reading per minute.

`Systemd` will automatically restart the Raspi-Sump process if it stops and is a more robust way to handle failed processes than `rsumpmonitor.py`.

## If you currently take readings once per minute or more

If you currently call `rsump.py` with cron every minute or more and are happy with this approach you can continue doing this. Nothing changes for you. However `systemd` makes it easier to stop and start processes.

e.g. If `reading_interval = 0` in your `raspisump.conf` file and you use cron to call rsump.py every minute or more, you do not need to use `systemd`. It is recommended to switch but Raspi-Sump will continue working as normal.

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

Copy and paste the following aliases for Raspi-Sump `systemd` commands in the file.

        alias sumpon="systemctl --user start raspisump && systemctl --user start rsumpwebchart.timer"
        alias sumpoff="systemctl --user stop raspisump && systemctl --user stop rsumpwebchart.timer"
        alias sumpstats="systemctl --user status raspisump"
        alias sumpchartstats="systemctl --user status rsumpwebchart.timer"
        alias sumpboot="systemctl --user enable raspisump && systemctl --user enable rsumpwebchart.timer"
        alias sumpnoboot="systemctl --user disable raspisump && systemctl --user disable rsumpwebchart.timer"
        alias sumprestart="systemctl --user restart raspisump"

Save the file, logout and log back in to activate the new aliases.

- Start raspisump and rsumpwebchart.timer

        sumpon

- Stop raspisump and rsumpwebchart.timer

        sumpoff

- Show status of the raspisump service

        sumpstats

- Show status of the rsumpwebchart timer

        sumpchartstats

- Enable raspisump and rsumpchart.timer on boot

        sumpboot

- Disable raspisump and rsumpchart.timer on boot

        sumpnoboot

- Restart raspisump after making a `raspisump.conf` file change

        sumprestart
