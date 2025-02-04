# Upgrading Versions (v1.10)

The following instructions will help you upgrade Raspi-Sump from version 1.10 to later decimal and major versions.

Raspi-Sump now creates a virtualenv in `/opt/raspi-sump/`.
It will be necessary to enter the virtual environment to perform the upgrade process.

## Step 1

Activate the virtual environment;

    source /opt/raspi-sump/bin/activate

Your cursor will now look as follows;

`(raspi-sump) username@hostname:~ $`

The `(raspi-sump)` portion identifies an active virtual environment.

## Step 2

Perform the upgrade;

    pip3 install -U --no-binary :all: raspisump

NOTE\*\*\* You will see some depracation warnings from pip, don't worry as these will be addressed in a future release. Proceed with configuration....

Once the install is complete you can deactivate the virtual environment as follows.

    deactivate

Your cursor will now return to normal and you may proceed with configuration.

`username@hostname:~ $`

## Step 3

Reload the systemd user daemon

     systemctl --user daemon-reload

## Step 4

Check to make sure raspi-sump and resumpwebchart.timer are running

    systemctl --user status raspisump
    systemctl --user status rsumpwebchart.timer

You are looking for the following line to show that the service is active;

`Active: active (running) since Tue 2025-01-28 09:55:34 EST; 1 weeks 0 days ago
`

## Support

For help with any issues that may arise, run the following command;

    rsumpsupport

    ** If you did not add /opt/raspi-sump/bin to your path as mentioned in the install instructions you can type the full location of the command

    /opt/raspi-sump/bin/rsumpsupport

This will create a file `support_date_time.txt` in the `/home/__username__/raspi-sump/support` directory that can be attached to a support request.

This text file will provide key information to diagnose any issues when requesting support. There is no sensitive information in the file except the name of the /home/user folder. If you are uncomfortable posting this info you can email it to me instead.

For support open an issue on the Github Issue Tracker or consider joining our discord server.

For Discord simply send an email to alaudet@linuxnorth.org and request an invite link.
