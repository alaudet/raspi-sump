# Raspi-Sump

Raspi-Sump is a sump pit water level monitoring system for the Raspberry Pi. It uses an ultrasonic sensor to continuously measure water depth, logs all readings to a local SQLite database, sends email or Mastodon alerts if the water reaches a critical level, and provides a built-in web interface for monitoring and administration.

![Homepage screenshot](betatesting/screenshots/homepage%20dark.png)

---

## Features

- Continuous water level monitoring at configurable intervals
- Email and/or [Mastodon](https://joinmastodon.org/) alerts when water reaches a critical level
- Heartbeat notifications to confirm the system is running
- Secure HTTPS web interface (self-signed certificate, nginx + Flask)
- Interactive charts with dark mode support
- Historical readings with single-day, multi-day, and custom date range views
- Admin panel: service control, configuration editor, backup/export, CSV import, support tools
- Installed as a standard Debian package — no virtual environment required
- systemd services with automatic startup

---

## Supported Hardware

- Raspberry Pi 2, 3, 4, and 5
- Ultrasonic sensors: HC-SR04, JSN-SR04T (waterproof, recommended)

---

## Supported OS

| OS | Architecture |
|---|---|
| Raspberry Pi OS 13 (Trixie) | 32-bit and 64-bit |
| Raspberry Pi OS 12 (Bookworm) | 32-bit and 64-bit |

Raspi-Sump follows the [Debian release schedule](https://wiki.debian.org/DebianReleases). Older OS versions are not supported.

---

## What's New in Version 2.0

Version 2.0 is a complete rewrite:

- Installed as a `.deb` package — no virtual environment, no manual dependency management
- SQLite database replaces per-day CSV files
- Full HTTPS web interface with dark mode, interactive charts (uPlot), and a mobile-friendly layout
- Admin panel with service control, config editor, backup/restore, CSV import/export, and support tools
- Persistent admin login with 30-day session cookie
- Mastodon DM alerts as an alternative or complement to email
- FHS-compliant paths (`/etc/raspi-sump/`, `/var/log/raspi-sump/`, `/var/lib/raspi-sump/`)
- systemd services for both the monitor and web interface

See the [changelog](https://github.com/alaudet/raspi-sump/blob/master/debian/changelog) for full details.

---

## Install

See the [install guide](https://github.com/alaudet/raspi-sump/blob/master/docs/install.md).

---

## Upgrade

See the [upgrade guide](https://github.com/alaudet/raspi-sump/blob/master/docs/upgrade.md).

---

## More Info

[https://www.linuxnorth.org/raspi-sump/](https://www.linuxnorth.org/raspi-sump/)

---

## Community

- **Discord** — discuss and get support from other users. Email [alaudet@linuxnorth.org](mailto:alaudet@linuxnorth.org) for an invite link.
- **Issue tracker** — [GitHub Issues](https://github.com/alaudet/raspi-sump/issues)

---

## Disclaimer

Raspi-Sump is a passive monitoring tool. It does not control your pump and cannot prevent flooding. There is no warranty. See the license for details.

Best practices:

- Install a backup pump that triggers at a slightly higher water level than your primary pump
- Connect the backup pump to a separate dedicated electrical breaker
- Have an alternate power source (generator or battery backup) for extended outages during spring thaw or severe weather
- If building a new home, consider lot grading that allows gravity drainage — use a pump and Raspi-Sump as a backup layer

---

## License

Version 2.0 is released under the [Apache 2.0 License](https://github.com/alaudet/raspi-sump/blob/master/LICENSE).

Version 1.x was released under the MIT License.

---

## Contributing

Please read the [Contributing Guidelines](https://github.com/alaudet/raspi-sump/blob/master/CONTRIBUTING.md) before submitting a pull request.

---

## Donate

[Your support is appreciated](https://www.paypal.com/donate/?hosted_button_id=7DLCUXLC5TQSA)
