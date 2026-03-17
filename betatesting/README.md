# Raspi-Sump Beta Testing Guide

## Prerequisites

- Raspberry Pi running **Raspberry Pi OS Trixie or Bookworm** (32-bit or 64-bit)
- HC-SR04 ultrasonic sensor (or compatible) wired to the GPIO pins (wire or breadboard) defined in `raspisump.conf`
- Internet access during install (to download packages)

---

## Screenshots

Screenshots of the web interface are available in the [screenshots folder](screenshots/README.md).

---

## Removing a Legacy Raspi-Sump Installation

If you have an older raspi-sump (1.x) installed in a Python virtual environment,
remove it before installing the new package.

**1. Remove the old Python packages from the virtual environment:**

```bash
source /opt/raspi-sump/bin/activate
pip uninstall raspisump hcsr04sensor
deactivate
```

If you used a different virtual environment path, adjust accordingly.

**2. Archive the old raspi-sump directory:**

```bash
mv /home/$USER/raspi-sump /home/$USER/raspi-sump.archive
```

This preserves your old config and logs in case you need to refer back to them.

**3. Remove lighttpd if installed:**

Raspi-Sump uses nginx. If lighttpd is running it will conflict on port 80.

```bash
sudo systemctl stop lighttpd
sudo apt remove --purge lighttpd
```

**4. Remove any old cron jobs:**

```bash
crontab -e
```

Remove any lines referencing `rsump`, `rsumpmonitor`, or `rsumpwebchart` and save.

---

## Alpha install

Alpha releases are available via the Linuxnorth APT repository. This is an
unstable channel intended for testers — use on a production system at your own risk.

You must remove any previous versions of Raspi-Sump or hcsr04sensor before doing this.  If you are not sure what to do ask in the Issue Tracker.

```bash
# 1. Import the signing key
curl -fsSL https://apt.linuxnorth.org/public_key.asc \
  | sudo gpg --dearmor -o /usr/share/keyrings/linuxnorth-archive-keyring.gpg

# 2. Add the repository
echo "deb [signed-by=/usr/share/keyrings/linuxnorth-archive-keyring.gpg] \
  https://apt.linuxnorth.org unstable main" \
  | sudo tee /etc/apt/sources.list.d/linuxnorth.list

# 3. Install
sudo apt update
sudo apt install raspisump
```

Please report issues in the [issue tracker](https://github.com/alaudet/raspi-sump/issues).


**3. Log out and back in:**

Your user account is added to the `raspisump` group during install. You need to
log out and back in for this to take effect.



**4. Edit the configuration:**

Access the config at https://<ip of your pi>

Accept the browser warning for the self-signed certificate. The web interface
shows live water level data and provides administration tools.

---

Your configuration files (`raspisump.conf`, `credentials.conf`) are never
overwritten during an upgrade. Updated example configs are placed at:

```
/usr/share/raspi-sump/examples/raspisump.conf
/usr/share/raspi-sump/examples/credentials.conf
```

Review the examples after each upgrade for any new settings.

Services are restarted automatically at the end of the upgrade.

---

## Reporting Issues

Please report bugs and feedback via GitHub or Discord:

**GitHub issue trackers:**
- Raspi-Sump: https://github.com/alaudet/raspi-sump/issues
- Pinsource: https://github.com/alaudet/pinsource/issues

**Discord:** If you are a member of the Raspi-Sump Discord group you can report
issues there and they will be imported to GitHub.

When reporting a bug, please attach a support file generated from the web interface:

**Administration → Support → Generate & Download Support File**

This captures your system configuration, service status, and recent logs without
including passwords or sensitive credentials.
