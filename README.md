# Service Status for Home Assistant

A custom integration that polls an aggregated service-status API (such as
[`lookup.minopia.de`](https://lookup.minopia.de/api/status/all)) and exposes
one sensor per monitored service (Discord, GitHub, Steam, AWS, Cloudflare, …),
all grouped under a single device.

## Features

- **Customizable endpoint** — any URL returning the aggregated status JSON
  (a `{"response": {"services": [...], "incidents": [...]}}` wrapper or a bare
  `{"services": [...]}` object).
- **One device, one sensor per service.** New services reported by the API are
  added automatically without a restart.
- **States are the raw status text** reported by each status page (e.g.
  `All Systems Operational`, `Minor Service Outage`, `Under Maintenance`).
  For stable automation triggers use the boolean `operational` attribute.
- **Rich attributes** on every sensor: category,
  status-page URL, active incident count, full incident list (name, impact,
  status, URL, timestamps), brand/status colors, and last-update time.
- Service icons are used as entity pictures automatically.

## Installation

### HACS (custom repository)

1. HACS → Integrations → ⋮ → *Custom repositories*
2. Add this repository as an *Integration*.
3. Install **Service Status** and restart Home Assistant.

### Manual

Copy `custom_components/service_status` into your Home Assistant
`config/custom_components/` folder and restart.

## Configuration

*Settings → Devices & Services → Add Integration → Service Status.*

| Field | Default | Description |
|---|---|---|
| API URL | `https://lookup.minopia.de/api/status/all?wait=true` | Endpoint to poll |
| Device name | `Service Status` | Name of the created device |
| Poll interval | `900` (15 min) | How often to poll, in seconds (minimum 60) |

Options (gear icon on the entry): change the URL and the poll interval later.

## Example automation

```yaml
alias: Notify on Discord outage
triggers:
  - trigger: state
    entity_id: sensor.service_status_discord
    attribute: operational
    to: false
actions:
  - action: notify.notify
    data:
      title: "Discord: {{ states('sensor.service_status_discord') }}"
      message: >-
        {{ state_attr('sensor.service_status_discord', 'active_incidents') }}
        active incidents
```
