**Show BodyLocations**
----
  Returns a json list of all body locations. Requires jwt user token

* **URL**

  /users

* **Method:**

  `GET`
  
*  **URL Params**

   **Optional:**
 
  `user_id=[integer]`

* **Data Params**

  None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{'BodyLocations': [{'wound_stage': False, 'distance': 0.0226186, 'sensor_id': u'f8c5d29a-bd5a-4ed5-9046-bd251b416b32', 'is_wound': False, 'fast_blink': False, 'battery': 2865, 'JSID': u'left_heel', 'binary_state': False, 'patient_id': 2, 'alarm_clear_multiple': 2, 'has_previous_alert': False, 'pressure_state': u'NO_PRESSURE', 'stopped': False, 'under_pressure_milliseconds': 0, 'force_state': 0, 'alarm_threshold_minutes': 1, 'type': u'SWITCH_TYPE', 'id': 25, 'last_seen': '2016-02-16T21:18:14Z'}, {'wound_stage': False, 'distance': 1.01795, 'sensor_id': u'e7ba9226-5e35-4a83-9d15-ed9c7fdf702e', 'is_wound': False, 'fast_blink': False, 'battery': 2640, 'JSID': u'sacrum', 'binary_state': False, 'patient_id': 2, 'alarm_clear_multiple': 4, 'has_previous_alert': False, 'pressure_state': u'NO_PRESSURE', 'stopped': False, 'under_pressure_milliseconds': 0, 'force_state': 8208L, 'alarm_threshold_minutes': 60, 'type': u'FORCE_TYPE', 'id': 26, 'last_seen': '2016-02-16T21:18:14Z'}]}`
 
* **Error Response:**

  * **Code:** 404 NOT FOUND <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Show Devices**
----
  Returns a json list of devices. Requires jwt user token

* **URL**

  /devices

* **Method:**

  `GET`
  
*  **URL Params**

  None

* **Data Params**

  None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ "devices": [ { "alarm_duration": 2, "alarm_sound": "voice", "alarm_volume": "normal", "device_id": "db376736-6858-4b99-94b2-27e4cb5c01e0", "id": 1, "language": "es", "last_seen": "2016-02-16T21:14:16Z", "name": "db376736-6858-4b99-94b2-27e4cb5c01e0", "patient_id": 1, "secret": "fec6859e-b639-400f-a4e6-218cbc36422b" }, { "alarm_duration": 2, "alarm_sound": "voice", "alarm_volume": "normal", "device_id": "bc6e2c9d-3c2b-4025-b17c-5a293af60597", "id": 2, "language": "es", "last_seen": "2016-02-16T21:18:14Z", "name": "bc6e2c9d-3c2b-4025-b17c-5a293af60597", "patient_id": 2, "secret": "c9a99fcd-b652-4b71-87d7-b403b3b43fb1" }]}`
 
* **Error Response:**

  * **Code:** 404 NOT FOUND <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Create Device**
----
  Add a device. device_id is a unique identifier

* **URL**

  /devices

* **Method:**

  `POST`
  
*  **URL Params**

  None

* **Data Params**

  'device_id=[string]'
  'secret=[string]'

* **Success Response:**

  * **Code:** 204 NO CONTENT <br />
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Sync Device**
----
  Sync a device. device_id is a unique identifier

* **URL**

  /devices/sync

* **Method:**

  `POST`
  
*  **URL Params**

  None

* **Data Params**

  'type=[string]'
  'id=[string]'
  'stopped=[boolean]'
  'force_state=[string]'
  'fast_blink=[boolean]'
  'distance=[float]'
  'alarm_clear_multiple=[integer]'
  'alarm_threshold_minutes=[integer]'
  'battery=[integer]'
  'binary_state=[boolean]'
  'JSID=[string]'
  'under_pressure_milliseconds=[integer]'
  'is_wound=[boolean]'
  'pressure_state=[string]'
  'wound_stage=[string]'
  'has_previous_alert=[boolean]'
  Globals
  'language=[string]'
  'alarm_volume=[string]'
  'alarm_sound=[string]'
  'alarm_duration=[integer]'

* **Success Response:**

  * **Code:** 204 NO CONTENT <br />
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Show Events**
----
  Returns a json list of events. Can specify a patient_id. Requires jwt user token

* **URL**

  /events

* **Method:**

  `GET`
  
*  **URL Params**

   **Optional:**
 
  `patient_id=[integer]`

* **Data Params**

  None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{'events': [{'instance': '2016-01-26T20:40:58Z', 'message': u'Monitoring was resumed', 'device_id': 5, 'id': 29, 'patient_id': 5}, {'instance': '2016-01-26T16:23:09Z', 'message': u'Monitoring was resumed', 'device_id': 5, 'id': 30, 'patient_id': 5}, {'range_start': '2016-01-28T15:13:18Z', 'patient_id': 5, 'location': u'LEFT_HEEL', 'message': u'PRESSURE_RISING', 'id': 31, 'device_id': 5}, {'instance': '2016-01-26T20:40:47Z', 'message': u'Monitoring was paused', 'device_id': 5, 'id': 32, 'patient_id': 5}]}`
 
* **Error Response:**

  * **Code:** 404 NOT FOUND <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Create Event**
----
  Add an event. Email is a unique identifier. Requires a jwt device token

* **URL**

  /events

* **Method:**

  `POST`
  
*  **URL Params**

  None

* **Data Params**

  'message=[string]'
  'location=[string]'
  'epoch_timestamp=[timestamp]'

* **Success Response:**

  * **Code:** 204 NO CONTENT <br />
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />


**Show GlobalDeviceSettings**
----
  Returns a json list of GlobalDeviceSettings. Requires jwt user token

* **URL**

  /devices/settings

* **Method:**

  `GET`
  
*  **URL Params**

  None

* **Data Params**

  None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{'alarm_duration': 3, 'alarm_volume': u'loud', 'alarm_sound': u'voice', 'id': 1, 'language': u'en'}`
 
* **Error Response:**

  * **Code:** 401 UNAUTHORIZED <br />

**Update GlobalDeviceSettings**
----
  Add a device. device_id is a unique identifier

* **URL**

  /devices/settings

* **Method:**

  `POST`
  
*  **URL Params**

  None

* **Data Params**

  'alarm_duration=[integer]'
  'alarm_volume=[string]'
  'alarm_sound=[string]'
  'language=[string]'

* **Success Response:**

  * **Code:** 204 NO CONTENT <br />
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Create Patient**
----
  Add a patient. patient_id is a unique identifier. Requires jwt user token

* **URL**

  /patients

* **Method:**

  `POST`
  
*  **URL Params**

  None

* **Data Params**

  'patient_id=[string]' only required field
  'gender=[string]'
  'DOB=[string]'
  'unit_floor=[string]'
  'bed_type=[string]'
  'ethnicity=[string]'
  'braden_score=[string]'
  'mobility=[string]'
  'diagnosis=[string]'
  'medication=[string]'
  'weight=[float]'
  'height=[float]'
  'albumin_level=[string]'
  'A1C=[string]'
  'hemoglobin=[string]'
  'o2_saturation=[string]'
  'blood_pressure=[string]'
  'sensor_location=[string]'
  'site_assessment=[string]'
  'sensor_removal=[string]'

* **Success Response:**

  * **Code:** 200 OK <br />
  **Content:** `{'id' : 3 }`
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Link Patient with Device**
----
  Assign a device to a patient. patient_id is a unique identifier. Requires jwt user token

* **URL**

  /patients

* **Method:**

  `PUT`
  
*  **URL Params**

  None

* **Data Params**

  'patient_id=[integer]'
  'device_id=[integer]'

* **Success Response:**

  * **Code:** 204 NO CONTENT <br />
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Link Patient with Wound**
----
  Assign a device to a patient. patient_id is a unique identifier. Requires jwt user token

* **URL**

  /patients

* **Method:**

  `PUT`
  
*  **URL Params**

  None

* **Data Params**

  'patient_id=[integer]'
  'wound_id=[integer]'

* **Success Response:**

  * **Code:** 204 NO CONTENT <br />
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />


**Update Patient**
----
  Update a patient. patient_id is a unique identifier. Requires jwt user token

* **URL**

  /patients

* **Method:**

  `PUT`
  
*  **URL Params**

  None

* **Data Params**

  'patient_id=[string]' only required field
  'gender=[string]'
  'DOB=[string]'
  'unit_floor=[string]'
  'bed_type=[string]'
  'ethnicity=[string]'
  'braden_score=[string]'
  'mobility=[string]'
  'diagnosis=[string]'
  'medication=[string]'
  'weight=[float]'
  'height=[float]'
  'albumin_level=[string]'
  'A1C=[string]'
  'hemoglobin=[string]'
  'o2_saturation=[string]'
  'blood_pressure=[string]'
  'sensor_location=[string]'
  'site_assessment=[string]'
  'sensor_removal=[string]'

* **Success Response:**

  * **Code:** 204 NO CONTENT <br />
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Show Users**
----
  Returns a json list of users. Can specify a specific user_id. Requires jwt user token

* **URL**

  /users

* **Method:**

  `GET`
  
*  **URL Params**

   **Optional:**
 
  `user_id=[integer]`

* **Data Params**

  None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{'users': [{'password': 'd3af79d2-094c-480f-bfbb-0445d1519328', 'id': 6, 'name': '39257953-281b-4efa-b6b5-0bd9b35dec30', 'email': '39257953-281b-4efa-b6b5-0bd9b35dec30@jon.com'}, {'password': '31ac3f62-2adf-4a29-a9ad-f59d5bca9353', 'id': 9, 'name': '3e2938fc-4d9c-4ac4-8b31-8e5062c0713f', 'email': '3e2938fc-4d9c-4ac4-8b31-8e5062c0713f@jon.com'}]}`
 
* **Error Response:**

  * **Code:** 404 NOT FOUND <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Create User**
----
  Add a user. Email is a unique identifier

* **URL**

  /users

* **Method:**

  `POST`
  
*  **URL Params**

  None

* **Data Params**

  'name=[string]'
  'password=[string]'
  'email=[string]'
  'phone_number=[string]'

* **Success Response:**

  * **Code:** 204 NO CONTENT <br />
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />

**Log In User**
----
  Log in a user.

* **URL**

  /users/login

* **Method:**

  `POST`
  
*  **URL Params**

  None

* **Data Params**

  'email=[string]'
  'password=[string]'

* **Success Response:**

  * **Code:** 204 NO CONTENT <br />
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

  OR

  * **Code:** 401 UNAUTHORIZED <br />
