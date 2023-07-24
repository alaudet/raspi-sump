#!/usr/bin/env python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

from raspisump import checkpid, log


def main():
    """run checkpid.py module to restart Raspi-Sump if the rsump.py process is
    stopped or has spawned multiple processes."""
    process = "/usr/local/bin/rsump.py"
    checkpid.check_pid(process)


if __name__ == "__main__":
    print("rsumpmonitor.py is depracated.  Switch to systemd.")
    print("https://github.com/alaudet/raspi-sump/blob/master/docs/upgrade_systemd.md")
    log.log_event(
        "info_log",
        "Deprecation Warning - rsumpmonitor.py is depracated. Switch to systemd",
    )
    main()
