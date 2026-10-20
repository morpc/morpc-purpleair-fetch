from unittest.mock import Mock

import pandas as pd
import pytest
import requests


def fake_response(status_code, json=None):
    r = Mock(status_code=status_code, content=b'', url='https://api.purpleair.com/test')
    if isinstance(json, Exception):
        r.json.side_effect = json
    else:
        r.json.return_value = json
    return r


def history_json(purpleair, time_stamps):
    return {
        'fields': ['time_stamp'] + purpleair.DATA_FIELDS_QUERY,
        'data': [[ts] + [1.0] * len(purpleair.DATA_FIELDS_QUERY) for ts in time_stamps],
    }


GROUP_DETAILS = {'members': [
    {'id': 10, 'sensor_index': 33773, 'created': 0},
    {'id': 20, 'sensor_index': 12345, 'created': 0},
]}


def test_env_with_blank_line_is_read(purpleair):
    assert purpleair.read_header == {'X-API-Key': 'test-read'}
    assert purpleair.write_header == {'X-API-Key': 'test-write'}


def test_data_fields_map_has_unique_columns(purpleair):
    values = list(purpleair.DATA_FIELDS_MAP.values())
    assert len(values) == len(set(values))


def test_get_json_safely_raises_http_error(purpleair, monkeypatch):
    monkeypatch.setattr(requests, 'get', lambda *a, **k: fake_response(500))
    with pytest.raises(requests.HTTPError):
        purpleair.get_json_safely('https://api.purpleair.com/test', {})


def test_get_json_safely_raises_json_decode_error(purpleair, monkeypatch):
    bad_json = requests.JSONDecodeError('Expecting value', '', 0)
    monkeypatch.setattr(requests, 'get', lambda *a, **k: fake_response(200, bad_json))
    with pytest.raises(requests.JSONDecodeError):
        purpleair.get_json_safely('https://api.purpleair.com/test', {})


def test_delete_safely_sends_delete(purpleair, monkeypatch):
    delete = Mock(return_value=fake_response(204))
    monkeypatch.setattr(requests, 'delete', delete)
    monkeypatch.setattr(requests, 'post', Mock(side_effect=AssertionError('used POST')))
    purpleair.delete_safely('https://api.purpleair.com/test', {})
    delete.assert_called_once()


def test_update_group_members_removes_sensors(purpleair, monkeypatch):
    delete_member = Mock()
    monkeypatch.setattr(purpleair, 'delete_member', delete_member)
    purpleair.update_group_members({'to_add': [], 'to_remove': [999]}, group_id=1)
    delete_member.assert_called_once_with(1, 999)


def test_check_interval_keeps_partial_last_period(purpleair):
    interval = pd.Interval(pd.Timestamp('2025-01-01'), pd.Timestamp('2025-02-15'))
    intervals = purpleair.check_interval(interval, average=0)
    assert [(i.left, i.right) for i in intervals] == [
        (pd.Timestamp('2025-01-01'), pd.Timestamp('2025-01-31')),
        (pd.Timestamp('2025-01-31'), pd.Timestamp('2025-02-15')),
    ]


@pytest.mark.parametrize('average', [360, 1440, 10080, 43200, 525600])
def test_check_interval_year_limits(purpleair, average):
    interval = pd.Interval(pd.Timestamp('2025-01-01'), pd.Timestamp('2025-01-02'))
    assert purpleair.check_interval(interval, average=average) == interval


def test_sensor_history_sends_utc_epoch_timestamps(purpleair, monkeypatch):
    get = Mock(return_value=history_json(purpleair, [1756684800]))
    monkeypatch.setattr(purpleair, 'get_json_safely', get)
    purpleair.get_sensor_history(33773, start='2025-09-01', end='2025-10-01')
    params = get.call_args.kwargs['params']
    assert int(params['start_timestamp']) == 1756684800
    assert int(params['end_timestamp']) == 1759276800


def test_member_history_sends_utc_epoch_timestamps(purpleair, monkeypatch):
    get = Mock(return_value=history_json(purpleair, [1756684800]))
    monkeypatch.setattr(purpleair, 'get_json_safely', get)
    monkeypatch.setattr(purpleair, 'get_group_details', lambda group_id: GROUP_DETAILS)
    df = purpleair.get_member_history(1, 10, start='2025-09-01', end='2025-10-01')
    params = get.call_args.kwargs['params']
    assert int(params['start_timestamp']) == 1756684800
    assert int(params['end_timestamp']) == 1759276800
    assert df['index'].tolist() == [33773]


def test_members_history_combines_all_members(purpleair, monkeypatch):
    monkeypatch.setattr(purpleair, 'get_group_details', lambda group_id: GROUP_DETAILS)
    monkeypatch.setattr(purpleair, 'get_json_safely', lambda *a, **k: history_json(purpleair, [1756684800]))
    df = purpleair.get_members_history(1, start='2025-09-01', end='2025-10-01')
    assert df['index'].tolist() == [33773, 12345]
    assert 'pm025_atm_a' in df.columns


def test_sensorid_from_memberid_ignores_extra_member_fields(purpleair, monkeypatch):
    details = {'members': [{'id': 10, 'sensor_index': 33773, 'created': 0, 'extra': 'x'}]}
    monkeypatch.setattr(purpleair, 'get_group_details', lambda group_id: details)
    assert purpleair.sensorid_from_memberid(1, pd.Series([10])).tolist() == [33773]
