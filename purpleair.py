# Get API keys from .env file
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

def get_organization():
    import requests

    r = requests.get(ORG_URL, headers=read_header)
    if r.status_code != 200:
        print(r.content)
        raise requests.HTTPError
    else:
        try:
            json = r.json()
        except:
            raise requests.JSONDecodeError
    r.close()

    return json

def get_sensor_index(log_path, sheet_name):
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

    deployments = pd.read_excel(log_path, sheet_name=sheet_name).drop(0)
    deployed = deployments.loc[(~deployments['Sensor ID Deployment'].str.endswith('00'))&(deployments['Deployment_End'].isna())]
    sensor_index = [int(x) for x in deployed.Sensor_Index_ID if not math.isnan(x)]

    return sensor_index

def post_group(group_name):
    import requests

    params = {
        'name': group_name
    }

    r = requests.post(GROUPS_URL, headers=write_header, params=params)
    if r.status_code != 201:
        print(r.content)
        raise requests.HTTPError
    else:
        try:
            json = r.json()
        except:
            raise requests.JSONDecodeError
    r.close()

def get_groups():
    import requests

    r = requests.get(GROUPS_URL, headers=read_header)
    if r.status_code != 200:
        print(r.content)
        raise requests.HTTPError
    else:
        try:
            json = r.json()
        except:
            raise requests.JSONDecodeError
    r.close()

    return json

def get_group_details(group_id):
    import requests

    r = requests.get(f"{GROUPS_URL}/{group_id}", headers=read_header)

    if r.status_code != 200:
        print(r.url)
        print(r.content)
        raise requests.HTTPError
    else:
        try:
            json = r.json()
        except:
            raise requests.JSONDecodeError
    r.close()

    return json

def delete_group(group_id):
    import requests

    r = requests.delete(f"{GROUPS_URL}/{group_id}", headers=write_header)
    if r.status_code != 204:
        print(r.url)
        print(r.content)
        raise requests.HTTPError
    else:
        print(r.content)
    r.close()

def post_member(group_id, sensor_index):
    import requests

    params = {
        'group_id': group_id,
        'sensor_index': sensor_index
    }

    r = requests.post(f"{GROUPS_URL}/{group_id}/members", headers=write_header, params=params)
    if r.status_code != 201:
        print(r.content)
        raise requests.HTTPError
    else:
        try:
            json = r.json()
        except:
            raise requests.JSONDecodeError
    r.close()

def delete_member(group_id, sensor_index):
    import requests

    r = requests.delete(f"{GROUPS_URL}/{group_id}/members/{sensor_index}", headers=write_header)
    if r.status_code != 204:
        print(r.content)
        raise requests.HTTPError
    else:
        print(r.content)
    r.close()

def check_group_members(sensor_index, group_id):

    details = get_group_details(group_id=group_id)
    in_group = [x['sensor_index'] for x in details['members']]

    print(f"{len(sensor_index)} sensors in index from deployment log: {", ".join([str(x) for x in sensor_index])}")
    print(f"{len(in_group)} sensors in API group: {", ".join([str(x) for x in in_group])}")

    to_add = []
    for x in sensor_index:
        if x not in in_group:
            to_add.append(x)

    to_remove = []
    for x in in_group:
        if x not in sensor_index:
            to_remove.append(x)

    return {'to_add': to_add, 'to_remove': to_remove}


def update_group_members(update, group_id):

    if len(update['to_add']) > 0:
        print(f'Adding sensor {', '.join([str(x) for x in update['to_add']])} to {group_id}')
        for sensor in update['to_add']:
            post_member(group_id, sensor)
    else:
        print('No sensors to add.')

    if len(update['to_remove']) > 0:
        print(f'Removing sensors {', '.join({[str(x) for x in update['to_remove']]})} from {group_id}')
        for sensor in update['to_remove']:
            delete_member(group_id, sensor)
    else:
        print('No sensors to remove.')

    print(f'Group {group_id} is up to date.')



