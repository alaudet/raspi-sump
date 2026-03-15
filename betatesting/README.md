# Raspi-Sump Beta Testing Guide

**Version: 2.0a51**

Thank you for helping test Raspi-Sump 2.0. This is a complete rewrite targeting
Raspberry Pi OS Trixie and Bookworm. Feedback on installation, usability, and
bugs is very much appreciated.

---

## Prerequisites

- Raspberry Pi running **Raspberry Pi OS Trixie or Bookworm** (32-bit or 64-bit)
- HC-SR04 ultrasonic sensor wired to the GPIO pins defined in `raspisump.conf`
- Internet access during install (to download packages)

---

## Screenshots

Screenshots of the web interface are available in the [screenshots folder](screenshots/README.md).

---

## Download

The packages are not yet in an APT repository. Download the `.deb` files directly:

| Package | Link |
|---|---|
| `python3-pinsource` | [python3-pinsource_0.0.4~a1_all.deb](https://github.com/alaudet/raspi-sump/raw/V2/betatesting/python3-pinsource_0.0.4~a1_all.deb) |
| `raspisump` | [raspisump_2.0~a51_all.deb](https://github.com/alaudet/raspi-sump/raw/V2/betatesting/raspisump_2.0~a51_all.deb) |

---

## Removing a Legacy Raspi-Sump Installation

If you have an older raspi-sump (1.x) installed in a Python virtual environment,
remove it before installing the new package.

**1. Remove the old Python packages from the virtual environment:**

```bash
source ~/raspi-sump-venv/bin/activate
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
sudo apt-get remove --purge lighttpd
```

**4. Remove any old cron jobs:**

```bash
crontab -e
```

Remove any lines referencing `rsump`, `rsumpmonitor`, or `rsumpwebchart`.

---

## Fresh Install

**1. Install the pinsource dependency first:**

```bash
sudo dpkg -i python3-pinsource_*.deb
sudo apt-get install -f
```

**2. Install raspisump:**

```bash
sudo dpkg -i raspisump_*.deb
sudo apt-get install -f
```

The installer will:
- Create the `raspisump` system user and set up all required directories
- Install nginx and configure it for HTTPS with a self-signed certificate
- Copy default config files to `/etc/raspi-sump/`
- Enable `raspisump.service` and `rsumpweb.service`

**3. Log out and back in:**

Your user account is added to the `raspisump` group during install. You need to
log out and back in for this to take effect.

**4. Edit the configuration:**

```bash
sudo nano /etc/raspi-sump/raspisump.conf
```

Key settings to review:

| Setting | Description |
|---|---|
| `trig_pin` | GPIO pin number for HC-SR04 trigger |
| `echo_pin` | GPIO pin number for HC-SR04 echo |
| `pit_depth` | Total depth of your pit in cm (or inches) |
| `critical_water_level` | Water depth that triggers an alert |
| `unit` | `metric` (cm) or `imperial` (inches) |
| `alert_type` | `1` = email, `2` = Mastodon, `3` = both |

**5. Set the admin password:**

```bash
sudo nano /etc/raspi-sump/credentials.conf
```

Set the `password` field under `[web]` to your chosen admin password. This
protects the Administration section of the web interface.

**6. Start the service:**

```bash
sudo systemctl start raspisump.service
```

**7. Access the web interface:**

Open a browser and go to:

```
https://<your-pi-ip>/
```

Accept the browser warning for the self-signed certificate. The web interface
shows live water level data and provides administration tools.

---

## Upgrading

To upgrade to a newer beta release:

**1. Download the new `.deb` files.**

**2. Install over the existing version:**

```bash
sudo dpkg -i python3-pinsource_*.deb raspisump_*.deb
sudo apt-get install -f
```

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
