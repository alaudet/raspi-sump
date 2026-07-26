# Home Assistant

Raspi-Sump ships a custom Home Assistant integration. It appears under
**Settings → Devices & Services**, creates proper sensor entities, and includes
a Lovelace card that reproduces the Raspi-Sump chart inside your dashboard.

It replaces the hand-written `rest:` sensor that people have historically used
to pull readings into Home Assistant.

## Requirements

- Home Assistant **2025.2.0** or later
- A Raspi-Sump install whose web interface is reachable from Home Assistant and
  which provides the `/api/status` endpoint (see [Web Interface](web-interface.md#json-api))

Home Assistant does not need to run on the same Pi.

## Installation

Either method works. Copying the files by hand needs nothing installed
beforehand; HACS is worth setting up only if you want update notifications.

### Manually

Copy the `custom_components/raspi_sump` directory from this repository into
Home Assistant's configuration directory — the one containing
`configuration.yaml` — so that you end up with:

```
<config>/custom_components/raspi_sump/manifest.json
```

Where that directory lives depends on how Home Assistant was installed:

| Installation | Configuration directory | Getting files in |
| --- | --- | --- |
| Home Assistant OS / Supervised | `/config` | the **Samba share** or **Advanced SSH & Web Terminal** add-on |
| Container / Docker | whatever you mapped to `/config` | copy it on the host |
| Core (venv) | `~/.homeassistant` | copy it directly |

Then restart Home Assistant: **Settings → System →** power icon (top right) **→
Restart Home Assistant**. A reload is not enough; a newly added integration
needs a full restart.

### Via HACS

[HACS](https://www.hacs.xyz/) is a separate community project, not part of Home
Assistant. If you do not already have a **HACS** entry in your sidebar, you
would need to [install it first](https://www.hacs.xyz/docs/use/download/download/)
— use the manual method above instead unless you want it for other reasons.

With HACS installed:

1. Open **HACS** from the sidebar.
2. Click the **⋮** menu in the **top right corner** and select **Custom repositories**.
3. Add `https://github.com/alaudet/raspi-sump` and set the type to **Integration**.
4. Download **Raspi-Sump**, then restart Home Assistant.

## Adding your sump pit

Go to **Settings → Devices & Services → Add Integration** and search for
**Raspi-Sump**.

| Field | Notes |
| --- | --- |
| Host | Hostname or IP of the Pi running Raspi-Sump |
| Port | `80` by default, or `443` when served over HTTPS |
| Uses HTTPS | Enable if the web interface is behind TLS |
| Verify SSL certificate | Turn off only for a self-signed certificate |
| Path prefix | Only when a reverse proxy serves Raspi-Sump under a subpath |

The address is verified before the entry is created. If Home Assistant reports
that the API version is unsupported, the Pi is running a Raspi-Sump release
that predates the `/api/status` endpoint — upgrade it.

The polling interval defaults to 60 seconds and can be changed under
**Configure** on the integration entry. There is nothing to gain from polling
faster than the `reading_interval` set in `raspisump.conf`.

## Entities

One device named **Raspi-Sump** is created, with a link back to the real web
interface on its device page.

| Entity | Description |
| --- | --- |
| `sensor.raspi_sump_water_level` | Depth of water in the pit |
| `sensor.raspi_sump_pit_full` | Water level as a percentage of `pit_depth` |
| `sensor.raspi_sump_level_min_today` | Lowest level recorded today |
| `sensor.raspi_sump_level_max_today` | Highest level recorded today |
| `sensor.raspi_sump_pit_empties_today` | Pump cycles today — only when `cycle_detection` is enabled |
| `sensor.raspi_sump_readings_today` | Number of readings taken today (diagnostic) |
| `sensor.raspi_sump_last_reading` | When the most recent reading was taken (diagnostic) |
| `sensor.raspi_sump_critical_level` | The configured `critical_water_level` (diagnostic) |
| `sensor.raspi_sump_pit_depth` | The configured `pit_depth` (diagnostic) |
| `binary_sensor.raspi_sump_critical` | On when the level has crossed `critical_water_level` |
| `binary_sensor.raspi_sump_service` | Whether `raspisump.service` is running (diagnostic) |

Levels are reported in centimetres or inches, matching the `unit` set in
`raspisump.conf`.

!!! note "Which way is up"
    Raspi-Sump records the **depth of water in the pit**, not the distance from
    the sensor down to the water — the value rises as the water rises. The
    critical binary sensor follows the same rule Raspi-Sump uses for alerts: it
    turns on above `critical_water_level` when `alert_when = high`, and below it
    when `alert_when = low`.

Entities report `unknown` when Raspi-Sump has no value for them (for example
before the first reading of the day), and `unavailable` when the web interface
cannot be reached at all.

### Example automation

```yaml
automation:
  - alias: Sump pit critical
    triggers:
      - trigger: state
        entity_id: binary_sensor.raspi_sump_critical
        to: "on"
        for: "00:02:00"
    actions:
      - action: notify.mobile_app
        data:
          title: Sump pit alert
          message: >-
            Water level is {{ states('sensor.raspi_sump_water_level') }}
            {{ state_attr('sensor.raspi_sump_water_level', 'unit_of_measurement') }}.
```

## The Lovelace card

The integration serves and registers its own card, so there is no resource to
add by hand. After a restart, **Raspi-Sump** appears in the card picker.

```yaml
type: custom:raspi-sump-card
```

All options:

```yaml
type: custom:raspi-sump-card
title: Sump Pit          # heading (default "Raspi-Sump")
show_stats: true         # stat tiles under the chart (default true)
height: 320              # chart height in pixels
entry_id: null           # only when several Raspi-Sump instances are configured
device_id: null          # restrict the stat tiles to one device
```

The card draws the same uPlot chart as the web interface, including the
critical-level threshold line, and follows your Home Assistant theme. Use
**‹** and **›** to page back through previous days, **Today** to return, and
**PNG** to download the chart.

The card does not talk to the Pi directly — it asks Home Assistant, which holds
the connection details. Nothing about your Raspi-Sump install is exposed to the
browser.

### Example dashboard

```yaml
views:
  - title: Sump Pit
    cards:
      - type: custom:raspi-sump-card
        title: Sump Pit

      - type: gauge
        entity: sensor.raspi_sump_pit_full
        name: Pit full
        min: 0
        max: 100
        severity:
          green: 0
          yellow: 50
          red: 75

      - type: entities
        entities:
          - binary_sensor.raspi_sump_critical
          - sensor.raspi_sump_water_level
          - sensor.raspi_sump_level_max_today
          - sensor.raspi_sump_last_reading
          - binary_sensor.raspi_sump_service
```

## Migrating from a REST sensor

If you previously polled Raspi-Sump with a `rest:` sensor:

1. Add the integration as described above and confirm the new entities report
   sensible values.
2. Delete the `rest:` block from `configuration.yaml` and restart Home
   Assistant.
3. Point your automations and dashboards at the new entities.

To avoid editing automations, you can instead rename the new entity to match
the old one: open the entity, click the ⚙ icon, and change its **Entity ID**.
Do this only after the old REST sensor has been removed, or the two will
collide.

Historical data recorded under the old entity stays with the old entity ID. If
you want long-term statistics to carry over, rename the new entity to the old
ID rather than adopting a new one.

## Troubleshooting

**The integration cannot connect.** Check that Home Assistant can reach the web
interface: `curl https://<pi>/api/status` from the Home Assistant host. A
self-signed certificate needs **Verify SSL certificate** turned off.

**`Pit empties today` is missing.** Cycle detection is off by default. Set
`cycle_detection = yes` in the `[experimental]` section of `raspisump.conf`,
restart `raspisump.service`, then reload the integration.

**The card does not appear in the picker.** Do a hard refresh of the browser
(Ctrl-Shift-R). The card is loaded from `/raspi_sump_static/` with a version
query string, so a restart plus a refresh is enough after an upgrade.

**Levels are labelled in the wrong unit.** The unit is read once when entities
are created. After changing `unit` in `raspisump.conf`, reload the integration
entry.
