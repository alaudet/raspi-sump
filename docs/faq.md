# FAQ

## Why is no data showing on the home page?

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

## How do I reset my admin password?

Log in to the web interface and go to **gear icon → Security**. Enter a new
password in the admin password fields and save.

If you are locked out entirely, edit `/etc/raspi-sump/credentials.conf`
directly and set:

```ini
[web]
admin_password = admin
```

Then restart the `rsumpweb` service. The first-run setup wizard will appear
on next browser visit and prompt you to set a new password.

---

## The web interface shows a security warning in my browser

This is expected. The TLS certificate is self-signed. Accept the browser
exception to proceed — the connection is still encrypted.

---

## How do I change the GPIO pins?

Edit `raspisump.conf` via **gear icon → Configuration** and update `trig_pin`
and `echo_pin` to your chosen BCM GPIO numbers. Restart the `raspisump`
service for the change to take effect.

---

## No readings after changing the reading interval

Restart the `raspisump` service after changing `reading_interval`:

```bash
sudo systemctl restart raspisump
```

Or use the restart button on **gear icon → System Status**.

---

## How do I import data from Raspi-Sump 1.x?

See the [Upgrading](upgrade.md) guide for full instructions. The short version:

```bash
rsumpimport --dir ~/raspi-sump-backup/ --unit metric
```

Or use the web interface: **gear icon → Import/Export CSV**.

---

## alerttest is not sending email

Check the following:

1. `alert_type = 1` in `raspisump.conf`
2. SMTP credentials are correct in `credentials.conf`
3. `smtp_server`, `smtp_tls`/`smtp_ssl`, and `smtp_authentication` match your provider
4. If using Gmail, ensure you are using an App Password, not your account password

Run `alerttest` from the command line to see any error output.

---

## How do I back up my data?

Use **gear icon → Backup/Export** in the web interface. This downloads a zip
file containing the SQLite database and `raspisump.conf`.

---

## Can I run Raspi-Sump without the web interface?

Yes. The `raspisump` and `rsumpweb` services are independent. Stop
`rsumpweb` if you do not need the web interface:

```bash
sudo systemctl stop rsumpweb
sudo systemctl disable rsumpweb
```

The monitoring daemon (`raspisump`) will continue running and logging readings.

---

## Where are the log files?

| Log | Location |
|-----|----------|
| Service logs | `journalctl -u raspisump` / `journalctl -u rsumpweb` |
| Error log | `/var/log/raspi-sump/` |
| Database | `/var/lib/raspi-sump/raspisump.db` |

---

## How do I report a bug?

Run `rsumpsupport` to generate a support file:

```bash
rsumpsupport
```

Then open an issue in the
[issue tracker](https://github.com/alaudet/raspi-sump/issues) and attach
the support file.
