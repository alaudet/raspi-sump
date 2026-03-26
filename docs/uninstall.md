# Full Uninstall

### 1. Stop and disable the services

```bash
sudo systemctl stop raspisump rsumpweb
sudo systemctl disable raspisump rsumpweb
```

### 2. Purge the package

```bash
sudo apt purge raspisump
sudo apt autoremove
```

### 3. Remove the raspisump user and home directory

```bash
sudo deluser --remove-home raspisump
```

### 4. Remove remaining data directories

```bash
sudo rm -rf /var/lib/raspisump
sudo rm -rf /var/log/raspisump
```

### 5. Remove the Linuxnorth APT repository and signing key

```bash
sudo rm /etc/apt/sources.list.d/linuxnorth.list
sudo rm /usr/share/keyrings/linuxnorth-archive-keyring.gpg
sudo apt update
```


# Full Uninstall - Earlier 1.x versions { #earlier-1x }

### Removing a Legacy Raspi-Sump Installation

If you have an older raspi-sump (1.x) installed in a Python virtual environment,
remove it before installing the new package.

### 1. Remove the old Python packages from the virtual environment:**

```bash
source /opt/raspi-sump/bin/activate
pip uninstall raspisump hcsr04sensor
deactivate
```

If you used a different virtual environment path, adjust accordingly.

### 2. Archive the old raspi-sump directory:**

```bash
mv /home/$USER/raspi-sump /home/$USER/raspi-sump.archive
```

This preserves your old config and logs in case you need to refer back to them.

### 3. Remove lighttpd if installed:**

Raspi-Sump uses nginx. If lighttpd is running it will conflict on port 80.

```bash
sudo systemctl stop lighttpd
sudo apt remove --purge lighttpd
```

### 4. Remove any old cron jobs:**

```bash
crontab -e
```

Remove any lines referencing `rsump`, `rsumpmonitor`, or `rsumpwebchart` and save.

