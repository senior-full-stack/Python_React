import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from random import randint
import json
import jwt, base64
import requests
import time, datetime
from datetime import timedelta
from flask_api import status
import uuid
from rfc3339 import nowtostr, now, strtotimestamp, nowtimestamp, utcformysqlfromtimestamp

def contains(list, filter):
	for x in list:
		if filter(x):
			return True
	return False

def test_full_happy_path():
	#register user
	ID = str(uuid.uuid4())
	username = ID + '@dmsystems.com'
	admin_user = 'jflores@digitalhealths.com'
	admin_pass = 'pasuccess1'
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
	url_base = 'http://localhost:5666/'
	today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
	yesterday = datetime.datetime.now() - timedelta(days=1)
	yesterday = yesterday.strftime('%Y-%m-%d %H:%M')


	#datetime.datetime.now().isoformat()

	#test health
	headers = {
		'Content-Type' : 'application/json'
		}

	url = url_base + 'health'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

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

	# fail log in
	data = {"email": 'fake' ,"password": 'user'}
	url = url_base + 'users/login'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_401_UNAUTHORIZED == r.status_code

	#log in user
	data = {"email": username ,"password": password}
	url = url_base + 'users/login'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_200_OK == r.status_code
	assert 'token' in r.json()

	user_token = r.json()['token']

	#update user
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"eula_accepted": True}
	url = url_base + 'users/' + username

	r = requests.put(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#attempt to update different user w/out permission
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"eula_accepted": True}
	url = url_base + 'users/' + admin_user

	r = requests.put(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_403_FORBIDDEN == r.status_code
	assert r.json()['error'] == 'You do not have permission to change another user'

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

	#update patient
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

	r = requests.put(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#get patients
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'patients'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get user
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'users/' + username

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	assert True == r.json()['eula_accepted']

	#get users
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'users'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

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

	#try to register same device

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_409_CONFLICT == r.status_code

	# get devices

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	# get unassigned devices

	url = url+ "?unassigned=True"
	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	# update device

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"language": "es"}
	url = url_base + 'devices/' + device_id

	r = requests.put(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	# get single device

	url = url_base + 'devices/' + device_id
	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code
	assert r.json()['language'] == 'es'

	#unassign unassigned patient

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = ""
	url = url_base + 'patients/' + patient_id + '/unassign/'

	r = requests.put(url, data=None, headers=headers)

	assert status.HTTP_400_BAD_REQUEST == r.status_code
	assert r.json()['error'] == 'patient not assigned'

	#unassign unassigned device

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = ""
	url = url_base + 'devices/' + device_id + '/unassign/'

	r = requests.put(url, data=None, headers=headers)

	assert status.HTTP_400_BAD_REQUEST == r.status_code
	assert r.json()['error'] == 'device not assigned'

	#assign device to patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = ""
	url = url_base + 'patients/' + patient_id + '/assign/' + device_id + '/'

	r = requests.put(url, data=None, headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#unassign patient

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = ""
	url = url_base + 'patients/' + patient_id + '/unassign/'

	r = requests.put(url, data=None, headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#get unassigned patients
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'patients?unassigned=True'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	found = False
	for patient in r.json()['patients']:
		if patient['pa_id'] == patient_id:
			found = True
	assert found
	#assert [x for x in r.json()['patients'] if x['medical_record_number'] == 30]
	#assert contains(r.json()['patients'], lambda x: x.medical_record_number == patient_id)

	#assign device to patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = ""
	url = url_base + 'patients/' + patient_id + '/assign/' + device_id + '/'

	r = requests.put(url, data=None, headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#unassign device

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = ""
	url = url_base + 'devices/' + device_id + '/unassign/'

	r = requests.put(url, data=None, headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#assign device to patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = ""
	url = url_base + 'patients/' + patient_id + '/assign/' + device_id + '/'

	r = requests.put(url, data=None, headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#test bad device token
	bad_device_token_data = {
		"sub" : device_id,
		"iat" : nowtimestamp()
	}

	bad_device_token = jwt.encode(device_token_data, "device_secret", algorithm='HS256')
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + bad_device_token
		}
	data = {}
	url = url_base + 'devices/sync'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_401_UNAUTHORIZED == r.status_code

		#post patient note
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"pa_id" : patient_id, "patient_site" : "SACRUM", "dressing_application_surface" : "Patient skin",
	"device_surrounding_dressing" : "None", "reason_for_dressing_change" : "Dressing not changed", 
	"reason_for_dressing_removal" : "Not applicable", "tablet_issues" : "None", "sensor_issues" : "None",
	"support_contacted" : False, "occurred" : "2016-05-04T09:44:00.000Z", "comments" : "All is well"}

	url = url_base + 'patientnotes/'

	r = requests.post(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#get patient note for body location
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'patientnotes/' + patient_id + '/SACRUM/'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	note_id = r.json()[0]['id']


	#update patient notes
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"id" : note_id, "pa_id" : patient_id, "patient_site" : "SACRUM", "dressing_application_surface" : "Patient skin",
	"device_surrounding_dressing" : "None", "reason_for_dressing_change" : "Dressing not changed", 
	"reason_for_dressing_removal" : "Not applicable", "tablet_issues" : "None", "sensor_issues" : "None",
	"support_contacted" : False, "occurred" : "2016-05-04T09:44:00.000Z", "comments" : "All is not well"}

	url = url_base + 'patientnotes/'

	r = requests.put(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#get default sync
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}
	url = url_base + 'default/sync/'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#sync
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}
	data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.01', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
	url = url_base + 'devices/sync'

	r = requests.post(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#sync again
	data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016-08-02T14:05:58Z', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016-08-02T14:05:58Z', "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": 'no sensor assigned', "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }

	r = requests.post(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#post events
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}

	#data = { "pressure_events": [ { "message": "NO_PRESSURE", "location": "LEFT_HEEL", "epoch_timestamp": 1453994012 }, { "message": "Patient was turned by caregiver", "epoch_timestamp": 1453825340 }, { "message": "Patient was turned by caregiver", "epoch_timestamp": 1453825399 }, { "message": "Monitoring was paused", "epoch_timestamp": 1453825382 }, { "message": "Monitoring was resumed", "epoch_timestamp": 1453840858 }, { "message": "Monitoring was resumed", "epoch_timestamp": 1453825389 }, { "message": "PRESSURE_RISING", "location": "LEFT_HEEL", "epoch_timestamp": 1453993998 }, { "message": "Monitoring was paused", "epoch_timestamp": 1453840847 } ] }
	data = {'pressure_events': [{'message': 'PRESSURE_RISING', 'epoch_timestamp': 1455401161, 'location': 'SKULL'}, {'message': 'PRESSURE_FALLING', 'epoch_timestamp': 1455400870, 'location': 'SKULL'}, {'message': 'NO_PRESSURE', 'epoch_timestamp': 1455400935, 'location': 'SKULL'}, {'message': 'PRESSURE_FALLING', 'epoch_timestamp': 1455400560, 'location': 'SKULL'}, {'message': 'PRESSURE_ALARM', 'epoch_timestamp': 1455400550, 'location': 'SKULL'}, {'message': 'PRESSURE_ALARM', 'epoch_timestamp': 1455400861, 'location': 'SKULL'}, {'message': 'PRESSURE_RISING', 'epoch_timestamp': 1455400806, 'location': 'SKULL'}, {'message': 'PRESSURE_RISING', 'epoch_timestamp': 1455400490, 'location': 'SKULL'}]}
	url = url_base + 'events'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#get events
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'events'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get events for patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'events?medical_record_number=' + patient_id

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	assert patient_id == r.json()['events'][0]['medical_record_number']

	#update global device settings
	alarm_duration = randint(1,10)

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"alarm_duration": alarm_duration ,"alarm_volume": 'loud', "alarm_sound" : 'voice', 'language' : 'en'}
	url = url_base + 'default/devices/settings'

	r = requests.put(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#get device settings with user token

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	assert alarm_duration == r.json()['alarm_duration']

	#get device settings with device token
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	assert alarm_duration == r.json()['alarm_duration']

	#update global location settings
	alarm_multiple = randint(1,10)

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"type":"SWITCH_TYPE", "JSID":"location", "alarm_clear_multiple":alarm_multiple, "alarm_threshold_minutes":60, 
			"pressure_state":"NO_PRESSURE", "wound_stage":"", "is_wound":False, "has_previous_alert":False,
			"site_assessment":'', "sensor_removal":None, "wound_measurement":"", "existing_wound":False, "wound_alarm_threshold_minutes":5,
			 "wound_alarm_clear_multiple":5, "previous_alarm_threshold_hours":24}
	url = url_base + 'default/bodylocations/SKULL/'

	r = requests.put(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#get location settings with user token

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	assert alarm_multiple == r.json()['alarm_clear_multiple']

	#get location settings with device token
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	assert alarm_multiple == r.json()['alarm_clear_multiple']

	#get device sync with device token
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}

	url = url_base + 'default/sync/'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get body locations for patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'patients/' + patient_id + '/bodylocations/'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get specific body location
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'patients/' + patient_id + '/bodylocations/left_heel'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code
	body_location_id = r.json()['id']

	time.sleep(1)

	#update specific body location
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'patients/' + patient_id + '/bodylocations/left_heel'

	data = { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2866, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }
	

	r = requests.put(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#sync to test last web sync
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}
	data = { "sensors": [ { 'wound_is_existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : '2016.01.02', "too_much_data" : True, "has_previous_alert": False, "wound_stage" : 1, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "SWITCH_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "sensor_serial": sync_id_1, "JSID": "left_heel", "alarm_clear_multiple": 2, "alarm_threshold_minutes": 1, "battery": 2865, "binary_state": False, "distance": 0.022618642, "fast_blink": False, "force_state": 0 }, { 'existing': True, 'wound_measurement': '3x3x3', 'wound_existing_since' : 1455400806, "has_previous_alert": False,  "wound_stage" : 2, "is_wound" : True, "under_pressure_milliseconds": 0, "type": "FORCE_TYPE", "stopped": False, "pressure_state": "NO_PRESSURE", "id": sync_id_2, "JSID": "sacrum", "alarm_clear_multiple": 4, "alarm_threshold_minutes": 60, "battery": 2640, "binary_state": False, "distance": 1.017953, "fast_blink": False, "force_state": 8208 } ], "globals": { "language": "es", "alarm_volume": "normal", "alarm_sound": "voice", "alarm_duration": "2" } }
	url = url_base + 'devices/sync'

	r = requests.post(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'patients/' + patient_id +'/'

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code


	#get patient reports
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'patientinforeports'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get patient info report for single patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'patientinforeports/' + patient_id +'/'

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	#get patient info report with start and end date
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'patientinforeports?start=' + yesterday + '&end=' + today

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	#get body location history reports
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'bodylocationhistoryreports'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get body location history report for single patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'bodylocationhistoryreports/' + patient_id +'/'

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	#get body location history report with start and end date
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'bodylocationhistoryreports?start=' + yesterday + '&end=' + today

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	#get pu reports
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'pustatusreports'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get pu status report with start and end date
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'pustatusreports?start=' + yesterday + '&end=' + today

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	#get pu reports for patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'pustatusreports/' + patient_id +'/'

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	#get event reports
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'eventreports'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get event report with start and end date
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'eventreports?start=' + yesterday + '&end=' + today

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	#get event reports for patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'eventreports/' + patient_id

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get report token
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'download-token/'

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	report_email = r.json()['email']
	report_expiration = r.json()['expiration']
	report_token = r.json()['token']

	time.sleep(1)

	#get event reports in csv format
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'eventreports?format=csv&email='+report_email+'&expiration='+str(report_expiration)+'&token='+report_token

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code


	#get event for patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'pustatusreports/' + patient_id +'/'

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	#change password
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}

	data = {"new_password": new_password ,"old_password": password}
	url = url_base + 'users/' + username + '/password/'

	r = requests.put(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#update user password with admin token
	data = {"email": admin_user ,"password": admin_pass}
	url = url_base + 'users/login'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_200_OK == r.status_code
	assert 'token' in r.json()

	admin_token = r.json()['token']

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	data = {"password": 'whatever'}
	url = url_base + 'users/' + username

	r = requests.put(url, data=json.dumps(data), headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code

	#update admin defaults
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	data = {"unit_floor": '["1","1A","2B","3C","4D","Dev1","DevS","G Unit","Unit up","moon unit","you unit"]'}
	url = url_base + 'admin'

	r = requests.put(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#get admin defaults
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'admin'

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	#try update admin defaults with caregiver token
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"unit_floor": '["one", "two", "three"]'}
	url = url_base + 'admin'

	r = requests.put(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_403_FORBIDDEN == r.status_code

	#associate patient with user
	# headers = {
	# 	'Content-Type' : 'application/json',
	# 	'Authorization' : 'Bearer ' + user_token
	# 	}
	# data = ""
	# url = url_base + 'users/' + username + '/patients/' + patient_id + '/'

	# r = requests.put(url, data=None, headers=headers)

	# assert status.HTTP_204_NO_CONTENT == r.status_code

	#register second device

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"serial": device_id2, "secret" : device_secret2}
	url = url_base + 'devices'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#"delete" device

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'devices/' + device_id

	r = requests.delete(url, headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#"delete" device 2

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'devices/' + device_id2

	r = requests.delete(url, headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#reregister second device

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"serial": device_id2, "secret" : device_secret2}
	url = url_base + 'devices'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#reregister device

	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = {"serial": device_id, "secret" : device_secret}
	url = url_base + 'devices'

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#assign device to patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	data = ""
	url = url_base + 'patients/' + patient_id + '/assign/' + device_id + '/'

	r = requests.put(url, data=None, headers=headers)

	assert status.HTTP_204_NO_CONTENT == r.status_code


	#post events
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + device_token
		}

	data =  {'pressure_events': [{'message': 'NO_PRESSURE', 'epoch_timestamp': 1461268371, 'location': 'LEFT_ELBOW'}, {'message': 'PRESSURE_ALARM', 'epoch_timestamp': 1461268357, 'location': 'LEFT_ELBOW'}, {'message': 'PRESSURE_ALARM', 'epoch_timestamp': 1461268351, 'location': 'RIGHT_ELBOW'}, {'message': 'Patient was turned by caregiver', 'epoch_timestamp': 1461268358}, {'message': 'NO_PRESSURE', 'epoch_timestamp': 1461268322, 'location': 'LEFT_ELBOW'}, {'message': 'left elbow pressure was too high', 'epoch_timestamp': 1461268357}, {'message': 'NO_PRESSURE', 'epoch_timestamp': 1461268316, 'location': 'RIGHT_ELBOW'}, {'message': 'right elbow pressure was too high', 'epoch_timestamp': 1461268351}]}
	url = url_base + 'events'

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

	#get timeline
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'timelines?medical_record_number=' + patient_id

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code
	assert 'name' in r.json()

	#get outcome
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'outcomes/' + patient_id + '/'

	r = requests.get(url, headers=headers)
	assert status.HTTP_200_OK == r.status_code

	#deactivate
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'deactivate/' + patient_id + '/'
	data = {"status": "Inactive" ,"occurred": '2016-05-04T09:44:00.000Z', "reason" : 'because', 'sensors_collected' : False, 
			'sensors_not_collected_reason': 'because', 'reason_other': 'also because'}

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#deactivate
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'deactivate/' + patient_id + '/'
	data = {"status": "Inactive" ,"occurred": '2016-05-04T09:44:00.000Z', "reason" : 'because', 'sensors_collected' : False, 
			'sensors_not_collected_reason': 'because', 'reason_other': 'also because'}

	r = requests.post(url, data=json.dumps(data), headers=headers)
	assert status.HTTP_200_OK == r.status_code


	#check if user in get all users
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'users/'

	r = requests.get(url, headers=headers)
	users = r.json()['users']
	found_user = False
	print username
	for u in users:
		print u['email']
		if u['email'] == username:
			found_user = True
	assert True == found_user

	#delete user
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'users/' + username

	r = requests.delete(url, headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#try deleted user token
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + user_token
		}
	url = url_base + 'status-station'

	r = requests.get(url, headers=headers)
	assert status.HTTP_401_UNAUTHORIZED == r.status_code

	#try to get deleted user
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'users/' + username

	r = requests.get(url, headers=headers)
	assert status.HTTP_404_NOT_FOUND == r.status_code

	#make sure user not returned in get users
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'users/'

	r = requests.get(url, headers=headers)
	users = r.json()['users']
	found_user = False
	for u in users:
		if u['email'] == username:
			found_user = True
	assert False == found_user

	#make sure user is returned in get users with show_all
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'users/?show_all=True'

	r = requests.get(url, headers=headers)
	users = r.json()['users']
	found_user = False
	for u in users:
		if u['email'] == username:
			found_user = True
	assert True == found_user

	#delete patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'patients/' + patient_id

	r = requests.delete(url, headers=headers)
	assert status.HTTP_204_NO_CONTENT == r.status_code

	#try to get deleted patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'patients/' + patient_id

	r = requests.get(url, headers=headers)
	assert status.HTTP_404_NOT_FOUND == r.status_code

	#get reposition report for unit
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'repositionreports?start=2016-02-13 0:0&end=2016-02-13 0:0&unit_floor=3B'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get reposition report for patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'repositionreports/61759723-a23b-4fda-9681-1225acb1cd41/?start=2016-02-13 0:0&end=2016-02-13 0:0'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get alarm response report for unit
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'alarmresponsereports?start=2016-02-13 0:0&end=2016-02-13 0:0&unit_floor=3B'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code

	#get alarm response report for patient
	headers = {
		'Content-Type' : 'application/json',
		'Authorization' : 'Bearer ' + admin_token
		}
	url = url_base + 'alarmresponsereports/61759723-a23b-4fda-9681-1225acb1cd41/?start=2016-02-13 0:0&end=2016-02-13 0:0'

	r = requests.get(url, headers=headers)

	assert status.HTTP_200_OK == r.status_code





