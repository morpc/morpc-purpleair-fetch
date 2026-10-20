# Get API keys from .env file
from datetime import date
import logging

logger = logging.getLogger(__name__)

with open('.env') as env:
    lines = env.readlines()
    env = {}
    for line in lines:
        if not line.strip() or line.startswith('#'):
            continue
        k, v = line.split('=', 1)
        env[k] = v.strip()

# Construct headers
read_header = {
'X-API-Key': env['READ_KEY']
}

write_header = {
'X-API-Key': env['WRITE_KEY']
}

# Store URLS
GROUPS_URL = 'https://api.purpleair.com/v1/groups'
SENSORS_URL = 'https://api.purpleair.com/v1/sensors'
ORG_URL = 'https://api.purpleair.com/v1/organization'

DATA_FIELDS = [
        'humidity',
        'temperature', 
        'pressure', 
        'pm1.0_atm_a', 'pm1.0_atm_b', 'pm1.0_cf_1_a', 'pm1.0_cf_1_b',
        'pm2.5_alt_a', 'pm2.5_alt_b',  'pm2.5_atm_a', 'pm2.5_atm_b', 'pm2.5_cf_1_a', 'pm2.5_cf_1_b',
        'pm10.0_atm_a', 'pm10.0_atm_b', 'pm10.0_cf_1_a', 'pm10.0_cf_1_b',
        '0.3_um_count', '0.5_um_count', '1.0_um_count', '2.5_um_count', '5.0_um_count', '10.0_um_count', 
        ]

DATA_FIELDS_MAP = {
        'humidity': 'humidity',
        'temperature': 'temperature',
        'pressure': 'pressure',
        'pm1.0_atm_a': 'pm010_atm_a',
        'pm1.0_atm_b': 'pm010_atm_b',
        'pm1.0_cf_1_a': 'pm010_cf_1_a',
        'pm1.0_cf_1_b': 'pm010_cf_1_b',
        'pm2.5_alt_a': 'pm025_alt_a',
        'pm2.5_alt_b': 'pm025_alt_b',  
        'pm2.5_atm_a': 'pm025_atm_a', 
        'pm2.5_atm_b': 'pm025_atm_b', 
        'pm2.5_cf_1_a': 'pm025_cf_1_a', 
        'pm2.5_cf_1_b': 'pm025_cf_1_b',
        'pm10.0_atm_a': 'pm100_atm_a', 
        'pm10.0_atm_b': 'pm100_atm_b', 
        'pm10.0_cf_1_a': 'pm100_cf_1_a', 
        'pm10.0_cf_1_b': 'pm100_cf_1_b',
        '0.3_um_count': 'um_count_003',
        '0.5_um_count': 'um_count_005',
        '1.0_um_count': 'um_count_010',
        '2.5_um_count': 'um_count_025',
        '5.0_um_count': 'um_count_050',
        '10.0_um_count': 'um_count_100'
}

DATA_FIELDS_QUERY = [f"{x}|d3" for x in DATA_FIELDS] # Assign the number of decimals to return for pm data

AVERAGE_LIMITS = {
    0: [30, 'days'],
    10:	[60, 'days'],
    30:	[90, 'days'],
    60:	[180, 'days'],
    360:	[365, 'days'],
    1440:	[730, 'days'],
    10080:	[1825, 'days'],
    43200:	[7300, 'days'],
    525600:	[36500, 'days'],
}

def get_json_safely(url, headers, params=None):
    import requests

    logger.info(f"Getting data from {url} with parameters {params}.")
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        logger.error(f"Request content: {r.content}")
        raise requests.HTTPError(f"{r.status_code} error for {r.url}", response=r)
    else:
        logger.debug(f"Request successful. Decoding return JSON.")
        try:
            json = r.json()
        except requests.JSONDecodeError:
            logger.error(f"JSONDecoderError. Check the url. {r.url}")
            raise
    r.close()

    return json

def post_safely(url, headers, params=None):
    import requests

    logger.info(f"Posting data to {url} with parameters {params}.")
    r = requests.post(url, headers=headers, params=params)
    if r.status_code != 201:
        logger.error(f"Request content: {r.content}")
        raise requests.HTTPError(f"{r.status_code} error for {r.url}", response=r)
    else:
        logger.debug(f"Request successful. Decoding return JSON.")
        try:
            json = r.json()
        except requests.JSONDecodeError:
            logger.error(f"JSONDecoderError. Check the url. {r.url}")
            raise
    r.close()

    return json

def delete_safely(url, headers, params=None):
    import requests

    logger.info(f"Deleting data at {url} with parameters {params}.")
    r = requests.delete(url, headers=headers, params=params)
    if r.status_code != 204:
        logger.error(f"Request content: {r.content}")
        raise requests.HTTPError(f"{r.status_code} error for {r.url}", response=r)
    else:
        logger.debug(f"Delete successful.")
    r.close()

def verify_interval(start, end = None):
    import pandas as pd
    import datetime
    today = pd.to_datetime(datetime.datetime.today())
    

    if not isinstance(start, date):
        logger.debug(f"Converting {start} to date.")
        try:
            start = pd.to_datetime(start, yearfirst=True)
        except Exception as e:
            logger.error(f'Start parameter must be a date or convertible by pd.to_datetime: {e}')
            raise pd.errors.ParserError

    if end != None:
        if not isinstance(end, date):
            logger.debug(f"Converting {end} to date.")
            try:
                end = pd.to_datetime(end, yearfirst=True)
            except Exception as e:
                logger.error(f'Start parameter must be a date or convertible by pd.to_datetime: {e}')
                raise pd.errors.ParserError

    elif end == None:
        logger.debug(f"No end date provided. Using {today}")
        end = today

    logger.info(f'Creating interval for filtering deployments from {start} to {end}')
    interval = pd.Interval(start, end)

    return interval

def check_interval(interval, average):
    import pandas as pd

    logger.debug(f"Checking if {interval} is longer than allowable length.")
    freq = pd.Timedelta(value=AVERAGE_LIMITS[average][0], unit=AVERAGE_LIMITS[average][1])

    if interval.length > freq:
        interval_list = split_interval(interval=interval, freq=freq)
        logger.info(f"{interval} is longer than allowable {freq} returning list of {len(interval_list)} intervals")
        return interval_list
    else:
        logger.info(f"{interval} is within the allowable {freq} returning freq.")
        return interval

def split_interval(interval, freq):
    import pandas as pd

    logger.info(f"Splitting {interval} by {freq}")
    breaks = pd.date_range(interval.left, interval.right, freq=freq).to_list()
    if breaks[-1] != interval.right:
        breaks.append(interval.right)  # keep the final partial period
    range = pd.IntervalIndex.from_breaks(breaks).to_list()

    return range

def get_organization():
    logger.info(f"Getting organization data form PurpleAir API.")

    json = get_json_safely(ORG_URL, read_header)

    return json

def post_group(group_name):
    logger.info(f"Creating new group with name {group_name}. See get_group for all current groups.")

    params = {
        'name': group_name
    }

    json = post_safely(GROUPS_URL, write_header, params)

    return json

def get_groups():
    logger.info(f"Getting list of all groups in PurpleAir API.")
    json = get_json_safely(GROUPS_URL, read_header)

    return json

def get_group_details(group_id):
    logger.info(f"Getting group details for group id: {group_id}")

    json = get_json_safely(f"{GROUPS_URL}/{group_id}", headers=read_header)

    return json

def delete_group(group_id):
    logger.info(f"Deleting group {group_id} from PurpleAir API.")

    delete_safely(f"{GROUPS_URL}/{group_id}", headers=write_header)

def post_member(group_id, sensor_index):
    logger.info(f"Adding member to group with sensor index {sensor_index} to group {group_id}")

    params = {
        'group_id': group_id,
        'sensor_index': sensor_index
    }

    post_safely(f"{GROUPS_URL}/{group_id}/members", headers=write_header, params=params)

def delete_member(group_id, sensor_index):
    logger.info(f"Delete member {sensor_index} from group {group_id}")

    delete_safely(f"{GROUPS_URL}/{group_id}/members/{sensor_index}", headers=write_header)

def check_group_members(sensor_index, group_id):
    """
    Compare a list of sensor indexes to the current members of a PurpleAir API group.

    Parameters:
    -----------
    sensor_index : list of int
        The sensor indexes that should be members of the group.

    group_id : int
        The id number for the group. See get_groups().

    Returns:
    --------
    dict
        {'to_add': [...], 'to_remove': [...]} to pass to update_group_members().
    """

    details = get_group_details(group_id=group_id)
    in_group = [x['sensor_index'] for x in details['members']]

    logger.info(f"Comparing {len(sensor_index)} sensors and in PurpleAir API group {group_id}")

    to_add = []
    for x in sensor_index:
        if x not in in_group:
            to_add.append(x)

    to_remove = []
    for x in in_group:
        if x not in sensor_index:
            to_remove.append(x)

    logger.info(f"{len(to_add)} sensor to add and {len(to_remove)} to remove.")

    return {'to_add': to_add, 'to_remove': to_remove}


def update_group_members(update, group_id):
    import datetime
    logger.info(f"Updating sensor group {group_id}")

    if len(update['to_add']) > 0:
        logger.debug(f'Adding sensor {', '.join([str(x) for x in update['to_add']])} to {group_id}')
        for sensor in update['to_add']:
            post_member(group_id, sensor)
    else:
        logger.debug('No sensors to add.')

    if len(update['to_remove']) > 0:
        logger.debug(f'Removing sensors {', '.join([str(x) for x in update['to_remove']])} from {group_id}')
        for sensor in update['to_remove']:
            delete_member(group_id, sensor)
    else:
        logger.debug('No sensors to remove.')

    logger.info(f'Group {group_id} is up to date as of {datetime.datetime.today()}.')

def get_members_metadata(group_id):
    import requests
    import pandas as pd
    import datetime
    logger.info(f"Getting sensor metadata for group {group_id}")

    fields=['name', 'model', 'hardware', 'date_created', 'location_type', 'latitude', 'longitude', 'altitude']

    params = {
        'fields': ",".join(fields)
    }

    json = get_json_safely(f"{GROUPS_URL}/{group_id}/members", headers=read_header, params=params)

    df = pd.DataFrame([x for x in json['data']], columns=json['fields'])
    df['date_created'] = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc) for x in df['date_created']]

    return df

def get_members_health(group_id):
    import requests
    import pandas as pd
    import datetime
    logger.info(f"Getting health check data for sensors in group {group_id}")

    fields=['name', 'rssi', 'firmware_version', 'firmware_upgrade', 'uptime', 'pa_latency', 'memory', 'last_seen', 'last_modified', 'channel_state']

    params = {
        'fields': ",".join(fields)
    }

    json = get_json_safely(f"{GROUPS_URL}/{group_id}/members", headers=read_header, params=params)

    df = pd.DataFrame([x for x in json['data']], columns=json['fields'])
    df['last_seen'] = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc) for x in df['last_seen']]
    df['last_modified'] = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc) for x in df['last_modified']]
    df['datetime_check'] = datetime.datetime.fromtimestamp(json['data_time_stamp'], datetime.timezone.utc)

    df['status'] = None ## add calculation for status. 

    return df

def get_members_data(group_id):
    import pandas as pd
    import datetime
    logger.info(f"Getting most recent data reading for all members in group {group_id}")

    params = {
        'fields': ",".join(DATA_FIELDS_QUERY + ['last_seen'])
    }

    json = get_json_safely(f"{GROUPS_URL}/{group_id}/members", headers=read_header, params=params)

    df = pd.DataFrame([x for x in json['data']], columns=json['fields'])
    df.columns = [x.replace('|d3','') if x.endswith('|d3') else x for x in df.columns]
    df['time_stamp'] = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc) for x in df['last_seen']]
    df = df[['sensor_index', 'time_stamp'] + [col for col in DATA_FIELDS if col not in ['time_stamp', 'sensor_index']]]
    df.columns = [DATA_FIELDS_MAP[x] if x not in ['sensor_index', 'time_stamp'] else x for x in df.columns]
    df = df.rename(columns={'sensor_index': 'index'})

    return df

def get_member_history(group_id, member_id, start=None, end=None, average=0):
    """
    Retrieves historical data from the purple API for a given member of a group. 

    Start and end dates can be designated for a specific time period. If only one is designated then the max number of reading will be 
    returned based on the average reading that is set. If neither is set the readings will contain the max number of readings for the
    most recent period. 

    Parameters:
    -----------
    group_id : str
        The id number for the group. See get_groups().

    member_id : str
        The id number for the member of a given group. See get_group_details().

    start : date-like
        The beginning date for the data. 

    end : date-like
        The end date for the data.

    average : int
        default to 0 or realtime data. The timeframe of the data to return. See options below and associated query limits.
    
        Average	Maximum Data Returnable per Request
                0 (Real-time)	    30 days
                10 (10-minute)	    60 days
                30 (30-minute)  	90 days
                60 (1-hour)	        180 days
                360 (6-hour)	    1 year
                1440 (1-day)	    2 years
                10080 (1-week)	    5 years
                43200 (1-month)	    20 years
                525600 (1-year) 	100 years
    

    Returns:
    --------
    pandas.Dataframe
        A pandas dataframe with all the sensor readings for the sensor by member_id
    """

    import pandas as pd
    import datetime
    logger.info(f"Getting data for sensor with member id {member_id} between {start} and {end}, readings averaged every {average} minutes.")

    params = {
        'fields': ",".join(DATA_FIELDS_QUERY),
        'average': average
    }

    if start != None:
        if not isinstance(start, date):
            logger.debug(f"Converting {start} to date.")
            try:
                start = int(pd.to_datetime(start, yearfirst=True).timestamp())
            except Exception as e:
                logger.error(f'Start parameter must be a date or convertible by pd.to_datetime: {e}')
                raise pd.errors.ParserError
        else:
            start = int(pd.Timestamp(start).timestamp())
        params.update({'start_timestamp': start})

    if end != None:
        if not isinstance(end, date):
            logger.debug(f"Converting {end} to date.")
            try:
                end = int(pd.to_datetime(end, yearfirst=True).timestamp())
            except Exception as e:
                logger.error(f'End parameter must be a date or convertible by pd.to_datetime: {e}')
                raise pd.errors.ParserError
        else:
            end = int(pd.Timestamp(end).timestamp())
        params.update({'end_timestamp': end})

    json = get_json_safely(f"{GROUPS_URL}/{group_id}/members/{member_id}/history", headers=read_header, params=params)

    df = pd.DataFrame([x for x in json['data']], columns=json['fields'])
    df.columns = [x.replace('|d3','') if x.endswith('|d3') else x for x in df.columns]
    df['member_id'] = member_id
    df['group_id'] = group_id
    df['time_stamp'] = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc) for x in df['time_stamp']]

    df['sensor_index'] = sensorid_from_memberid(group_id=group_id, member_ids=df['member_id'])
    df = df[['sensor_index', 'time_stamp'] + [col for col in DATA_FIELDS if col not in ['time_stamp', 'sensor_index']]]
    df.columns = [DATA_FIELDS_MAP[x] if x not in ['sensor_index', 'time_stamp'] else x for x in df.columns]
    df = df.rename(columns={'sensor_index': 'index'})

    return df

def get_members_history(group_id, start, end, average=0):
    import pandas as pd
    
    details = get_group_details(group_id)
    members = [x['id'] for x in details['members']]
    logger.info(f"Getting data between {start} and {end} for all {len(members)} members of group {group_id}.")

    df = []
    for member in members:
        member_data = get_member_history(group_id, member, start=start, end=end, average=average)
        df.append(member_data)

    df = pd.concat(df)

    return df
    
def sensorid_from_memberid(group_id, member_ids):
    details = get_group_details(group_id)
    id_map = {x['id']: x['sensor_index'] for x in details['members']}

    return member_ids.map(id_map)

def get_sensor_history(sensor_index, start=None, end=None, average=0):
    import pandas as pd
    import datetime
    logger.info(f"Getting data for sensor {sensor_index} between {start} and {end}, readings averaged every {average} minutes.")

    params = {
        'fields': ",".join(DATA_FIELDS_QUERY),
        'average': average
    }

    if start != None:
        if not isinstance(start, date):
            logger.debug(f"Converting {start} to date.")
            try:
                start = int(pd.to_datetime(start, yearfirst=True).timestamp())
            except Exception as e:
                logger.error(f'Start parameter must be a date or convertible by pd.to_datetime: {e}')
                raise pd.errors.ParserError
        else:
            start = int(pd.Timestamp(start).timestamp())
        params.update({'start_timestamp': start})

    if end != None:
        if not isinstance(end, date):
            logger.debug(f"Converting {end} to date.")
            try:
                end = int(pd.to_datetime(end, yearfirst=True).timestamp())
            except Exception as e:
                logger.error(f'End parameter must be a date or convertible by pd.to_datetime: {e}')
                raise pd.errors.ParserError
        else:
            end = int(pd.Timestamp(end).timestamp())
        params.update({'end_timestamp': end})

    json = get_json_safely(f"https://api.purpleair.com/v1/sensors/{sensor_index}/history", headers=read_header, params=params)
    logger.debug(f"{json}")
    df = pd.DataFrame([x for x in json['data']], columns=json['fields'])
    df.columns = [x.replace('|d3','') if x.endswith('|d3') else x for x in df.columns]
    df['time_stamp'] = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc) for x in df['time_stamp']]
    df['sensor_index'] = sensor_index
    df = df[['sensor_index', 'time_stamp'] + [col for col in DATA_FIELDS if col not in ['time_stamp', 'sensor_index']]]
    df.columns = [DATA_FIELDS_MAP[x] if x not in ['sensor_index', 'time_stamp'] else x for x in df.columns]

    return df
