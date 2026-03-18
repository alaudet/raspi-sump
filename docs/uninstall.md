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
