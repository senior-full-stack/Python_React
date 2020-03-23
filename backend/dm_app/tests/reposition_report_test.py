import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from random import randint
import json
import jwt, base64
import requests
from dateutil import rrule, tz
from datetime import datetime, time, timedelta
from flask_api import status
import uuid
from rfc3339 import nowtostr, now, strtotimestamp, nowtimestamp, utcformysqlfromtimestamp, datetimetostr

#timezone
TIMEZONE = 'America/Chicago'
USE_TIMEZONE = True


def set_tz(date):
	if USE_TIMEZONE:
		to_zone = tz.gettz(TIMEZONE)
		converted_date = date.replace(tzinfo=to_zone)
	else:
		converted_date = date
	return converted_date

def contains(list, filter):
	for x in list:
		if filter(x):
			return True
	return False

def date_to_utc_timestamp(date):
	d = set_tz(date)
	s = datetimetostr(d)
	t = strtotimestamp(s)
	return t

def test_reposition_report():
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
	patient_id2 = str(uuid.uuid4())
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
	data = {"medical_record_number": patient_id, "name" : patient_name, "gender": "cat", "DOB": "7/11/01", "unit_floor": patient_id, "bed_type": "floating", "ethnicity": "feline",
			"braden_score": "3", "mobility": "mobile", "weight": "90", "height": "175",
			"albumin_level": "some", "A1C": "yes", "hemoglobin": "5", "o2_saturation": "90", "blood_pressure": "80/120", 
			"sensor_location": "Foot", "site_assessment": "great", "sensor_removal": "nope", "units": "metric", "date_of_admission": "2016-05-12",
			"diagnosis":[{"name":"hypertension","display_name":"Hypertension","value":False},{"name":"malignancy","display_name":"Malignancy","value":False},{"name":"diabetes","display_name":"Diabetes","value":False},{"name":"heart_disease","display_name":"Heart Disease","value":False},{"name":"stroke","display_name":"Stroke","value":False},{"name":"immobility","display_name":"Immobility (stroke, paraplegic, quadriplegic)","value":False},{"name":"pvd","display_name":"PVD (Peripheral Vascular Disease)","value":False},{"name":"neuropathy","display_name":"Neuropathy","value":False},{"name":"incontinence","display_name":"Incontinence","value":False},{"name":"malnutrition","display_name":"Malnutrition","value":False},{"name":"heart_attack","display_name":"Heart attack (CAD)","value":True},{"name":"prior_skin_pressure_injury","display_name":"Prior skin pressure injury","value":True},{"name":"hip_pelvic_fracture","display_name":"Hip/pelvic fracture","value":False},{"name":"femur_fracture","display_name":"Femur fracture","value":True},{"name":"other","display_name":"Other","value":False}],
			"past_diagnosis":[{"display_name":"Hypertension","name":"hypertension","value":False},{"display_name":"Malignancy","name":"malignancy","value":False},{"display_name":"Diabetes","name":"diabetes","value":False},{"display_name":"Heart Disease","name":"heart_disease","value":False},{"display_name":"Stroke","name":"stroke","value":False},{"display_name":"Immobility (stroke, paraplegic, quadriplegic)","name":"immobility","value":False},{"display_name":"PVD (peripheral vascular disease)","name":"pvd","value":False},{"display_name":"Neuropathy","name":"neuropathy","value":False},{"display_name":"Incontinence","name":"incontinence","value":False},{"display_name":"Malnutrition","name":"malnutrition","value":False},{"display_name":"Heart attack (CAD)","name":"heart_attack","value":False},{"display_name":"Prior skin pressure injury","name":"prior_skin_pressure_injury","value":False},{"display_name":"Hip/pelvic fracture","name":"hip_pelvic_fracture","value":False},{"display_name":"Femur fracture","name":"femur_fracture","value":False},{"display_name":"Other","name":"other","value":False}],
			"medication":[{"name":"none","display_name":"None","value":False},{"name":"chemotherapy","display_name":"Chemotherapy","value":False},{"name":"radiation","display_name":"Radiation","value":False},{"name":"steroids","display_name":"Steroids","value":False},{"name":"vasopressors","display_name":"Vasopressors","value":False},{"name":"heart_rhythm","display_name":"Heart rhythm","value":False},{"name":"blood_pressure","display_name":"Blood pressure","value":False},{"name":"narcotic_pain","display_name":"Narcotic pain control","value":False},{"name":"non_narcotic_pain","display_name":"Non-narcotic pain","value":False},{"name":"hypoglycemic","display_name":"Hypoglycemic","value":False},{"name":"sleeping","display_name":"Sleeping","value":False},{"name":"constipation_relief","display_name":"Constipation relief","value":False},{"name":"anxiety_control","display_name":"Anxiety control","value":False},{"name":"antispasmodics","display_name":"Antispasmodics","value":True},{"name":"antibiotics","display_name":"Antibiotics","value":True},{"name":"other","display_name":"Other","value":False}]}
	url = url_base + 'patients'

	r = requests.post(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_200_OK == r.status_code

	patient_id = r.json()['medical_record_number']

	#register second patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"medical_record_number": patient_id2, "name" : patient_name, "gender": "cat", "DOB": "7/11/01", "unit_floor": patient_id, "bed_type": "floating", "ethnicity": "feline",
			"braden_score": "3", "mobility": "mobile", "weight": "90", "height": "175",
			"albumin_level": "some", "A1C": "yes", "hemoglobin": "5", "o2_saturation": "90", "blood_pressure": "80/120", 
			"sensor_location": "Foot", "site_assessment": "great", "sensor_removal": "nope", "units": "metric", "date_of_admission": "2016-05-12",
			"diagnosis":[{"name":"hypertension","display_name":"Hypertension","value":False},{"name":"malignancy","display_name":"Malignancy","value":False},{"name":"diabetes","display_name":"Diabetes","value":False},{"name":"heart_disease","display_name":"Heart Disease","value":False},{"name":"stroke","display_name":"Stroke","value":False},{"name":"immobility","display_name":"Immobility (stroke, paraplegic, quadriplegic)","value":False},{"name":"pvd","display_name":"PVD (Peripheral Vascular Disease)","value":False},{"name":"neuropathy","display_name":"Neuropathy","value":False},{"name":"incontinence","display_name":"Incontinence","value":False},{"name":"malnutrition","display_name":"Malnutrition","value":False},{"name":"heart_attack","display_name":"Heart attack (CAD)","value":True},{"name":"prior_skin_pressure_injury","display_name":"Prior skin pressure injury","value":True},{"name":"hip_pelvic_fracture","display_name":"Hip/pelvic fracture","value":False},{"name":"femur_fracture","display_name":"Femur fracture","value":True},{"name":"other","display_name":"Other","value":False}],
			"past_diagnosis":[{"display_name":"Hypertension","name":"hypertension","value":False},{"display_name":"Malignancy","name":"malignancy","value":False},{"display_name":"Diabetes","name":"diabetes","value":False},{"display_name":"Heart Disease","name":"heart_disease","value":False},{"display_name":"Stroke","name":"stroke","value":False},{"display_name":"Immobility (stroke, paraplegic, quadriplegic)","name":"immobility","value":False},{"display_name":"PVD (peripheral vascular disease)","name":"pvd","value":False},{"display_name":"Neuropathy","name":"neuropathy","value":False},{"display_name":"Incontinence","name":"incontinence","value":False},{"display_name":"Malnutrition","name":"malnutrition","value":False},{"display_name":"Heart attack (CAD)","name":"heart_attack","value":False},{"display_name":"Prior skin pressure injury","name":"prior_skin_pressure_injury","value":False},{"display_name":"Hip/pelvic fracture","name":"hip_pelvic_fracture","value":False},{"display_name":"Femur fracture","name":"femur_fracture","value":False},{"display_name":"Other","name":"other","value":False}],
			"medication":[{"name":"none","display_name":"None","value":False},{"name":"chemotherapy","display_name":"Chemotherapy","value":False},{"name":"radiation","display_name":"Radiation","value":False},{"name":"steroids","display_name":"Steroids","value":False},{"name":"vasopressors","display_name":"Vasopressors","value":False},{"name":"heart_rhythm","display_name":"Heart rhythm","value":False},{"name":"blood_pressure","display_name":"Blood pressure","value":False},{"name":"narcotic_pain","display_name":"Narcotic pain control","value":False},{"name":"non_narcotic_pain","display_name":"Non-narcotic pain","value":False},{"name":"hypoglycemic","display_name":"Hypoglycemic","value":False},{"name":"sleeping","display_name":"Sleeping","value":False},{"name":"constipation_relief","display_name":"Constipation relief","value":False},{"name":"anxiety_control","display_name":"Anxiety control","value":False},{"name":"antispasmodics","display_name":"Antispasmodics","value":True},{"name":"antibiotics","display_name":"Antibiotics","value":True},{"name":"other","display_name":"Other","value":False}]}
	url = url_base + 'patients'

	r = requests.post(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_200_OK == r.status_code

	patient_id2 = r.json()['medical_record_number']

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

	#register device 2

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"serial": device_id2, "secret" : device_secret2}
	url = url_base + 'devices'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	device_token_data = {
		"sub" : device_id2,
		"iat" : nowtimestamp()
	}

	device_token2 = jwt.encode(device_token_data, device_secret2, algorithm='HS256')

	#assign device to patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = ""
	url = url_base + 'patients/' + patient_id + '/assign/' + device_id + '/'

	r = requests.put(url, data=None, headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#assign device2 to patient2
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = ""
	url = url_base + 'patients/' + patient_id2 + '/assign/' + device_id2 + '/'

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

	assert status.HTTP_200_OK == r.status_code

	#sync device 2
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token2
		}
	data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.01', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
	url = url_base + 'devices/sync'

	r = requests.post(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_200_OK == r.status_code

	n = datetime.now()
	n = n.replace(minute=0, second=0, microsecond=0, hour=0)


	#post patient 1 alarms
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}

	data =  {'pressure_events': [{'message': 'PRESSURE_ALARM', 'epoch_timestamp': date_to_utc_timestamp(n.replace(minute=1)), 'location': 'RIGHT_ELBOW'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#post patient 1 clear
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}

	data =  {'pressure_events': [{'message': 'PRESSURE_FALLING', 'epoch_timestamp': date_to_utc_timestamp(n.replace(minute=6)), 'location': 'RIGHT_ELBOW'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#post patient 1 simultaneous alarms 
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}

	data =  {'pressure_events': [{'message': 'PRESSURE_ALARM', 'epoch_timestamp': date_to_utc_timestamp(n.replace(minute=2)), 'location': 'LEFT_ELBOW'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#post patient 1 simultaneous clear
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}

	data =  {'pressure_events': [{'message': 'PRESSURE_FALLING', 'epoch_timestamp': date_to_utc_timestamp(n.replace(minute=5)), 'location': 'LEFT_ELBOW'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#post patient 2 alarm
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token2
		}

	data =  {'pressure_events': [{'message': 'PRESSURE_ALARM', 'epoch_timestamp': date_to_utc_timestamp(n.replace(minute=4)), 'location': 'RIGHT_ELBOW'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#post patient 2 clear
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token2
		}

	data =  {'pressure_events': [{'message': 'PRESSURE_FALLING', 'epoch_timestamp': date_to_utc_timestamp(n.replace(minute=11)), 'location': 'RIGHT_ELBOW'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#post patient 2 turned
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token2
		}

	data =  {'pressure_events': [{'message': 'PATIENT WAS TURNED BY CAREGIVER', 'epoch_timestamp': date_to_utc_timestamp(n.replace(minute=12)), 'location': 'RIGHT_ELBOW'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#post patient 2 alarm over hour
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token2
		}

	data =  {'pressure_events': [{'message': 'PRESSURE_ALARM', 'epoch_timestamp': date_to_utc_timestamp(n.replace(minute=55)), 'location': 'RIGHT_ELBOW'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#post patient 2 turned over hour
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token2
		}

	data =  {'pressure_events': [{'message': 'PATIENT WAS TURNED BY CAREGIVER', 'epoch_timestamp': date_to_utc_timestamp(n.replace(minute=59)), 'location': 'RIGHT_ELBOW'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#post patient 2 clear over hour
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token2
		}

	data =  {'pressure_events': [{'message': 'PRESSURE_FALLING', 'epoch_timestamp': date_to_utc_timestamp(n.replace(hour=1,minute=4)), 'location': 'RIGHT_ELBOW'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code



	#log in user
	headers = {'Content-Type' : 'application/json'}
	data = {"email": admin_user ,"password": admin_pass}
	url = url_base + 'users/login'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_200_OK == r.status_code
	assert 'token' in r.json()

	admin_token = r.json()['token']

	#get reposition report for unit
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'repositionreports?start=' + str(n.date()) + ' 6:0&end=' + str(n.date()) + ' 6:0&unit_floor=' + patient_id

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	print r.json()['reposition_reports']
	for x in r.json()['reposition_reports']:
		if x['description'] == 'Total Repos':
			assert x['hour0'] == 3
		if x['description'] == 'Patient Repos':
			assert x['hour0'] == 2
		if x['description'] == 'Caregiver Repos':
			assert x['hour0'] == 1
			assert x['hour1'] == 1

	#get alarm response report for patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'alarmresponsereports/' + patient_id + '/?start=' + str(n.date()) + ' 6:0&end=' + str(n.date()) + ' 6:0'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get reposition report for patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'repositionreports/' + patient_id + '/?start=' + str(n.date()) + ' 6:0&end=' + str(n.date()) + ' 6:0'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get alarm response report for unit
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'alarmresponsereports?start=' + str(n.date()) + ' 6:0&end=' + str(n.date()) + ' 6:0&unit_floor=' + patient_id

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	print r.json()['alarm_response_reports']
	for x in r.json()['alarm_response_reports']:
		if x['description'] == 'Alarms':
			assert x['hour0'] == 4
		if x['description'] == 'Minutes of Alarming':
			assert x['hour0'] == 19
			assert x['hour1'] == 5

	#get reposition report for unit
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'repositionreports?start=' + str(n.date()) + ' 6:0&end=' + str(n.date()) + ' 6:0&unit_floor=3B'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	print r.json()['reposition_reports']


	#get alarm response report for wrong unit
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'alarmresponsereports?start=' + str(n.date()) + ' 6:0&end=' + str(n.date()) + ' 6:0&unit_floor=Z'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	print r.json()['alarm_response_reports']

	#get reposition report for wrong unit
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'repositionreports?start=' + str(n.date()) + ' 6:0&end=' + str(n.date()) + ' 6:0&unit_floor=Z'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	print r.json()['reposition_reports']
	#assert 'thing' in r.json()['alarm_response_reports'][0]

	#get reposition report for all
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'repositionreports?start=' + str(n.date()) + ' 6:0&end=' + str(n.date()) + ' 6:0'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get alarm response report for all
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'alarmresponsereports?start=' + str(n.date()) + ' 6:0&end=' + str(n.date()) + ' 6:0'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	print r.json()['alarm_response_reports']

	#delete patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'patients/' + patient_id

	r = requests.delete(url, headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#delete patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'patients/' + patient_id2

	r = requests.delete(url, headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code
