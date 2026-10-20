# morpc-purpleair-fetch

A minimal example of pulling air quality sensor data from the [PurpleAir API](https://api.purpleair.com) with Python.

## Requirements

- Python 3.12+ with `requests` and `pandas`
- Read and Write API keys from PurpleAir (see the [PurpleAir Developer Dashboard](https://develop.purpleair.com))

## Setup

Create a `.env` file in the directory you run from (it is ignored by git):

```
READ_KEY=your-read-key
WRITE_KEY=your-write-key
```

## Usage

`purpleair.py` wraps the PurpleAir API endpoints. Sensors are identified by their sensor index, which is shown in the URL when you select a sensor on the [PurpleAir map](https://map.purpleair.com).

```python
import purpleair

sensor_index = [33773]  # replace with your sensor indexes

# Historical data for a single sensor
history = purpleair.get_sensor_history(33773, start='2021-07-23', end='2021-08-06', average=60)

# Keep a PurpleAir group in sync with your list of sensors
group = purpleair.post_group('my-sensors')  # or pick an existing id from purpleair.get_groups()
update = purpleair.check_group_members(sensor_index=sensor_index, group_id=group['group_id'])
purpleair.update_group_members(update=update, group_id=group['group_id'])

# Metadata, health, and latest readings for every sensor in the group
metadata = purpleair.get_members_metadata(group['group_id'])
health = purpleair.get_members_health(group['group_id'])
data = purpleair.get_members_data(group['group_id'])
```

See `DEV-morpc-purpleair-fetch.ipynb` for a step-by-step walkthrough. The schemas for the output tables are in `output_data/`.
