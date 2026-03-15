"""Pure-Python helpers for the configuration editor (no Flask dependency)."""

import configparser
import re

_CONF_PATH = "/etc/raspi-sump/raspisump.conf"

# ---------------------------------------------------------------------------
# Field schema
# Each section: (section_key, section_label, [fields])
# Each field:   (key, label, widget, options_or_None, help_text_or_None)
# widget:  "integer" | "float" | "text" | "select"
# options: [(value, display), ...] for select, else None
# ---------------------------------------------------------------------------
FIELD_SCHEMA = [
    ("gpio_pins", "GPIO Pins", [
        ("trig_pin", "Trig Pin", "integer", None,
         "GPIO pin number that sends the trigger signal"),
        ("echo_pin", "Echo Pin", "integer", None,
         "GPIO pin number that receives the echo signal"),
    ]),
    ("pit", "Pit Settings", [
        ("unit", "Unit of Measure", "select",
         [("metric", "Metric (cm)"), ("imperial", "Imperial (inches)")], None),
        ("critical_water_level", "Critical Water Level", "float", None,
         "cm if metric, inches if imperial — triggers an alert"),
        ("pit_depth", "Pit Depth", "float", None,
         "Distance from sensor to pit bottom (cm or inches)"),
        ("reading_interval", "Reading Interval", "integer", None,
         "Seconds between readings; 0 = take one reading then exit"),
        ("temperature", "Temperature", "float", None,
         "°C if metric, °F if imperial — adjusts speed of sound calculation"),
        ("alert_when", "Alert When", "select",
         [("high", "High — alert on high water (sump pit)"),
          ("low",  "Low — alert on low water (cistern)")], None),
    ]),
("email", "Alerts & Email", [
        ("alert_interval", "Alert Interval (minutes)", "integer", None,
         "Minimum minutes between repeated alerts"),
        ("alert_type", "Alert Type", "select",
         [("1", "1 — Email / SMTP"), ("2", "2 — Mastodon")], None),
        ("smtp_authentication", "SMTP Authentication", "select",
         [("0", "0 — No"), ("1", "1 — Yes")],
         "Required for Gmail, Office 365; not needed for localhost"),
        ("smtp_tls", "SMTP TLS", "select",
         [("0", "0 — No"), ("1", "1 — Yes")],
         "Office 365 uses TLS — never enable both TLS and SSL"),
        ("smtp_ssl", "SMTP SSL", "select",
         [("0", "0 — No"), ("1", "1 — Yes")],
         "Gmail uses SSL — never enable both TLS and SSL"),
        ("smtp_server", "SMTP Server", "text", None,
         "e.g. smtp.gmail.com:465 (SSL) or smtp.office365.com:587 (TLS)"),
        ("email_to", "Email To", "text", None,
         "Recipient address(es) — separate multiple with a comma and space"),
        ("email_from", "Email From", "text", None,
         "Sender address — e.g. Raspi-Sump <you@example.com>"),
        ("heartbeat", "Heartbeat", "select",
         [("0", "0 — Disabled"), ("1", "1 — Enabled")],
         "Sends a periodic test notification to confirm alerts are working"),
        ("heartbeat_interval", "Heartbeat Interval (minutes)", "integer", None,
         "1439 = daily, 10079 = weekly, 43199 = monthly"),
    ]),
]


def load_current_values(path: str = None) -> dict:
    """Return nested dict {section: {key: value}} from the config file."""
    if path is None:
        path = _CONF_PATH
    cp = configparser.RawConfigParser()
    cp.read(path)
    return {section: dict(cp.items(section)) for section in cp.sections()}


def validate_config_form(form_data) -> tuple:
    """Validate POST form data against FIELD_SCHEMA.

    Returns (changes, errors) where:
      changes : {(section, key): value_str} — all valid fields
      errors  : list of human-readable error strings
    """
    changes = {}
    errors = []
    for section, _label, fields in FIELD_SCHEMA:
        for key, label, widget, options, _help in fields:
            raw = form_data.get(f"{section}__{key}", "").strip()
            if widget == "integer":
                try:
                    int(raw)
                except ValueError:
                    errors.append(f"{label}: must be a whole number (got {raw!r})")
                    continue
            elif widget == "float":
                try:
                    float(raw)
                except ValueError:
                    errors.append(f"{label}: must be a number (got {raw!r})")
                    continue
            elif widget == "select":
                valid = [o[0] for o in options]
                if raw not in valid:
                    errors.append(f"{label}: invalid selection {raw!r}")
                    continue
            changes[(section, key)] = raw
    return changes, errors


def write_config_values(changes: dict, path: str = None) -> None:
    """Write changed values into the config file, preserving all comments."""
    if path is None:
        path = _CONF_PATH
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
