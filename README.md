# DWD Pollenflug

This component adds pollen forecasts from [Deutscher Wetterdienst (DWD)](https://www.dwd.de/DE/leistungen/gefahrenindizespollen/gefahrenindexpollen.html) to Home Assistant.

The DWD provides forecasts for [27 regions](https://www.dwd.de/DE/leistungen/gefahrenindizespollen/Gebiete.html;jsessionid=6EFEC19F16B0D0204A19D135D464295E.live11041?nn=16102&lsbId=463856) in Germany. The data will be updated daily (currently at 11am) and the forecasts include the data for today and tomorrow (and the day after tomorrow on Friday).

A forecast is provided for the following grass and tree pollen:

- Alder (Erle)
- Ambrosia (Ambrosia)
- Ash (Esche)
- Birch (Birke)
- Hazel (Hasel)
- Grass (Gräser)
- Mugwort (Beifuss)
- Rye (Roggen)

This component fetches data every hour from DWD (although the data is updated only once per day).

If you like this component, please give it a star on [github](https://github.com/mampfes/hacs_dwd_pollenflug).

## Installation

1. Ensure that [HACS](https://hacs.xyz) is installed.
2. Install **DWD Pollenflug** integration via HACS.
3. Add **DWD Pollenflug** integration to Home Assistant (one per region):

   [![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=dwd_pollenflug)

In case you would like to install manually:

1. Copy the folder `custom_components/dwd_pollenflug` to `custom_components` in your Home Assistant `config` folder.
2. Add **DWD Pollenflug** integration to Home Assistant (one per region):

   [![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=dwd_pollenflug)

One instance of **DWD Pollenflug** covers one region. If you want to get the data from multiple regions, just add multiple instance of the **DWD Pollenflug** integration.

## Sensors

This integration provides one sensor per pollen type. The sensor is named according to the pollen type.

### Sensor State

 The sensor state represents an index of the pollen count. DWD is using the following index range:

Index | Description (in German)
------|-----------------------------------
0     | keine Belastung
0.5   | keine bis geringe Belastung
1     | geringe Belastung
1.5   | geringe bis mittlere Belastung
2     | mittlere Belastung
2.5   | mittlere bis hohe Belastung
3     | hohe Belastung

### Sensor Attributes

Each sensor provides the following attributes (not including default attributes):

Attribute           | Example                   | Description
--------------------|---------------------------|-------------------------------------------------------------------------
state_tomorrow      | 1                         | Forecast for tomorrow.
state_in_2_days     | 1                         | Forecast for the day after tomorrow.
state_today_desc    | geringe Belastung         | Human readable description of the forecast for today [in German].
state_tomorrow_desc | geringe Belastung         | Human readable description of the forecast for tomorrow [in German].
state_in_2_days_desc| geringe Belastung         | Human readable description of the forecast for the day after tomorrow [in German].
last_update         | 2021-09-28T11:00:00+02:00 | Timestamp representing the last update of the data by DWD.
next_update         | 2021-09-29T11:00:00+02:00 | Timestamp representing the next update of the data by DWD.

## Examples

A minimalistic example in combination with [Lovelace-Mushroom-Cards](https://github.com/piitaya/lovelace-mushroom) can look like this:

![](images/dwd-pollenflug-minimalistic.png)

To configure:

* Edit your dashboard
* Add a new Mushroom-Template-Card and copy/paste:

```yaml
square: true
type: grid
columns: 4
cards:
  - type: custom:mushroom-template-card
    entity: sensor.pollenflug_graeser_124
    primary: Gras
    icon: mdi:grass
    layout: vertical
    icon_color: |-
      {% if states(config.entity) | int <= 1 %}
        green
      {% elif states(config.entity) | int <= 2 %}
        orange
      {% elif states(config.entity) | int <= 3 %}
        red
      {% endif %}
    tap_action:
      action: more-info
    hold_action:
      action: none
    double_tap_action:
      action: none
    multiline_secondary: true
  - type: custom:mushroom-template-card
    entity: sensor.pollenflug_ambrosia_124
    primary: Ambrosia
    icon: mdi:flower-pollen
    layout: vertical
    icon_color: |-
      {% if states(config.entity) | int <= 1 %}
        green
      {% elif states(config.entity) | int <= 2 %}
        orange
      {% elif states(config.entity) | int <= 3 %}
        red
      {% endif %}
    tap_action:
      action: more-info
    hold_action:
      action: none
    double_tap_action:
      action: none
    multiline_secondary: true
  - type: custom:mushroom-template-card
    entity: sensor.pollenflug_beifuss_124
    primary: Beifuss
    icon: mdi:flower-pollen
    layout: vertical
    icon_color: |-
      {% if states(config.entity) | int <= 1 %}
        green
      {% elif states(config.entity) | int <= 2 %}
        orange
      {% elif states(config.entity) | int <= 3 %}
        red
      {% endif %}
    tap_action:
      action: more-info
    hold_action:
      action: none
    double_tap_action:
      action: none
    multiline_secondary: true
  - type: custom:mushroom-template-card
    entity: sensor.pollenflug_birke_124
    primary: Birke
    icon: mdi:flower-pollen
    layout: vertical
    icon_color: |-
      {% if states(config.entity) | int <= 1 %}
        green
      {% elif states(config.entity) | int <= 2 %}
        orange
      {% elif states(config.entity) | int <= 3 %}
        red
      {% endif %}
    tap_action:
      action: more-info
    hold_action:
      action: none
    double_tap_action:
      action: none
    multiline_secondary: true
  - type: custom:mushroom-template-card
    entity: sensor.pollenflug_erle_124
    primary: Erle
    icon: mdi:flower-pollen
    layout: vertical
    icon_color: |-
      {% if states(config.entity) | int <= 1 %}
        green
      {% elif states(config.entity) | int <= 2 %}
        orange
      {% elif states(config.entity) | int <= 3 %}
        red
      {% endif %}
    tap_action:
      action: more-info
    hold_action:
      action: none
    double_tap_action:
      action: none
    multiline_secondary: true
  - type: custom:mushroom-template-card
    entity: sensor.pollenflug_hasel_124
    primary: Hasel
    icon: mdi:flower-pollen
    layout: vertical
    icon_color: |-
      {% if states(config.entity) | int <= 1 %}
        green
      {% elif states(config.entity) | int <= 2 %}
        orange
      {% elif states(config.entity) | int <= 3 %}
        red
      {% endif %}
    tap_action:
      action: more-info
    hold_action:
      action: none
    double_tap_action:
      action: none
    multiline_secondary: true
  - type: custom:mushroom-template-card
    entity: sensor.pollenflug_esche_124
    primary: Esche
    icon: mdi:flower-pollen
    layout: vertical
    icon_color: |-
      {% if states(config.entity) | int <= 1 %}
        green
      {% elif states(config.entity) | int <= 2 %}
        orange
      {% elif states(config.entity) | int <= 3 %}
        red
      {% endif %}
    tap_action:
      action: more-info
    hold_action:
      action: none
    double_tap_action:
      action: none
    multiline_secondary: true
  - type: custom:mushroom-template-card
    entity: sensor.pollenflug_roggen_124
    primary: Roggen
    icon: mdi:flower-pollen
    layout: vertical
    icon_color: |-
      {% if states(config.entity) | int <= 1 %}
        green
      {% elif states(config.entity) | int <= 2 %}
        orange
      {% elif states(config.entity) | int <= 3 %}
        red
      {% endif %}
    tap_action:
      action: more-info
    hold_action:
      action: none
    double_tap_action:
      action: none
    multiline_secondary: true

```

You can also add the description / forecast:

![Alt text](images/dwd-pollenflug-desc.png)


Code:

```yaml
square: true
type: grid
columns: 2
cards:
  - type: custom:mushroom-template-card
    entity: sensor.pollenflug_graeser_124
    primary: Gras
    secondary: >-
      Today: {{ state_attr('sensor.pollenflug_graeser_124', 'state_today_desc') }}

      Tomorrow: {{ state_attr('sensor.pollenflug_graeser_124', 'state_tomorrow_desc') }}
    icon: mdi:grass
    layout: vertical
    icon_color: |-
      {% if states(config.entity) | int <= 1 %}
        green
      {% elif states(config.entity) | int <= 2 %}
        orange
      {% elif states(config.entity) | int <= 3 %}
        red
      {% endif %}
    tap_action:
      action: more-info
    hold_action:
      action: none
    double_tap_action:
      action: none
    multiline_secondary: true
  - type: custom:mushroom-template-card
    entity: sensor.pollenflug_erle_124
    primary: Erle
    secondary: >-
      Today: {{ state_attr('sensor.pollenflug_erle_124', 'state_today_desc') }}

      Tomorrow: {{ state_attr('sensor.pollenflug_erle_124', 'state_tomorrow_desc') }}
    icon: mdi:flower-pollen
    layout: vertical
    icon_color: |-
      {% if states(config.entity) | int <= 1 %}
        green
      {% elif states(config.entity) | int <= 2 %}
        orange
      {% elif states(config.entity) | int <= 3 %}
        red
      {% endif %}
    tap_action:
      action: more-info
    hold_action:
      action: none
    double_tap_action:
      action: none
    multiline_secondary: true
```

Use of auto-entities:

![Alt text](images/dwd-pollenflug-desc-autoentities.png)


Code:

```yaml
type: custom:auto-entities
card:
  type: grid
  columns: 2
  square: false
card_param: cards
filter:
  include:
    - name: Pollenflug*
      state: '>0'
      options:
        type: custom:mushroom-template-card
        primary: '{{state_attr(''this.entity_id'', ''friendly_name'')}}'
        secondary: morgen {{state_attr('this.entity_id', 'state_tomorrow_desc')}}
        icon: '{{state_attr(''this.entity_id'', ''icon'')}}'
        layout: horizontal
        icon_color: |-
          {% if states(config.entity) | float <= 1 %}
            green
          {% elif states(config.entity) | float <= 2 %}
            orange
          {% else %}
            red
          {% endif %}
        tap_action:
          action: more-info
        hold_action:
          action: none
        double_tap_action:
          action: none
        multiline_secondary: true
  exclude: []
sort:
  method: state
  reverse: true
show_empty: false

