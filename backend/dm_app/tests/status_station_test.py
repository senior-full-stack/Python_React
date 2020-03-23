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

def test_status_station():
    start_time = time.time()
    #register user
    ID = str(uuid.uuid4())
    username = ID + '@dmsystems.com'
    admin_user = 'klein1jonathan@gmail.com'
    admin_pass = 'dmpasspasspass'
    name = ID
    password = str(uuid.uuid4())
    new_password = 'pass'
    device_id = str(uuid.uuid4())
    device_id2 = str(uuid.uuid4())
    device_secret = str(uuid.uuid4())
    device_secret2 = str(uuid.uuid4())
    patient_name = 'Patient'
    patient_id = str(uuid.uuid4())
    sync_id_1 = str(uuid.uuid4())
    sync_id_2 = str(uuid.uuid4())
    url_base = 'http://localhost:5666/'#'http://dm.nemik.net/api/v1/'#

    #log in user
    headers = {'Content-Type' : 'application/json'}
    data = {"email": admin_user ,"password": admin_pass}
    url = url_base + 'users/login'

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert status.HTTP_200_OK == r.status_code
    assert 'token' in r.json()

    init_user_token = r.json()['token']

    #create new user
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + init_user_token
        }

    data = {"email": username ,"name": name ,"password": password, "phone_number": "+18478454531"}
    url = url_base + 'users'

    r = requests.post(url, data=json.dumps(data), headers=headers)

    assert status.HTTP_204_NO_CONTENT == r.status_code

    #log in user
    data = {"email": username ,"password": password}
    url = url_base + 'users/login'

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert status.HTTP_200_OK == r.status_code
    assert 'token' in r.json()

    user_token = r.json()['token']

    #register patient
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + user_token
        }
    data = {"medical_record_number": patient_id, "name" : patient_name, "gender": "cat", "DOB": "7-11-01", "unit_floor": "3B", "bed_type": "floating", "ethnicity": "feline",
            "braden_score": "3", "mobility": "mobile", "weight": "90", "height": "175",
            "albumin_level": "some", "A1C": "yes", "hemoglobin": "5", "o2_saturation": "90", "blood_pressure": "80/120", 
            "sensor_location": "Foot", "site_assessment": "great", "sensor_removal": "nope", "units": "metric", "date_of_admission": "2016-05-12",
            "diagnosis":[{"name":"respiratory_failure","display_name":"Respiratory Failure","value":False},{"name":"skin_flap_graft","display_name":"Skin Flap / Graft","value":False},{"name":"hypertension","display_name":"Hypertension","value":False},{"name":"malignancy","display_name":"Malignancy","value":False},{"name":"diabetes","display_name":"Diabetes","value":False},{"name":"heart_disease","display_name":"Heart Disease","value":False},{"name":"stroke","display_name":"Stroke","value":False},{"name":"immobility","display_name":"Immobility (stroke, paraplegic, quadriplegic)","value":False},{"name":"pvd","display_name":"PVD (Peripheral Vascular Disease)","value":False},{"name":"neuropathy","display_name":"Neuropathy","value":False},{"name":"incontinence","display_name":"Incontinence","value":False},{"name":"malnutrition","display_name":"Malnutrition","value":False},{"name":"heart_attack","display_name":"Heart attack (CAD)","value":True},{"name":"prior_skin_pressure_injury","display_name":"Prior skin pressure injury","value":True},{"name":"hip_pelvic_fracture","display_name":"Hip/pelvic fracture","value":False},{"name":"femur_fracture","display_name":"Femur fracture","value":True},{"name":"other","display_name":"Other","value":False}],
            "past_diagnosis":[{"name":"respiratory_failure","display_name":"Respiratory Failure","value":False},{"name":"skin_flap_graft","display_name":"Skin Flap / Graft","value":False},{"display_name":"Hypertension","name":"hypertension","value":False},{"display_name":"Malignancy","name":"malignancy","value":False},{"display_name":"Diabetes","name":"diabetes","value":False},{"display_name":"Heart Disease","name":"heart_disease","value":False},{"display_name":"Stroke","name":"stroke","value":False},{"display_name":"Immobility (stroke, paraplegic, quadriplegic)","name":"immobility","value":False},{"display_name":"PVD (peripheral vascular disease)","name":"pvd","value":False},{"display_name":"Neuropathy","name":"neuropathy","value":False},{"display_name":"Incontinence","name":"incontinence","value":False},{"display_name":"Malnutrition","name":"malnutrition","value":False},{"display_name":"Heart attack (CAD)","name":"heart_attack","value":False},{"display_name":"Prior skin pressure injury","name":"prior_skin_pressure_injury","value":False},{"display_name":"Hip/pelvic fracture","name":"hip_pelvic_fracture","value":False},{"display_name":"Femur fracture","name":"femur_fracture","value":False},{"display_name":"Other","name":"other","value":False}],
            "medication":[{"name":"none","display_name":"None","value":False},{"name":"chemotherapy","display_name":"Chemotherapy","value":False},{"name":"radiation","display_name":"Radiation","value":False},{"name":"steroids","display_name":"Steroids","value":False},{"name":"vasopressors","display_name":"Vasopressors","value":False},{"name":"heart_rhythm","display_name":"Heart rhythm","value":False},{"name":"blood_pressure","display_name":"Blood pressure","value":False},{"name":"narcotic_pain","display_name":"Narcotic pain control","value":False},{"name":"non_narcotic_pain","display_name":"Non-narcotic pain","value":False},{"name":"hypoglycemic","display_name":"Hypoglycemic","value":False},{"name":"sleeping","display_name":"Sleeping","value":False},{"name":"constipation_relief","display_name":"Constipation relief","value":False},{"name":"anxiety_control","display_name":"Anxiety control","value":False},{"name":"antispasmodics","display_name":"Antispasmodics","value":True},{"name":"antibiotics","display_name":"Antibiotics","value":True},{"name":"other","display_name":"Other","value":False}]}
    url = url_base + 'patients'

    r = requests.post(url, data=json.dumps(data), headers=headers)

    assert status.HTTP_200_OK == r.status_code

    patient_id = r.json()['medical_record_number']

    #register device

    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + user_token
        }
    data = {"serial": device_id, "secret" : device_secret}
    url = url_base + 'devices'

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert status.HTTP_204_NO_CONTENT == r.status_code

    device_token_data = {
        "sub" : device_id,
        "iat" : nowtimestamp()
    }

    device_token = jwt.encode(device_token_data, device_secret, algorithm='HS256')

    #assign device to patient
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + user_token
        }
    data = ""
    url = url_base + 'patients/' + patient_id + '/assign/' + device_id + '/'

    r = requests.put(url, data=None, headers=headers)

    assert status.HTTP_204_NO_CONTENT == r.status_code

    #sync
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + device_token
        }
    data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.01', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
    url = url_base + 'devices/sync'

    r = requests.post(url, data=json.dumps(data), headers=headers)

    assert status.HTTP_204_NO_CONTENT == r.status_code

    #post events
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + device_token
        }

    data =  {'pressure_events': [{'message': 'left elbow pressure was completely relieved', 'epoch_timestamp': 1461268371}, {'message': 'PRESSURE_ALARM', 'epoch_timestamp': 1461268357, 'location': 'LEFT_ELBOW'}, {'message': 'PRESSURE_ALARM', 'epoch_timestamp': 1461268351, 'location': 'RIGHT_ELBOW'}, {'message': 'Patient was turned by caregiver', 'epoch_timestamp': 1461268358}, {'message': 'NO_PRESSURE', 'epoch_timestamp': 1461268322, 'location': 'LEFT_ELBOW'}, {'message': 'left elbow pressure was too high', 'epoch_timestamp': 1461268357}, {'message': 'NO_PRESSURE', 'epoch_timestamp': 1461268316, 'location': 'RIGHT_ELBOW'}, {'message': 'right elbow pressure was too high', 'epoch_timestamp': 1461268351}]}
    url = url_base + 'events'

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert status.HTTP_204_NO_CONTENT == r.status_code

    #post events
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + device_token
        }

    data =  {'pressure_events': [{'message': 'NO_PRESSURE', 'epoch_timestamp': 1461268376, 'location': 'RIGHT_ELBOW'}]}
    url = url_base + 'events'

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert status.HTTP_204_NO_CONTENT == r.status_code

    #post events
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + device_token
        }

    data =  {'pressure_events': [{'message': 'right elbow pressure was completely relieved', 'epoch_timestamp': 1461268376}]}
    url = url_base + 'events'

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert status.HTTP_204_NO_CONTENT == r.status_code

    #get status station
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + user_token
        }
    url = url_base + 'status-station'

    r = requests.get(url, headers=headers)
    assert status.HTTP_200_OK == r.status_code