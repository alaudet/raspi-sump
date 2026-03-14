"""Pure-Python helpers for the Security / credentials editor (no Flask dependency)."""

import configparser
import re

CRED_PATH = "/etc/raspi-sump/credentials.conf"

# ---------------------------------------------------------------------------
# Field schema
# Each section: (section_key, section_label, [fields])
# Each field:   (key, label, widget, help_text_or_None)
# widget: "text" | "password"
# ---------------------------------------------------------------------------
CRED_SCHEMA = [
    ("web", "Web Admin", [
        ("admin_password", "Admin Password", "password",
         "Password for the admin interface. "
         "Restart rsumpweb.service for a new password to take effect."),
    ]),
    ("credentials", "Email / Mastodon Credentials", [
        ("username", "SMTP Username", "text",
         "SMTP login username — leave blank when smtp_authentication = 0"),
        ("password", "SMTP Password", "password",
         "SMTP login password — leave blank when smtp_authentication = 0"),
        ("client_id",     "Mastodon Client ID",     "password",
         "OAuth client_id from your Mastodon app registration"),
        ("client_secret", "Mastodon Client Secret", "password",
         "OAuth client_secret from your Mastodon app registration"),
        ("access_token",  "Mastodon Access Token",  "password",
         "OAuth access token from your Mastodon app registration"),
        ("api_base_url",  "Mastodon API Base URL",  "text",
         "e.g. https://mastodon.social"),
        ("handle",        "Mastodon Handle",        "text",
         "e.g. @you@mastodon.social"),
    ]),
]


def load_credentials(path: str = None) -> dict:
    """Return nested dict {section: {key: value}} read fresh from credentials.conf."""
    if path is None:
        path = CRED_PATH
    cp = configparser.RawConfigParser()
    cp.read(path)
    return {section: dict(cp.items(section)) for section in cp.sections()}


def validate_credentials_form(form_data) -> tuple:
    """Validate POST form data for the Security page.

    Returns (changes, errors) where:
      changes : {(section, key): value_str}
      errors  : list of human-readable error strings
    """
    changes = {}
    errors = []
    for section, _label, fields in CRED_SCHEMA:
        for key, label, _widget, _help in fields:
            raw = form_data.get(f"{section}__{key}", "").strip()
            if section == "web" and key == "admin_password" and not raw:
                errors.append("Admin Password must not be empty.")
                continue
            changes[(section, key)] = raw
    return changes, errors


def write_credentials(changes: dict, path: str = None) -> None:
    """Write changed values into credentials.conf, preserving all comments."""
    if path is None:
        path = CRED_PATH
    with open(path, "r") as f:
        lines = f.readlines()

    current_section = None
    out = []
    for line in lines:
        stripped = line.strip()

        # Section header
        m = re.match(r"^\[([^\]]+)\]$", stripped)
        if m:
            current_section = m.group(1)
            out.append(line)
            continue

        # Comment or blank line — preserve as-is
        if stripped.startswith("#") or stripped == "":
            out.append(line)
            continue

        # key = value line
        m = re.match(r"^(\w+)\s*=\s*(.*)$", stripped)
        if m and current_section:
            key = m.group(1)
            if (current_section, key) in changes:
                out.append(f"{key} = {changes[(current_section, key)]}\n")
                continue

        out.append(line)

    with open(path, "w") as f:
        f.writelines(out)
