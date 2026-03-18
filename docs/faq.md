# FAQ

## Project Related

- [What is Raspi-Sump?](#what-is-raspi-sump)
- [What problem does Raspi-Sump solve?](#what-problem-does-raspi-sump-solve)
- [How much does it cost?](#how-much-does-it-cost)
- [Will it always be free?](#will-it-always-be-free)
- [What Python and OS versions are supported?](#what-python-and-os-versions-are-supported)
- [I would like to re-use the code to make a different program](#i-would-like-to-re-use-the-code-to-make-a-different-program)
- [I have a good idea for the application, can you add it?](#i-have-a-good-idea-for-the-application-can-you-add-it)
- [How can I get help?](#how-can-i-get-help)
- [How can I donate to the project?](#how-can-i-donate-to-the-project)

## Technical

- [Why is no data showing on the home page?](#why-is-no-data-showing-on-the-home-page)
- [I am not getting any depth readings](#i-am-not-getting-any-depth-readings)
- [Why am I getting multiple readings of 0?](#why-am-i-getting-multiple-readings-of-0)
- [I use the JSN-SR04T and get bad readings when the water is high](#i-use-the-jsn-sr04t-and-get-bad-readings-when-the-water-is-high)
- [I want alerts when the water level gets too low](#i-want-alerts-when-the-water-level-gets-too-low)
- [How do I reset my admin password?](#how-do-i-reset-my-admin-password)
- [The web interface shows a security warning in my browser](#the-web-interface-shows-a-security-warning-in-my-browser)
- [How do I change the GPIO pins?](#how-do-i-change-the-gpio-pins)
- [No readings after changing the reading interval](#no-readings-after-changing-the-reading-interval)
- [Why are my alerts not working?](#why-are-my-alerts-not-working)
- [How do I set the heartbeat alert to always arrive at the same time?](#how-do-i-set-the-heartbeat-alert-to-always-arrive-at-the-same-time)
- [What about power outages?](#what-about-power-outages)
- [Can the Pi control the pump directly?](#can-the-pi-control-the-pump-directly)
- [How do I import data from Raspi-Sump 1.x?](#how-do-i-import-data-from-raspi-sump-1x)
- [How do I back up my data?](#how-do-i-back-up-my-data)
- [Can I run Raspi-Sump without the web interface?](#can-i-run-raspi-sump-without-the-web-interface)
- [Where are the log files?](#where-are-the-log-files)
- [How do I report a bug?](#how-do-i-report-a-bug)

---

## Project Related

### What is Raspi-Sump?

Raspi-Sump is a water level monitoring system that uses an ultrasonic distance
sensor connected to the GPIO pins of a Raspberry Pi. It passively monitors the
water level and sends you an alert if the water exceeds a pre-defined level.

The program is written in Python and the source code is available on
[GitHub](https://github.com/alaudet/raspi-sump).

---

### What problem does Raspi-Sump solve?

Monitoring the water level of a sump pit requires you to be at that location.
Raspi-Sump allows you to monitor the level from anywhere with an internet
connection, and actively alerts you if there is a problem so you can address it
before there is a disaster.

---

### How much does it cost?

Raspi-Sump is free to use under the
[Apache 2.0 License](https://github.com/alaudet/raspi-sump/blob/main/LICENSE). The
source code is freely available to use, modify, and distribute as you see fit.

---

### Will it always be free?

Yes. Raspi-Sump will always remain free to use.

---

### What Python and OS versions are supported?

Raspi-Sump requires Python 3.11 or later and runs on Raspberry Pi OS Bookworm
(v12) or Trixie (v13) on any Raspberry Pi 2 or greater.

Support targets in-support versions of Raspberry Pi OS. It may work on
other ARM-based operating systems or boards (such as Orange Pi or Ubuntu ARM)
but these are not officially supported.

---

### I would like to re-use the code to make a different program

The [Apache 2.0 License](https://github.com/alaudet/raspi-sump/blob/main/LICENSE) allows this.

Please see the license details.

---

### I have a good idea for the application, can you add it?

Raspi-Sump is open source and contributions are welcome. There are
[contribution guidelines](https://github.com/alaudet/raspi-sump/blob/main/CONTRIBUTING.md)
to follow. Be clear about what you are proposing and why, make sure your code
works and is readable before submitting a pull request. Run the unit tests
before submitting — it is the first thing that will be checked.

If you are not sure whether something is worth pursuing, open an issue in the
[tracker](https://github.com/alaudet/raspi-sump/issues) to discuss it before writing any code.

---

### How can I get help?

- Report problems or find solutions on the [GitHub issue tracker](https://github.com/alaudet/raspi-sump/issues)
- Join the Discord group — [email for an invite](mailto:alaudet@linuxnorth.org?Subject=Raspi-Sump%20Discord%20Invite)

---

### How can I donate to the project?

See the [donation page](https://www.linuxnorth.org/donate/).

---

## Technical

### Why is no data showing on the home page?

The `raspisump` service is likely not running. Check the service status via
**gear icon → System Status** in the web interface, or from the command line:

```bash
sudo systemctl status raspisump
```

If it is not running, start it:

```bash
sudo systemctl start raspisump
```

Also verify that your configuration is correct — particularly `trig_pin`,
`echo_pin`, and `pit_depth` in `raspisump.conf`.

---

### I am not getting any depth readings

If the sensor signal is not being received, check `journalctl -u raspisump` or
the error log in `/var/log/raspi-sump/` for the following:

```
ERROR - Signal not received. Possible cable or sensor problem.
```

Check that the cable is firmly attached and that each pin is connected to the
correct GPIO pin as configured in `raspisump.conf`. Check the sensor for
corrosion. You can test the sensor directly on the comman line with:

```bash
pinsource -t trigpin -e echopin
```

Replace `trigpin` and `echopin` with the BCM GPIO numbers you are using.

---

### Why am I getting multiple readings of 0?

This is almost always a failing sensor. Raspi-Sump corrects negative values to
0 to keep charts readable, so a sensor throwing high negative values shows up
as repeated zeros. Check for corrosion on the sensor and replace it if
necessary.

---

### I use the JSN-SR04T and get bad readings when the water is high

The JSN-SR04T v2.0 has a minimum sensing distance of approximately 20 cm (8
inches). If the water level gets within that range of the sensor it will return
bad readings. Try mounting the sensor slightly higher if possible, and adjust
`pit_depth` in `raspisump.conf` to match the new position — that value is the
distance from the sensor face to the bottom of the pit.

---

### I want alerts when the water level gets too low

Raspi-Sump can monitor for low water levels as well as high — useful for
cisterns or tanks. In `raspisump.conf` change:

```ini
alert_when = high
```

to:

```ini
alert_when = low
```

Adjust `critical_water_level` accordingly. Alerts will be worded for low water
conditions.

---

### How do I reset my admin password?

Log in to the web interface and go to **gear icon → Security**. Enter a new
password in the admin password fields and save.

If you are locked out entirely, edit `/etc/raspi-sump/credentials.conf`
directly and set:

```ini
[web]
admin_password = admin
```

Then restart the `rsumpweb` service. The first-run setup wizard will appear on
next browser visit and prompt you to set a new password.

---

### The web interface shows a security warning in my browser

This is expected. The TLS certificate is self-signed. Accept the browser
exception to proceed — the connection is still encrypted.

---

### How do I change the GPIO pins?

Edit `raspisump.conf` via **gear icon → Configuration** and update `trig_pin`
and `echo_pin` to your chosen BCM GPIO numbers. Restart the `raspisump`
service for the change to take effect.

---

### No readings after changing the reading interval

Restart the `raspisump` service after changing `reading_interval`:

```bash
sudo systemctl restart raspisump
```

Or use the restart button on **gear icon → System Status**.

---

### Why are my alerts not working?

Check the following:

- Are the server configuration details correct in `raspisump.conf`?
- Are the credentials correct in `credentials.conf`?
- If using Gmail, are you using an App Password? Google requires app passwords
  when two-factor authentication is enabled. See
  [Signing in with App Passwords](https://support.google.com/mail/answer/185833).
- If using Mastodon, are the OAuth2 settings configured correctly in
  `credentials.conf`?

Run `alerttest` from the command line to see error output. If problems persist,
open an issue in the [GitHub tracker](https://github.com/alaudet/raspi-sump/issues).

---

### How do I set the heartbeat alert to always arrive at the same time?

Set `heartbeat_interval` to match your desired frequency (in minutes):

```ini
# daily   = 1439 minutes
# weekly  = 10079 minutes
# monthly = 43199 minutes
heartbeat_interval = 1439
```

To pin the start time, check `/var/log/raspi-sump/heartbeat_log` for the last heartbeat time entry and change to the time you want to receive heartbeat notices. 

Then save the file. 

---

### What about power outages?

A battery backup (UPS) is essential for both the Pi and your internet
modem/router. With a UPS, alerting should continue through short outages. A
mobile data connection is another option, a USB data plan and pi plugged into a UPS
would allow the Pi to send alerts even if the home network goes down, though
that requires configuration on your part and is beyond the scope of Raspi-Sump.

Remember that Raspi-Sump is one layer of protection. It cannot start a failed
pump or supply power. A backup pump and generator are important infrastructure
to have in place first.

---

### Can the Pi control the pump directly?

Technically possible, but strongly not recommended. Mechanical float devices
are reliable for a reason. Raspi-Sump is and will always be a **passive**
monitoring system. A software or hardware failure on the Pi should never be the
reason a pump does not start.

---

### How do I import data from Raspi-Sump 1.x?

See the [Upgrading](upgrade.md) guide for full instructions. The short version:

```bash
rsumpimport --dir ~/raspi-sump-backup/ --unit metric
```

Or use the web interface: **gear icon → Import/Export CSV**.

---

### How do I back up my data?

Use **gear icon → Backup/Export** in the web interface. This downloads a zip
file containing the SQLite database and `raspisump.conf`.

---

### Can I run Raspi-Sump without the web interface?

Yes. The `raspisump` and `rsumpweb` services are independent. Stop `rsumpweb`
if you do not need the web interface:

```bash
sudo systemctl stop rsumpweb
sudo systemctl disable rsumpweb
```

The monitoring daemon (`raspisump`) will continue running and logging readings.

---

### Where are the log files?

| Log | Location |
|-----|----------|
| Service logs | `journalctl -u raspisump` / `journalctl -u rsumpweb` |
| Error log | `/var/log/raspi-sump/` |
| Database | `/var/lib/raspi-sump/raspisump.db` |

---

### How do I report a bug?

Run `rsumpsupport` to generate a support file:

```bash
rsumpsupport
```

On the web interface, **gear icon → Support**.  There is an option to download the support file directly to your computer.

Then open an issue in the
[issue tracker](https://github.com/alaudet/raspi-sump/issues) and attach the
support file.
