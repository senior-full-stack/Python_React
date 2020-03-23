import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from random import randint
import json
import jwt, base64
import requests
import time, datetime
from flask_api import status
import uuid
from rfc3339 import nowtostr, now, strtotimestamp, nowtimestamp, utcformysqlfromtimestamp

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

def test_full_happy_path():
    start_time = time.time()
    #register user
    ID = str(uuid.uuid4())
    username = ID + '@dmsystems.com'
    admin_user = 'mtrapani@dmsystems.com'
    admin_pass = 'PASuccess1'
    name = ID
    password = str(uuid.uuid4())
    new_password = 'pass'
    device_id = '8c364124-487f-4e5f-8505-0d2cdca8ad86'
    device_id2 = str(uuid.uuid4())
    device_secret = 'c7bfcdd5-0603-478a-8b42-262c9f4d49a1'
    device_secret2 = str(uuid.uuid4())
    patient_name = 'Patient'
    patient_id = str(uuid.uuid4())
    sync_id_1 = str(uuid.uuid4())
    sync_id_2 = str(uuid.uuid4())
    url_base = 'http://localhost:5666/'#'http://dm.nemik.net/api/v1/'#

    device_token_data = {
        "sub" : device_id,
        "iat" : nowtimestamp()
    }

    device_token = jwt.encode(device_token_data, device_secret, algorithm='HS256')

    #post events TEST
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + device_token
        }

    data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : 1455400806, "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
    url = url_base + 'devices/sync'
    r = requests.post(url, data=json.dumps(data), headers=headers)
    
    url = url_base + 'events'
    data = {'pressure_events': [{'epoch_timestamp': 1470141327, 'message': 'left heel pressure was completely relieved'}]}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : 1455400806, "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
    url = url_base + 'devices/sync'
    r = requests.post(url, data=json.dumps(data), headers=headers)

    url = url_base + 'events'
    data = {'pressure_events': [{'epoch_timestamp': 1470141327, 'location': 'LEFT_HEEL', 'message': 'NO_PRESSURE'}]}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : 1455400806, "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
    url = url_base + 'devices/sync'
    r = requests.post(url, data=json.dumps(data), headers=headers)

    url = url_base + 'events'
    data = {'pressure_events': [{'epoch_timestamp': 1470141468, 'location': 'LEFT_HEEL', 'message': 'PRESSURE_RISING'}]}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : 1455400806, "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
    url = url_base + 'devices/sync'
    r = requests.post(url, data=json.dumps(data), headers=headers)

    url = url_base + 'events'
    data = {'pressure_events': [{'epoch_timestamp': 1470141468, 'message': 'left heel pressure is rising'}]}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : 1455400806, "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
    url = url_base + 'devices/sync'
    r = requests.post(url, data=json.dumps(data), headers=headers)

    url = url_base + 'events'
    data = {'pressure_events': [{'epoch_timestamp': 1470142544, 'message': 'left heel pressure is rising'}]}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : 1455400806, "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
    url = url_base + 'devices/sync'
    r = requests.post(url, data=json.dumps(data), headers=headers)

    url = url_base + 'events'
    data = {'pressure_events': [{'epoch_timestamp': 1470142544, 'location': 'LEFT_HEEL', 'message': 'PRESSURE_RISING'}]}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : 1455400806, "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
    url = url_base + 'devices/sync'
    r = requests.post(url, data=json.dumps(data), headers=headers)

    url = url_base + 'events'
    data = {'pressure_events': [{'epoch_timestamp': 1470144531, 'location': 'LEFT_HEEL', 'message': 'PRESSURE_RISING'}]}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : 1455400806, "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
    url = url_base + 'devices/sync'
    r = requests.post(url, data=json.dumps(data), headers=headers)

    url = url_base + 'events'
    data = {'pressure_events': [{'epoch_timestamp': 1470144531, 'message': 'left heel pressure is rising'}]}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert status.HTTP_204_NO_CONTENT == r.status_code