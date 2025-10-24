# Get API keys from .env file
from datetime import date
import logging

from click import group
from matplotlib.pylab import det

logging.basicConfig(level=logging.DEBUG,
                    force=True,
                    format='%(asctime)s | %(levelname)s | %(name)s.%(funcName)s : %(message)s'
                    )
logger = logging.getLogger(__name__)


with open('.env') as env:
    lines = env.readlines()
    env = {}
    for line in lines:
        k, v = line.split('=')
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

def get_json_safely(url, headers, params=None):
    import requests

    logger.info(f"Getting data from {url} with parameters {params}.")
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        logger.error(f"Request content: {r.content}")
        raise requests.HTTPError
    else:
        logger.debug(f"Request successful. Decoding return JSON.")
        try:
            json = r.json()
        except:
            logger.error(f"JSONDecoderError. Check the url. {r.url}")
            raise requests.JSONDecodeError
    r.close()

    return json

def post_safely(url, headers, params=None):
    import requests

    logger.info(f"Posting data to {url} with parameters {params}.")
    r = requests.post(url, headers=headers, params=params)
    if r.status_code != 201:
        logger.error(f"Request content: {r.content}")
        raise requests.HTTPError
    else:
        logger.debug(f"Request successful. Decoding return JSON.")
        try:
            json = r.json()
        except:
            logger.error(f"JSONDecoderError. Check the url. {r.url}")
            raise requests.JSONDecodeError
    r.close()

    return json

def delete_safely(url, headers, params=None):
    import requests

    logger.info(f"Deleting data at {url} with parameters {params}.")
    r = requests.post(url, headers=headers, params=params)
    if r.status_code != 204:
        logger.error(f"Request content: {r.content}")
        raise requests.HTTPError
    else:
        logger.debug(f"Delete successful.")
    r.close()


def get_organization():
    logger.info(f"Getting organization data form PurpleAir API.")

    json = get_json_safely(ORG_URL, read_header)

    return json

def get_deployed_sensors(log_path, sheet_name):
    """
    Fetch list of sensor indexes.

    Parameters:
    -----------
    log_path : path_like
        A string of path of deployment log

    sheet_name : str
        The sheet name that contains the deployment log

    Return:
    -------
    list
        A list of sensor indexes of deployed sensors
    """
    import pandas as pd
    import math

    logger.debug(f"Reading deployment log from {log_path}, sheet_name {sheet_name}")
    deployments = pd.read_excel(log_path, sheet_name=sheet_name).drop(0)
    deployed = deployments.loc[(~deployments['Sensor ID Deployment'].str.endswith('00'))&(deployments['Deployment_End'].isna())]
    sensor_index = [int(x) for x in deployed.Sensor_Index_ID if not math.isnan(x)]
    logger.debug(f"{len(sensor_index)} Sensors: {", ".join([str(x) for x in sensor_index])}")

    return sensor_index

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
        logger.debug(f'Removing sensors {', '.join({[str(x) for x in update['to_remove']]})} from {group_id}')
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
    import requests
    import pandas as pd
    import datetime
    logger.info(f"Getting most recent data reading for all members in group {group_id}")

    fields = ['name', 'last_seen', 'pm2.5_a', 'pm2.5_b', 'pm1.0_a', 'pm1.0_b', 'humidity', 'temperature', 'pressure']

    params = {
        'fields': ",".join(fields)
    }

    json = get_json_safely(f"{GROUPS_URL}/{group_id}/members", headers=read_header, params=params)

    df = pd.DataFrame([x for x in json['data']], columns=json['fields'])
    df['last_seen'] = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc) for x in df['last_seen']]

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
    import requests
    import pandas as pd
    import datetime
    logger.info(f"Getting data for sensor with member id {member_id} between {start} and {end}, readings averaged every {average} minutes.")

    fields = [
        'humidity',
        'temperature', 
        'pressure', 
        'pm1.0_atm_a', 'pm1.0_atm_b', 'pm1.0_cf_1_a', 'pm1.0_cf_1_b',
        'pm2.5_alt_a', 'pm2.5_alt_b',  'pm2.5_atm_a', 'pm2.5_atm_b', 'pm2.5_cf_1_a', 'pm2.5_cf_1_b',
        'pm10.0_atm_a', 'pm10.0_atm_b', 'pm10.0_cf_1_a', 'pm10.0_cf_1_b'
        ]

    fields = [f"{x}|d3" if x.startswith('pm') else x for x in fields] # Assign the number of decimals to return for pm data

    params = {
        'fields': ",".join(fields),
        'average': average
    }

    if start != None:
        if not isinstance(start, date):
            logger.debug(f"Converting {start} to date.")
            try:
                start = pd.to_datetime(start, yearfirst=True).strftime('%s')
            except Exception as e:
                logger.error(f'Start parameter must be a date or convertible by pd.to_datetime: {e}')
                raise pd.errors.ParserError
        else:
            start = start.strftime('%s')
        params.update({'start_timestamp': start})

    if end != None:
        if not isinstance(end, date):
            logger.debug(f"Converting {end} to date.")
            try:
                end = pd.to_datetime(end, yearfirst=True).strftime('%s')
            except Exception as e:
                logger.error(f'End parameter must be a date or convertible by pd.to_datetime: {e}')
                raise pd.errors.ParserError
        else:
            end = end.strftime('%s')
        params.update({'end_timestamp': end})

    json = get_json_safely(f"{GROUPS_URL}/{group_id}/members/{member_id}/history", headers=read_header, params=params)

    details = get_group_details(group_id)
    id_map = {}
    [id_map.update({x: y}) for x,y,z in [sensor.values() for sensor in details['members']]]

    df = pd.DataFrame([x for x in json['data']], columns=json['fields'])
    df['member_id'] = member_id
    df['sensor_index'] = df['member_id'].map(id_map)

    df['time_stamp'] = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc) for x in df['time_stamp']]
    df = df[['member_id', 'sensor_index', 'time_stamp'] + [col for col in df.columns if col not in ['member_id', 'time_stamp', 'sensor_index']]]

    return df

def get_members_history(group_id, start, end, average=0):
    import pandas as pd
    
    details = get_group_details(group_id)
    members = [x['id'] for x in details['members']]
    id_map = {}
    [id_map.update({x: y}) for x,y,z in [sensor.values() for sensor in details['members']]]
    logger.info(f"Getting data between {start} and {end} for all {len(members)} members of group {group_id}.")

    data = []
    for member in members:
        member_data = get_member_history(member)
        data.append(member_data)

    data = pd.concat(data)

    return data
    