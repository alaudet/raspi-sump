# Fresh Install

## Prerequisites

- Raspberry Pi 2 or greater running **Raspberry Pi OS Bookworm (v12) or Trixie (v13)**
- A compatible ultrasonic distance sensor (see below)
- A voltage divider cable to reduce the echo pin signal from 5V to 3.3V
- Internet access on the Pi for the initial package install

### Supported Sensors

Raspi-Sump works with the **HC-SR04** and compatible sensors, including the
**JSN-SR04T v2.0** waterproof variant which is recommended for sump pit use.

!!! danger "JSN-SR04T v3.0 — Do not use"
    Version 3.0 of the JSN-SR04T uses a different communication protocol and
    is **not compatible** with Raspi-Sump. Always verify you are purchasing
    the v2.0 variant before ordering.

### Voltage Divider Requirement

The HC-SR04 and JSN-SR04T sensors operate at **5V** and return a 5V signal on
the echo pin. The Raspberry Pi GPIO pins are **3.3V tolerant only** — connecting
a 5V echo signal directly will damage your Pi.

A voltage divider on the echo pin is required to reduce the signal to a safe
3.3V level. A simple two-resistor divider works well:

- **R1:** 1kΩ (between sensor echo and GPIO pin)
- **R2:** 2kΩ (between GPIO pin and ground)

This divides the 5V echo signal to approximately 3.3V before it reaches the
GPIO pin. Pre-made voltage divider cables are available from many electronics
suppliers and are the simplest option for new users.

The trig pin (Pi → sensor) does not require a divider — 3.3V is sufficient
to trigger the sensor.

---

## Add the Linuxnorth APT Repository

Raspi-Sump is distributed via the Linuxnorth APT repository.

!!! warning "Alpha channel"
    The repository is currently serving alpha releases on the `unstable` channel.
    Use on a production system at your own risk.

### 1. Import the signing key

```bash
curl -fsSL https://apt.linuxnorth.org/public_key.asc \
  | sudo gpg --dearmor -o /usr/share/keyrings/linuxnorth-archive-keyring.gpg
```

### 2. Add the repository

```bash
echo "deb [signed-by=/usr/share/keyrings/linuxnorth-archive-keyring.gpg] \
  https://apt.linuxnorth.org unstable main" \
  | sudo tee /etc/apt/sources.list.d/linuxnorth.list
```

### 3. Install

```bash
sudo apt update
sudo apt install raspisump
```

The installer creates the `raspisump` system user, sets up directories and
permissions, generates a self-signed TLS certificate, and installs the
systemd services.

!!! important "Log out and back in after install"
    The installer adds your user account to the `raspisump` group so you can
    run manual commands without `sudo`. This group membership does not take
    effect until you log out and log back in to your Pi session.

---

## Configure nginx

The raspisump package automatically enables its nginx configuration and
removes the default nginx site during install. No manual nginx configuration
is required.

---

## First-Run Setup

After install, the `rsumpweb` service starts automatically. Open a browser and
navigate to:

```
https://<your-pi-ip>
```

!!! note "Self-signed certificate"
    Your browser will show a security warning because the TLS certificate is
    self-signed. This is expected on a LAN appliance. Accept the exception to
    proceed.

The first-run setup wizard will appear. It guides you through:

- Setting your admin password
- Configuring pit measurements (depth, critical level, units)
- Choosing your alert type (email or Mastodon)
- Setting the GPIO pins for your sensor
- Setting the reading interval and temperature

On completion, the wizard writes the configuration files and starts the
`raspisump` monitoring service automatically.

---

## Verify the Install

The easiest way to verify both services are running is via the web interface:
**gear icon → System Status**. Both `raspisump` and `rsumpweb` should show as
active.

Alternatively, from the command line:

```bash
sudo systemctl status raspisump
sudo systemctl status rsumpweb
```

The web interface home page will begin showing readings within one reading interval.

---

## Log Out of the Setup Wizard Session

After setup is complete, log out of the admin session via the gear icon in
the top navigation bar.

---

## Reporting Issues

Please report any problems in the
[issue tracker](https://github.com/alaudet/raspi-sump/issues).
