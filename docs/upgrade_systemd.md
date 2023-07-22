# Upgrade Raspi-Sump to use Systemd

Raspi-Sump versions after 1.8 use systemd to manage the services related to sump monitoring and chart creation.

`Systemd` replaces cron scheduling for taking readings, creating charts on a schedule. It also replaces `rsumpmonitor.py` for monitoring the status of the raspisump process when taking more than one reading per minute.

`Systemd` will automatically restart the Raspi-Sump process if it stops and is a more robust way to handle failed processes the `rsumpmonitor.py`.

## If you currently take readings once per minute or more

If you currently call `rsump.py` with cron every minute or more and are happy with this approach you can continue doing this. Nothing changes for you. However `systemd` makes it easier to stop and start processes.

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

- Start the chart generation timer

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

When you make changes to the raspisump.conf file you must restart the raspisump service

        systemctl --user restart raspisump
