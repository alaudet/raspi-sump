# Alerts

Raspi-Sump can notify you when the water level reaches a critical threshold
via email (SMTP) or Mastodon direct message.

---

## Alert Types

| `alert_type` | Method |
|--------------|--------|
| `1` | Email (SMTP) |
| `2` | Mastodon DM |

Set `alert_type` in `raspisump.conf` or via **gear icon → Configuration** in
the web interface.

---

## Email Alerts

### Configuration

Set the following in `raspisump.conf` (or via the web config editor):

```ini
[email]
alert_type = 1
smtp_authentication = 1
smtp_ssl = 1
smtp_server = smtp.gmail.com:465
email_to = you@example.com
email_from = Raspi-Sump <you@example.com>
```

Set your SMTP credentials in `credentials.conf` (or via **gear icon →
Security**):

```ini
[email]
smtp_username = you@example.com
smtp_password = your_app_password
```

### Common SMTP Providers

**Gmail**

Use an [App Password](https://support.google.com/accounts/answer/185833)
rather than your Google account password. Two-factor authentication must be
enabled on your Google account.

```ini
smtp_authentication = 1
smtp_ssl = 1
smtp_server = smtp.gmail.com:465
```

**Office 365**

```ini
smtp_authentication = 1
smtp_tls = 1
smtp_server = smtp.office365.com:587
```

**Local SMTP (Pi)**

If you have a local mail server running on the Pi:

```ini
smtp_authentication = 0
smtp_server = localhost:25
```

### Testing Email Alerts

After configuring, test from the command line:

```bash
alerttest
```

This sends a test alert to the address set in `email_to`.

---

## Mastodon Alerts

Raspi-Sump sends alerts as direct messages on Mastodon. Because Mastodon
does not allow an account to DM itself, you need **two accounts**:

- A **bot account** — the sender. The application is registered under this account.
- Your **personal account** — the recipient. This is where alerts are delivered.

### Create a Bot Account

Create a second Mastodon account on any instance to act as the bot sender
(e.g. `@raspisump_bot@mastodon.social`). This account sends the DMs to your
personal account.

### Register a Mastodon Application

1. Log in to the **bot account**
2. Go to **Settings → Development → New Application**
3. Give it a name (e.g. `raspi-sump`)
4. Scopes required: `read` and `write`
5. Save — note the **Client key**, **Client secret**, and **Access token**

### Configuration

Set `alert_type = 2` in `raspisump.conf`.

Add the Mastodon credentials to `credentials.conf` (or via **gear icon →
Security**):

```ini
[mastodon]
client_id = your_client_key
client_secret = your_client_secret
access_token = your_access_token
mastodon_url = https://your-mastodon-instance.example
mastodon_user = @yourpersonalaccount@any-mastodon-instance.example
```

- `mastodon_url` — the instance URL of the **bot account** (any Mastodon instance)
- `mastodon_user` — your **personal account** that receives the DMs (can be on any instance)

### Testing Mastodon Alerts

After configuring, test from the command line:

```bash
alerttest
```

This sends a test direct message to the account set in `mastodon_user`.

---

## Heartbeat Notifications

A heartbeat sends a periodic test notification to confirm that alerting is
working. This is useful for catching situations where the Pi loses network
access or a credentials change breaks alerting.

```ini
[email]
heartbeat = 1
heartbeat_interval = 10079   # weekly (in minutes)
```

| Reference | Minutes |
|-----------|---------|
| Daily | 1439 |
| Weekly | 10079 |
| Monthly | 43199 |

---

## Alert Interval

To avoid being flooded with alerts when water stays at a critical level,
set a minimum interval between repeat notifications:

```ini
alert_interval = 5   # minutes
```

Readings continue to be logged regardless of this setting — only the
alert notifications are throttled.
