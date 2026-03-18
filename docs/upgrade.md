# Upgrading

## Upgrading Between 2.x Versions

If you installed Raspi-Sump from the Linuxnorth APT repository, upgrading to
the latest version is a standard `apt upgrade`:

```bash
sudo apt update
sudo apt upgrade raspisump
```

The upgrade preserves your existing configuration files in `/etc/raspi-sump/`
and your database in `/var/lib/raspi-sump/`. No data is lost.

Both services are restarted automatically after the upgrade.

---

## Migrating from Raspi-Sump 1.x to 2.x

Version 2 is a complete rewrite and is **not compatible** with the 1.x
installation. You must remove 1.x before installing 2.x.

!!! warning "Back up your data first"
    Export or copy your 1.x CSV log files before removing the old package.
    They can be imported into the 2.x database after install.

### Step 1 — Back up your 1.x CSV files

1.x stores readings as daily CSV files, typically in `~/raspi-sump/csv/` or
`/home/pi/raspi-sump/csv/`. Copy them somewhere safe before proceeding:

```bash
cp -r ~/raspi-sump/csv/ ~/raspi-sump-backup/
```

### Step 2 — Remove Raspi-Sump 1.x

Uninstall the 1.x packages from the virtualenv in `/opt/raspi-sump`:

```bash
source /opt/raspi-sump/bin/activate
pip uninstall raspisump hcsr04sensor
deactivate
```

Remove any 1.x cron jobs:

```bash
crontab -l   # review and remove any raspisump cron entries
crontab -e   # edit to remove them
```

If you have **lighttpd** installed from the 1.x web interface, purge it:

```bash
sudo apt purge lighttpd
```

### Step 3 — Install Raspi-Sump 2.x

Follow the [Fresh Install](installation.md) guide to add the APT repository
and install the package.

### Step 4 — Import your 1.x CSV data

After completing the first-run setup wizard, log in to the admin panel and
navigate to **Import/Export CSV**. Upload your backed-up CSV files to import
your historical readings into the 2.x database.

The importer skips duplicate entries, so it is safe to import the same files
more than once.

---

## Reporting Issues

Please report any problems in the
[issue tracker](https://github.com/alaudet/raspi-sump/issues).
