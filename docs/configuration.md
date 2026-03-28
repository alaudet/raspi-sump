# Configuration

Raspi-Sump uses two configuration files located in `/etc/raspi-sump/`:

| File | Purpose |
|------|---------|
| `raspisump.conf` | Main configuration — sensor, pit, alerts, intervals |
| `credentials.conf` | Credentials — SMTP password, Mastodon tokens, admin password |

Both files can be edited via the web admin panel (**gear icon → Configuration**
and **gear icon → Security**) without touching the command line. Changes to
`raspisump.conf` take effect after restarting the `raspisump` service.
Changes to `credentials.conf` take effect after restarting the `rsumpweb` service.

---

## raspisump.conf

### [gpio_pins]

| Setting | Description | Default |
|---------|-------------|---------|
| `trig_pin` | GPIO number for the sensor trig pin (sends signal) | `17` |
| `echo_pin` | GPIO number for the sensor echo pin (receives signal) | `27` |

GPIO numbers refer to the **BCM GPIO numbering**, not the physical pin numbers
on the header.

---

### [pit]

| Setting | Description | Default |
|---------|-------------|---------|
| `unit` | Unit of measure: `metric` (cm) or `imperial` (inches) | `metric` |
| `critical_water_level` | Water level that triggers an alert (cm or inches) | `35` |
| `pit_depth` | Distance from sensor to the bottom of the pit (cm or inches) | `72` |
| `reading_interval` | Seconds between readings. Set to `0` for a single reading then exit | `60` |
| `temperature` | Basement temperature used to calibrate speed of sound (°C or °F) | `20` |
| `alert_when` | `high` to alert on high water (sump pit); `low` to alert on low water (cistern) | `high` |

!!! note "Changing units"
    After changing `unit`, the web interface label updates on the next sensor reading. Readings already stored in the database are not converted — they retain the unit they were recorded in.

---

### [email]

| Setting | Description | Default |
|---------|-------------|---------|
| `alert_interval` | Minimum minutes between repeat alerts | `5` |
| `alert_type` | `1` = email, `2` = Mastodon | `1` |
| `smtp_authentication` | `0` = no auth, `1` = requires username/password | `0` |
| `smtp_tls` | `1` = use TLS | `0` |
| `smtp_ssl` | `1` = use SSL | `0` |
| `smtp_server` | SMTP server and port (e.g. `smtp.gmail.com:465`) | `localhost:25` |
| `email_to` | Recipient address(es), comma-separated | _(empty)_ |
| `email_from` | Sender address | _(empty)_ |
| `heartbeat` | `0` = disabled, `1` = send periodic test notifications | `0` |
| `heartbeat_interval` | Heartbeat frequency in minutes | `10079` (weekly) |

!!! note "Credentials"
    SMTP username/password and Mastodon tokens are stored in
    `credentials.conf`, not here.

!!! warning "TLS and SSL are mutually exclusive"
    Set only one of `smtp_tls` or `smtp_ssl` to `1`. Setting both will cause
    an error.

#### Common SMTP configurations

| Provider | Setting |
|----------|---------|
| Gmail | `smtp_ssl = 1`, `smtp_server = smtp.gmail.com:465`, `smtp_authentication = 1` |
| Office 365 | `smtp_tls = 1`, `smtp_server = smtp.office365.com:587`, `smtp_authentication = 1` |
| Local (Pi) | `smtp_server = localhost:25`, `smtp_authentication = 0` |

---

### [experimental]

| Setting | Description | Default |
|---------|-------------|---------|
| `cycle_detection` | `yes` to count pump cycles (pit empties) per day | `no` |

Cycle detection uses the observed water level range for each day to set
adaptive thresholds. When enabled, the homepage displays a daily empty count
and `rsumplog --cycles` becomes available.

---

## credentials.conf

Credentials are stored separately from the main config so that the file can
have tighter permissions. This file is managed via the web admin panel
(**gear icon → Security**).

| Setting | Description |
|---------|-------------|
| `[web] admin_password` | Hashed admin password for the web interface |
| `[email] smtp_username` | SMTP username (if `smtp_authentication = 1`) |
| `[email] smtp_password` | SMTP password |
| `[mastodon] client_id` | Mastodon app client ID |
| `[mastodon] client_secret` | Mastodon app client secret |
| `[mastodon] access_token` | Mastodon app access token |
| `[mastodon] mastodon_url` | URL of your Mastodon instance |
| `[mastodon] mastodon_user` | Mastodon account to send DMs to |

---

## Applying Changes

| Changed file | Restart required |
|--------------|-----------------|
| `raspisump.conf` | `raspisump` service |
| `credentials.conf` | `rsumpweb` service |

Both can be restarted from **gear icon → System Status** in the web interface,
or from the command line:

```bash
sudo systemctl restart raspisump
```
```bash
sudo systemctl restart rsumpweb
```
