from dm_app import *
from json_serializer import JsonSerializer

@swagger.model
class DBAdminDefault(db.Model):
	__tablename__ = 'admin_default'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	unit_floor = db.Column(db.Text)
	alert_reponse_window = db.Column(db.Integer)

	def __init__(self, unit_floor, alert_reponse_window):
		self.unit_floor = unit_floor
		self.alert_reponse_window = alert_reponse_window

class AdminDefaultJsonSerializer(JsonSerializer):
	__attributes__ = ['unit_floor', 'alert_reponse_window']
	__required__ = ['unit_floor', 'alert_reponse_window']
	__attribute_serializer__ = dict()
	__object_class__ = DBAdminDefault

@swagger.model
class DBAlarmResponse(db.Model):
	__tablename__ = 'alarm_response'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	date = db.Column(db.Date, index=True)
	hour = db.Column(db.Integer, index=True)
	pa_id = db.Column(db.String(100), index=True)
	alarms_occurred = db.Column(db.Integer)
	patient_repositions = db.Column(db.Integer)
	caregiver_repositions = db.Column(db.Integer)
	total_repositions = db.Column(db.Integer)
	minutes_alarming = db.Column(db.String(60))
	unit_floor = db.Column(db.String(100), index=True)

	def __init__(self, date, hour, pa_id, alarms_occurred, patient_repositions, caregiver_repositions, total_repositions, minutes_alarming, unit_floor):
		self.date = date
		self.hour = hour
		self.pa_id = pa_id
		self.alarms_occurred = alarms_occurred
		self.patient_repositions = patient_repositions
		self.caregiver_repositions = caregiver_repositions
		self.total_repositions = total_repositions
		self.minutes_alarming = minutes_alarming
		self.unit_floor = unit_floor


class DBAlarmResponseJsonSerializer(JsonSerializer):
	__attributes__ = ['date', 'hour', 'pa_id', 'alarms_occurred', 'patient_repositions', 'caregiver_repositions', 'total_repositions',
	'minutes_alarming', 'unit_floor']
	__required__ = ['date', 'hour', 'pa_id', 'alarms_occurred', 'patient_repositions', 'caregiver_repositions', 'total_repositions',
	'minutes_alarming', 'unit_floor']
	__attribute_serializer__ = dict()
	__object_class__ = DBAlarmResponse

@swagger.model
class DBAlarmResponseReportData(db.Model):
	__tablename__ = 'alarm_response_report_data'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	date = db.Column(db.Date, index=True)
	pa_id = db.Column(db.String(100), index=True)
	unit_floor = db.Column(db.String(100), index=True)
	all = db.Column(db.Boolean)
	data = db.Column(db.Text)

	def __init__(self, date, data, pa_id=None, unit_floor=None, all=None):
		self.date = date
		self.data = data
		self.pa_id = pa_id
		self.unit_floor = unit_floor
		self.all = all


class DBAlarmResponseReportDataJsonSerializer(JsonSerializer):
	__attributes__ = ['date', 'pa_id', 'unit_floor', 'data']
	__required__ = ['date', 'pa_id', 'unit_floor', 'data']
	__attribute_serializer__ = dict()
	__object_class__ = DBAlarmResponseReportData

@swagger.model
class DBBodyLocation(db.Model):
	__tablename__ = 'body_location'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
	type = db.Column(db.String(100))
	sensor_serial = db.Column(db.String(100), index=True)
	stopped = db.Column(db.Boolean)
	fast_blink = db.Column(db.Boolean)
	force_state = db.Column(db.Integer)
	JSID = db.Column(db.String(100), index=True)
	alarm_clear_multiple = db.Column(db.Integer)
	alarm_threshold_minutes = db.Column(db.Integer)
	battery = db.Column(db.Integer)
	binary_state = db.Column(db.Boolean)
	last_seen = db.Column(db.DateTime)
	distance = db.Column(db.Float)
	under_pressure_milliseconds = db.Column(db.Integer)
	pressure_state = db.Column(db.String(100))
	wound_stage = db.Column(db.String(50))
	is_wound = db.Column(db.Boolean)
	has_previous_alert = db.Column(db.Boolean)
	site_assessment = db.Column(db.Text)
	sensor_removal = db.Column(db.Text)
	wound_measurement = db.Column(db.String(100))
	wound_existing_since = db.Column(db.DateTime)
	medical_record_number = db.Column(db.String(100), index=True)
	existing_wound = db.Column(db.Boolean)
	wound_alarm_threshold_minutes = db.Column(db.Integer)
	wound_alarm_clear_multiple = db.Column(db.Integer)
	previous_alarm_threshold_hours = db.Column(db.Integer)
	deleted = db.Column(db.Boolean)
	wound_outcome = db.Column(db.Text)
	wound_acquisition = db.Column(db.Text)

	def __init__(self, patient_id, JSID, sensor_serial=None, stopped=None, force_state=None, fast_blink=None, distance=None,
		type=None, alarm_clear_multiple=None, alarm_threshold_minutes=None, battery=None, binary_state=None, last_seen=None,
		under_pressure_milliseconds=None, pressure_state=None, wound_stage=None, is_wound=None, has_previous_alert=None,
		site_assessment=None, sensor_removal=None, wound_measurement=None, wound_existing_since=None, medical_record_number=None,
		existing_wound=None, wound_alarm_threshold_minutes=None, wound_alarm_clear_multiple=None, 
		previous_alarm_threshold_hours=None, wound_outcome=None, wound_acquisition=None, deleted=None):
		self.type = type
		self.sensor_serial = sensor_serial
		self.patient_id = patient_id
		self.stopped = stopped
		self.fast_blink = fast_blink
		self.force_state = force_state
		self.distance = distance
		self.JSID = JSID
		self.alarm_clear_multiple = alarm_clear_multiple
		self.alarm_threshold_minutes = alarm_threshold_minutes
		self.battery = battery
		self.binary_state = binary_state
		self.last_seen = last_seen
		self.under_pressure_milliseconds = under_pressure_milliseconds
		self.pressure_state = pressure_state
		self.wound_stage = wound_stage
		self.is_wound = is_wound
		self.has_previous_alert = has_previous_alert
		self.site_assessment = site_assessment
		self.sensor_removal = sensor_removal
		self.wound_measurement = wound_measurement
		self.wound_existing_since = wound_existing_since
		self.medical_record_number = medical_record_number
		self.existing_wound = existing_wound
		self.wound_alarm_threshold_minutes = wound_alarm_threshold_minutes
		self.wound_alarm_clear_multiple = wound_alarm_clear_multiple
		self.previous_alarm_threshold_hours = previous_alarm_threshold_hours
		self.wound_outcome = wound_outcome
		self.deleted = deleted
		self.wound_acquisition = wound_acquisition


class BodyLocationJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'medical_record_number', 'JSID', 'sensor_serial', 'stopped', 'force_state', 'fast_blink', 'distance',
		'type', 'alarm_clear_multiple', 'alarm_threshold_minutes', 'battery', 'binary_state', 'last_seen',
		'under_pressure_milliseconds', 'pressure_state', 'wound_stage', 'is_wound', 'has_previous_alert',
		'site_assessment', 'sensor_removal', 'wound_measurement', 'wound_existing_since', 'existing_wound',
		'wound_alarm_threshold_minutes', 'wound_alarm_clear_multiple', 'previous_alarm_threshold_hours', 'wound_outcome',
		'wound_acquisition', 'deleted']
	__required__ = ['id', 'patient_id', 'medical_record_number', 'JSID', 'sensor_serial', 'stopped', 'force_state', 'fast_blink', 'distance', \
		'type', 'alarm_clear_multiple', 'alarm_threshold_minutes', 'battery', 'binary_state', 'last_seen',
		'under_pressure_milliseconds', 'pressure_state', 'wound_stage', 'is_wound', 'has_previous_alert',
		'site_assessment', 'sensor_removal', 'wound_measurement', 'wound_existing_since', 'existing_wound',
		'wound_alarm_threshold_minutes', 'wound_alarm_clear_multiple', 'previous_alarm_threshold_hours', 'wound_outcome',
		'wound_acquisition', 'deleted']
	__attribute_serializer__ = dict(last_seen='datetime', wound_existing_since='datetime')#, events='event')
	__object_class__ = DBBodyLocation

class PUStatusReportJsonSerializer(JsonSerializer):
	__attributes__ = ['medical_record_number', 'is_wound', 'existing_wound', 'wound_stage', 'wound_measurement', 'wound_existing_since', 
	'JSID', 'wound_outcome']
	__required__ = ['medical_record_number', 'is_wound', 'existing_wound', 'wound_stage', 'wound_measurement', 'wound_existing_since', 
	'JSID', 'wound_outcome']
	__attribute_serializer__ = dict(wound_existing_since='datetime')
	__object_class__ = DBBodyLocation

@swagger.model
class DBBodyLocationHistory(db.Model):
	__tablename__ = 'body_location_history'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	type = db.Column(db.String(100))
	sensor_serial = db.Column(db.String(100))
	stopped = db.Column(db.Boolean)
	fast_blink = db.Column(db.Boolean)
	force_state = db.Column(db.Integer)
	JSID = db.Column(db.String(100), index=True)
	alarm_clear_multiple = db.Column(db.Integer)
	alarm_threshold_minutes = db.Column(db.Integer)
	battery = db.Column(db.Integer)
	binary_state = db.Column(db.Boolean)
	last_seen = db.Column(db.DateTime)
	distance = db.Column(db.Float)
	under_pressure_milliseconds = db.Column(db.Integer)
	pressure_state = db.Column(db.String(100))
	wound_stage = db.Column(db.String(50))
	is_wound = db.Column(db.Boolean)
	has_previous_alert = db.Column(db.Boolean)
	site_assessment = db.Column(db.Text)
	sensor_removal = db.Column(db.Text)
	wound_measurement = db.Column(db.String(100))
	wound_existing_since = db.Column(db.DateTime)
	medical_record_number = db.Column(db.String(100), index=True)
	existing_wound = db.Column(db.Boolean)
	wound_alarm_threshold_minutes = db.Column(db.Integer)
	wound_alarm_clear_multiple = db.Column(db.Integer)
	previous_alarm_threshold_hours = db.Column(db.Integer)
	deleted = db.Column(db.Boolean)
	wound_outcome = db.Column(db.Text)
	body_location_id = db.Column(db.Integer, index=True)
	user = db.Column(db.Text)
	date_of_record = db.Column(db.DateTime, index=True)
	wound_acquisition = db.Column(db.Text)

	def __init__(self, JSID, body_location_id, user, date_of_record, sensor_serial=None, stopped=None, force_state=None, fast_blink=None, distance=None,
		type=None, alarm_clear_multiple=None, alarm_threshold_minutes=None, battery=None, binary_state=None, last_seen=None,
		under_pressure_milliseconds=None, pressure_state=None, wound_stage=None, is_wound=None, has_previous_alert=None,
		site_assessment=None, sensor_removal=None, wound_measurement=None, wound_existing_since=None, medical_record_number=None,
		existing_wound=None, wound_alarm_threshold_minutes=None, wound_alarm_clear_multiple=None, 
		previous_alarm_threshold_hours=None, wound_outcome=None, wound_acquisition=None):
		self.type = type
		self.sensor_serial = sensor_serial
		self.stopped = stopped
		self.fast_blink = fast_blink
		self.force_state = force_state
		self.distance = distance
		self.JSID = JSID
		self.alarm_clear_multiple = alarm_clear_multiple
		self.alarm_threshold_minutes = alarm_threshold_minutes
		self.battery = battery
		self.binary_state = binary_state
		self.last_seen = last_seen
		self.under_pressure_milliseconds = under_pressure_milliseconds
		self.pressure_state = pressure_state
		self.wound_stage = wound_stage
		self.is_wound = is_wound
		self.has_previous_alert = has_previous_alert
		self.site_assessment = site_assessment
		self.sensor_removal = sensor_removal
		self.wound_measurement = wound_measurement
		self.wound_existing_since = wound_existing_since
		self.medical_record_number = medical_record_number
		self.existing_wound = existing_wound
		self.wound_alarm_threshold_minutes = wound_alarm_threshold_minutes
		self.wound_alarm_clear_multiple = wound_alarm_clear_multiple
		self.previous_alarm_threshold_hours = previous_alarm_threshold_hours
		self.wound_outcome = wound_outcome
		self.body_location_id = body_location_id
		self.user = user
		self.date_of_record = date_of_record
		self.wound_acquisition = wound_acquisition


class BodyLocationHistoryJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'medical_record_number', 'JSID', 'sensor_serial', 'stopped', 'force_state', 'fast_blink', 'distance', 'user', 'date_of_record',
		'type', 'alarm_clear_multiple', 'alarm_threshold_minutes', 'battery', 'binary_state', 'last_seen',
		'under_pressure_milliseconds', 'pressure_state', 'wound_stage', 'is_wound', 'has_previous_alert',
		'site_assessment', 'sensor_removal', 'wound_measurement', 'wound_existing_since', 'existing_wound',
		'wound_alarm_threshold_minutes', 'wound_alarm_clear_multiple', 'previous_alarm_threshold_hours', 'wound_outcome', 'wound_acquisition']
	__required__ = ['id', 'medical_record_number', 'JSID', 'sensor_serial', 'stopped', 'force_state', 'fast_blink', 'distance', 'user', 'date_of_record',
		'type', 'alarm_clear_multiple', 'alarm_threshold_minutes', 'battery', 'binary_state', 'last_seen',
		'under_pressure_milliseconds', 'pressure_state', 'wound_stage', 'is_wound', 'has_previous_alert',
		'site_assessment', 'sensor_removal', 'wound_measurement', 'wound_existing_since', 'existing_wound',
		'wound_alarm_threshold_minutes', 'wound_alarm_clear_multiple', 'previous_alarm_threshold_hours', 'wound_outcome', 'wound_acquisition']
	__attribute_serializer__ = dict(last_seen='datetime', wound_existing_since='datetime', date_of_record='datetime')
	__object_class__ = DBBodyLocationHistory

@swagger.model
class DBDevice(db.Model):
	__tablename__ = 'device'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), unique=True) 
	serial = db.Column(db.String(100), index=True, unique=True)
#	secret = db.Column(db.String(100), unique=True)
	name = db.Column(db.String(100))
	last_seen = db.Column(db.DateTime, index=True)
	alarm_duration = db.Column(db.Integer)
	alarm_sound = db.Column(db.String(100))
	alarm_volume = db.Column(db.String(100))
	language = db.Column(db.String(50))
	medical_record_number = db.Column(db.String(100), index=True, unique=True)
	last_device_sync = db.Column(db.DateTime)
	last_web_change = db.Column(db.DateTime)
	deleted = db.Column(db.Boolean)
	#timezone = db.Column(db.String(100))

	def __init__(self, serial, name, last_seen, patient_id=None, alarm_duration=None, alarm_sound=None, alarm_volume=None, \
		language=None, medical_record_number=None, last_device_sync=None, last_web_change=None, deleted=None):#, timezone=None):
		self.patient_id = patient_id
		self.serial = serial
#		self.secret = secret
		self.name = name
		self.last_seen = last_seen
		self.alarm_duration = alarm_duration
		self.alarm_sound = alarm_sound
		self.alarm_volume = alarm_volume
		self.language = language
		self.medical_record_number = medical_record_number
		self.last_device_sync = last_device_sync
		self.last_web_change = last_web_change
		self.deleted = deleted
		#self.timezone = timezone

class DeviceJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'medical_record_number', 'serial', 'name', 'last_seen', 'alarm_duration', 'alarm_sound', \
						'alarm_volume', 'language', 'deleted']#, 'timezone']
	__required__ = ['id', 'patient_id', 'medical_record_number', 'serial', 'name', 'last_seen', 'alarm_duration', 'alarm_sound', \
						'alarm_volume', 'language', 'deleted']#, 'timezone']
	__attribute_serializer__ = dict(last_seen='datetime')
	__object_class__ = DBDevice

@swagger.model
class DBDiagnosis(db.Model):
	__tablename__ = 'diagnosis'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), unique=True)
	past_diagnosis_patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), unique=True)
	diabetes = db.Column(db.Boolean)
	heart_disease = db.Column(db.Boolean)
	stroke = db.Column(db.Boolean)
	immobility = db.Column(db.Boolean)
	pvd = db.Column(db.Boolean)
	neuropathy = db.Column(db.Boolean)
	incontinence = db.Column(db.Boolean)
	malnutrition = db.Column(db.Boolean)
	heart_attack = db.Column(db.Boolean)
	prior_skin_pressure_injury = db.Column(db.Boolean)
	hip_pelvic_fracture = db.Column(db.Boolean)
	femur_fracture = db.Column(db.Boolean)
	other = db.Column(db.Boolean)
	hypertension = db.Column(db.Boolean)
	malignancy = db.Column(db.Boolean)
	skin_flap_graft = db.Column(db.Boolean)
	respiratory_failure = db.Column(db.Boolean)

	def __init__(self, diabetes, heart_disease, stroke, immobility, pvd, neuropathy, incontinence, malnutrition, heart_attack,
		prior_skin_pressure_injury, hip_pelvic_fracture, femur_fracture, other, hypertension, malignancy, skin_flap_graft,
		respiratory_failure, patient_id=None, past_diagnosis_patient_id=None):
		self.patient_id = patient_id
		self.diabetes = diabetes
		self.heart_disease = heart_disease
		self.stroke = stroke
		self.immobility = immobility
		self.pvd = pvd
		self.neuropathy = neuropathy
		self.incontinence = incontinence
		self.malnutrition = malnutrition
		self.heart_attack = heart_attack
		self.prior_skin_pressure_injury = prior_skin_pressure_injury
		self.hip_pelvic_fracture = hip_pelvic_fracture
		self.femur_fracture = femur_fracture
		self.other = other
		self.past_diagnosis_patient_id = past_diagnosis_patient_id
		self.hypertension = hypertension
		self.malignancy = malignancy
		self.skin_flap_graft = skin_flap_graft
		self.respiratory_failure = respiratory_failure

class DiagnosisJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'patient_id', 'diabetes', 'heart_disease', 'stroke', 'immobility', 'pvd', 'neuropathy', 'incontinence', 'malnutrition',
					'heart_attack', 'prior_skin_pressure_injury', 'hip_pelvic_fracture', 'femur_fracture', 'hypertension', 'malignancy',
					'skin_flap_graft', 'respiratory_failure', 'other']
	__required__ = ['id', 'patient_id', 'diabetes', 'heart_disease', 'stroke', 'immobility', 'pvd', 'neuropathy', 'incontinence', 'malnutrition',
					'heart_attack', 'prior_skin_pressure_injury', 'hip_pelvic_fracture', 'femur_fracture', 'hypertension', 'malignancy',
					'skin_flap_graft', 'respiratory_failure', 'other']
	__attribute_serializer__ = dict()
	__object_class__ = DBDiagnosis

@swagger.model
class DBEvent(db.Model):
	__tablename__ = 'event'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
	device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
	body_location_id = db.Column(db.Integer, db.ForeignKey('body_location.id'))
	message = db.Column(db.String(100), index=True)
	instance = db.Column(db.DateTime, index=True)
	range_start = db.Column(db.DateTime)
	range_end = db.Column(db.DateTime, index=True)
	location = db.Column(db.String(100), index=True)
	medical_record_number = db.Column(db.String(100), index=True)
	deleted = db.Column(db.Boolean)
	unit_floor = db.Column(db.String(100), index=True)
	latest = db.Column(db.String(100), index=True, unique=True)

	def __init__(self, patient_id, message, body_location_id=None, medical_record_number=None, device_id=None, instance=None, 
		range_start=None, range_end=None, location=None, unit_floor=None, latest=None):
		self.patient_id = patient_id
		self.message = message
		self.body_location_id = body_location_id
		self.device_id = device_id
		self.instance = instance
		self.range_start = range_start
		self.range_end = range_end
		self.location = location
		self.medical_record_number = medical_record_number
		self.unit_floor = unit_floor
		self.latest = latest

class EventJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'medical_record_number', 'device_id', 'message', 'instance', 'range_start', 'range_end', 'location', 'unit_floor', 'latest',]
	__required__ = ['id', 'medical_record_number', 'device_id', 'message', 'instance', 'range_start', 'range_end', 'location', 'unit_floor', 'latest']
	__attribute_serializer__ = dict(range_start='datetime', range_end='datetime', instance='datetime')
	__object_class__ = DBEvent

class StatusEventJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'medical_record_number', 'device_id', 'message', 'instance', 'range_start', 'range_end', 'location', 'unit_floor', 'latest', 'battery',]
	__required__ = ['id', 'medical_record_number', 'device_id', 'message', 'instance', 'range_start', 'range_end', 'location', 'unit_floor', 'latest', 'battery']
	__attribute_serializer__ = dict(range_start='datetime', range_end='datetime', instance='datetime')
	__object_class__ = DBEvent

@swagger.model
class DBEventHistory(db.Model):
	__tablename__ = 'event_history'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	sensor_serial = db.Column(db.String(100))
	location = db.Column(db.String(100))
	battery = db.Column(db.Integer)
	distance = db.Column(db.Float)
	alarm_threshold_minutes = db.Column(db.Integer)
	alarm_clear_multiple = db.Column(db.Integer)
	site_assessment = db.Column(db.String(100))
	sensor_removal = db.Column(db.String(50))
	event_type = db.Column(db.String(50))
	occurred = db.Column(db.DateTime)
	medical_record_number = db.Column(db.String(100), index=True)
	wound_alarm_threshold_minutes = db.Column(db.Integer)
	wound_alarm_clear_multiple = db.Column(db.Integer)
	previous_alarm_threshold_hours = db.Column(db.Integer)
	deleted = db.Column(db.Boolean)
	unit_floor = db.Column(db.String(100), index=True)

	def __init__(self, event_type, occurred, sensor_serial=None, medical_record_number=None, location=None, battery=None,
	distance=None, alarm_threshold_minutes=None, alarm_clear_multiple=None, site_assessment=None, sensor_removal=None,
	wound_alarm_threshold_minutes=None, wound_alarm_clear_multiple=None, previous_alarm_threshold_hours=None, unit_floor=None):
		self.event_type = event_type
		self.occurred = occurred
		self.sensor_serial = sensor_serial
		self.location = location
		self.battery = battery
		self.distance = distance
		self.alarm_threshold_minutes = alarm_threshold_minutes
		self.alarm_clear_multiple = alarm_clear_multiple
		self.site_assessment = site_assessment
		self.sensor_removal = sensor_removal
		self.medical_record_number = medical_record_number
		self.wound_alarm_threshold_minutes = wound_alarm_threshold_minutes
		self.wound_alarm_clear_multiple = wound_alarm_clear_multiple
		self.previous_alarm_threshold_hours = previous_alarm_threshold_hours
		self.unit_floor = unit_floor

class EventHistoryReportJsonSerializer(JsonSerializer):
	__attributes__ = ['event_type', 'occurred', 'sensor_serial', 'location', 'battery', 'distance', 'alarm_threshold_minutes', 'alarm_clear_multiple',
		'wound_alarm_threshold_minutes', 'wound_alarm_clear_multiple', 'previous_alarm_threshold_hours', 'name', 'last_name', 'unit_floor']
	__required__ = ['medical_record_number', 'event_type', 'occurred', 'sensor_serial', 'location', 'battery', 'distance',
	'alarm_threshold_minutes', 'alarm_clear_multiple', 'site_assessment', 'sensor_removal',
		'wound_alarm_threshold_minutes', 'wound_alarm_clear_multiple', 'previous_alarm_threshold_hours', 'name', 'last_name', 'unit_floor']
	__attribute_serializer__ = dict(occurred='datetime')
	__object_class__ = DBEventHistory

@swagger.model
class DBGlobalDeviceSettings(db.Model):
	__tablename__ = 'global_device_settings'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	alarm_duration = db.Column(db.Integer)
	alarm_sound = db.Column(db.String(100))
	alarm_volume = db.Column(db.String(100))
	language = db.Column(db.String(50))

	def __init__(self, alarm_duration, alarm_sound, alarm_volume, language):
		self.alarm_duration = alarm_duration
		self.alarm_sound = alarm_sound
		self.alarm_volume = alarm_volume
		self.language = language

	def as_dict(self):
		   return {c.name: getattr(self, c.name) for c in self.__table__.columns}

@swagger.model
class DBGlobalLocationSettings(db.Model):
	__tablename__ = 'global_location_settings'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	type = db.Column(db.String(100))
	JSID = db.Column(db.String(100), index=True)
	alarm_clear_multiple = db.Column(db.Integer)
	alarm_threshold_minutes = db.Column(db.Integer)
	pressure_state = db.Column(db.String(100))
	wound_stage = db.Column(db.String(50))
	is_wound = db.Column(db.Boolean)
	has_previous_alert = db.Column(db.Boolean)
	site_assessment = db.Column(db.String(100))
	sensor_removal = db.Column(db.String(50))
	wound_measurement = db.Column(db.String(100))
	existing_wound = db.Column(db.Boolean)
	wound_alarm_threshold_minutes = db.Column(db.Integer)
	wound_alarm_clear_multiple = db.Column(db.Integer)
	previous_alarm_threshold_hours = db.Column(db.Integer)

	def __init__(self, type, JSID, alarm_clear_multiple, alarm_threshold_minutes, pressure_state, wound_stage, is_wound, has_previous_alert,
			site_assessment, sensor_removal, wound_measurement, existing_wound, wound_alarm_threshold_minutes, wound_alarm_clear_multiple,
			previous_alarm_threshold_hours):
		self.type = type
		self.JSID = JSID
		self.alarm_clear_multiple = alarm_clear_multiple
		self.alarm_threshold_minutes = alarm_threshold_minutes
		self.pressure_state = pressure_state
		self.wound_stage = wound_stage
		self.is_wound = is_wound
		self.has_previous_alert = has_previous_alert
		self.site_assessment = site_assessment
		self.sensor_removal = sensor_removal
		self.wound_measurement = wound_measurement
		self.existing_wound = existing_wound
		self.wound_alarm_threshold_minutes = wound_alarm_threshold_minutes
		self.wound_alarm_clear_multiple = wound_alarm_clear_multiple
		self.previous_alarm_threshold_hours = previous_alarm_threshold_hours

	def as_dict(self):
		   return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@swagger.model
class DBLargeRequest(db.Model):
	__tablename__ = 'large_request'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	device_id = db.Column(db.Integer)
	patient_id = db.Column(db.Integer)
	request = db.Column(db.Text)
	request_class = db.Column(db.String(100))
	request_action = db.Column(db.String(100))
	occurred = db.Column(db.DateTime)
	processing = db.Column(db.Boolean)
	error = db.Column(db.Text)

	def __init__(self, device_id, patient_id, request, request_class, request_action, occurred, processing=False, error=None):
		self.device_id = device_id
		self.patient_id = patient_id
		self.request = request
		self.request_class = request_class
		self.request_action = request_action
		self.occurred = occurred
		self.processing = processing
		self.error = error



@swagger.model
class DBMedication(db.Model):
	__tablename__ = 'medication'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), unique=True)
	none = db.Column(db.Boolean)
	steroids = db.Column(db.Boolean)
	vasopressors = db.Column(db.Boolean)
	heart_rhythm = db.Column(db.Boolean)
	blood_pressure = db.Column(db.Boolean)
	narcotic_pain = db.Column(db.Boolean)
	non_narcotic_pain = db.Column(db.Boolean)
	hypoglycemic = db.Column(db.Boolean)
	sleeping = db.Column(db.Boolean)
	constipation_relief = db.Column(db.Boolean)
	anxiety_control = db.Column(db.Boolean)
	antispasmodics = db.Column(db.Boolean)
	antibiotics = db.Column(db.Boolean)
	other = db.Column(db.Boolean)
	chemotherapy = db.Column(db.Boolean)
	radiation = db.Column(db.Boolean)

	def __init__(self, none, steroids, vasopressors, heart_rhythm, blood_pressure, narcotic_pain, non_narcotic_pain, hypoglycemic, 
		sleeping, constipation_relief, anxiety_control, antispasmodics, antibiotics, other, chemotherapy, radiation, patient_id=None):
		self.patient_id = patient_id
		self.none = none
		self.steroids = steroids
		self.vasopressors = vasopressors
		self.heart_rhythm = heart_rhythm
		self.blood_pressure = blood_pressure
		self.narcotic_pain = narcotic_pain
		self.non_narcotic_pain = non_narcotic_pain
		self.hypoglycemic = hypoglycemic
		self.sleeping = sleeping
		self.constipation_relief = constipation_relief
		self.anxiety_control = anxiety_control
		self.antispasmodics = antispasmodics
		self.antibiotics = antibiotics
		self.other = other
		self.chemotherapy = chemotherapy
		self.radiation = radiation

class MedicationJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'patient_id', 'none', 'steroids', 'vasopressors', 'heart_rhythm', 'blood_pressure', 'narcotic_pain',
					'non_narcotic_pain', 'hypoglycemic', 'sleeping', 'constipation_relief', 'anxiety_control', 'antispasmodics',
					'antibiotics', 'chemotherapy', 'radiation', 'other']
	__required__ = ['id', 'patient_id', 'none', 'steroids', 'vasopressors', 'heart_rhythm', 'blood_pressure', 'narcotic_pain',
					'non_narcotic_pain', 'hypoglycemic', 'sleeping', 'constipation_relief', 'anxiety_control', 'antispasmodics',
					'antibiotics', 'chemotherapy', 'radiation', 'other']
	__attribute_serializer__ = dict()
	__object_class__ = DBMedication


@swagger.model
class DBPatient(db.Model):
	__tablename__ = 'patient'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	pa_id = db.Column(db.String(100), unique=True, index=True)
	diagnosis = db.relationship('DBDiagnosis', backref='patient', foreign_keys='DBDiagnosis.patient_id', uselist=False)
	past_diagnosis = db.relationship('DBDiagnosis', backref='past_patient', foreign_keys='DBDiagnosis.past_diagnosis_patient_id', uselist=False)
	medication = db.relationship('DBMedication', backref='patient', uselist=False)
	device = db.relationship('DBDevice', backref='patient', lazy='joined')
	body_locations = db.relationship('DBBodyLocation', backref='patient', lazy='joined')
	activations = db.relationship('DBPatientActivation', backref='patient', lazy='joined')
	gender = db.Column(db.String(10))
	DOB = db.Column(db.String(25))
	unit_floor = db.Column(db.String(50))
	bed_type = db.Column(db.String(50))
	ethnicity = db.Column(db.String(50))
	braden_score = db.Column(db.String(50))
	mobility = db.Column(db.String(50))
	incontinence = db.Column(db.String(50))
	weight = db.Column(db.Float)
	height = db.Column(db.Float)
	albumin_level = db.Column(db.String(50))
	A1C = db.Column(db.String(50))
	hemoglobin = db.Column(db.String(50))
	o2_saturation = db.Column(db.String(50))
	blood_pressure = db.Column(db.String(50))
	bmi = db.Column(db.Float)
	deleted = db.Column(db.Boolean)
	name = db.Column(db.String(100), index=True)
	last_name = db.Column(db.String(100), index=True)
	medical_record_number = db.Column(db.String(50), unique=True, index=True)
	date_of_admission = db.Column(db.Date)
	units = db.Column(db.String(50))
	room = db.Column(db.Text)

	def __init__(self, name, last_name, gender=None, DOB=None, unit_floor=None, bed_type=None, ethnicity=None, braden_score=None, mobility=None, \
		incontinence=None, weight=None, height=None, albumin_level=None, A1C=None, hemoglobin=None, o2_saturation=None, \
		blood_pressure=None, bmi=None, deleted=None, pa_id=None, medical_record_number=None, date_of_admission=None, units=None, room=None):
		self.pa_id = pa_id
		self.gender = gender
		self.DOB = DOB
		self.unit_floor = unit_floor
		self.bed_type = bed_type
		self.ethnicity = ethnicity
		self.braden_score = braden_score
		self.mobility = mobility
		self.incontinence = incontinence
		self.weight = weight
		self.height = height
		self.albumin_level = albumin_level
		self.A1C = A1C
		self.hemoglobin = hemoglobin
		self.o2_saturation = o2_saturation
		self.blood_pressure = blood_pressure
		self.bmi = bmi
		self.deleted = deleted
		self.name = name
		self.last_name = last_name
		self.medical_record_number = medical_record_number
		self.date_of_admission = date_of_admission
		self.units = units
		self.room = room

class PatientJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'medical_record_number', 'device', 'body_locations', 'gender', 'DOB', 'unit_floor', \
						'bed_type', 'ethnicity', 'braden_score', 'mobility', 'incontinence', 'weight', 'height', \
						'albumin_level', 'A1C', 'hemoglobin', 'o2_saturation', 'blood_pressure', 'bmi', 'deleted', 'name', 'last_name', 'pa_id',
						'diagnosis', 'medication', 'date_of_admission', 'units', 'activations', 'past_diagnosis', 'room']
	__required__ = ['id', 'medical_record_number', 'device', 'body_locations', 'gender', 'DOB', 'unit_floor', \
						'bed_type', 'ethnicity', 'braden_score', 'mobility', 'incontinence', 'weight', 'height', \
						'albumin_level', 'A1C', 'hemoglobin', 'o2_saturation', 'blood_pressure', 'bmi', 'deleted', 'name', 'last_name', 'pa_id',
						'diagnosis', 'medication', 'date_of_admission', 'units', 'activations', 'past_diagnosis', 'room']
	__attribute_serializer__ = dict(body_locations='body_locations', device='device', date_of_admission='date', diagnosis='diagnosis', 
		medication='medication', DOB='date', activations='activations', past_diagnosis='diagnosis')
	__object_class__ = DBPatient

	def __init__(self, timezone=None):
		super(PatientJsonSerializer, self).__init__(timezone)
		self.serializers['body_locations'] = dict(
			serialize=lambda x:
				[BodyLocationJsonSerializer(timezone).serialize(xx) for xx in x],
			deserialize=lambda x:
				[BodyLocationJsonSerializer(timezone).deserialize(xx) for xx in x]
		)
		self.serializers['device'] = dict(
			serialize=lambda x:
				[DeviceJsonSerializer(timezone).serialize(xx) for xx in x],
			deserialize=lambda x:
				[DeviceJsonSerializer(timezone).deserialize(xx) for xx in x]
		)
		self.serializers['diagnosis'] = dict(
			serialize=lambda x:
				[DiagnosisJsonSerializer(timezone).serialize(xx) for xx in x],
			deserialize=lambda x:
				[DiagnosisJsonSerializer(timezone).deserialize(xx) for xx in x]
		)
		self.serializers['medication'] = dict(
			serialize=lambda x:
				[MedicationJsonSerializer(timezone).serialize(xx) for xx in x],
			deserialize=lambda x:
				[MedicationJsonSerializer(timezone).deserialize(xx) for xx in x]
		)
		self.serializers['activations'] = dict(
			serialize=lambda x:
				[PatientActivationJsonSerializer(timezone).serialize(xx) for xx in x],
			deserialize=lambda x:
				[PatientActivationJsonSerializer(timezone).deserialize(xx) for xx in x]
		)

@swagger.model
class DBPatientActivation(db.Model):
	__tablename__ = 'patient_activation'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
	status = db.Column(db.String(50))
	occurred = db.Column(db.DateTime)
	reason = db.Column(db.Text)
	sensors_collected = db.Column(db.Boolean)
	sensors_not_collected_reason = db.Column(db.Text)
	date_of_record = db.Column(db.DateTime)
	reason_other = db.Column(db.Text)


	def __init__(self, patient_id, status, occurred, reason, date_of_record, sensors_collected=None, sensors_not_collected_reason=None, reason_other=None):
		self.patient_id = patient_id
		self.status = status
		self.occurred = occurred
		self.reason = reason
		self.date_of_record = date_of_record
		self.sensors_collected = sensors_collected
		self.sensors_not_collected_reason = sensors_not_collected_reason
		self.reason_other = reason_other

class PatientActivationJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'patient_id', 'status', 'occurred', 'reason', 'sensors_collected', 'sensors_not_collected_reason', 'reason_other']
	__required__ = ['id', 'patient_id', 'status', 'occurred', 'reason', 'sensors_collected', 'sensors_not_collected_reason', 'reason_other']
	__attribute_serializer__ = dict(occurred='datetime')
	__object_class__ = DBPatientActivation

@swagger.model
class DBPatientsActive(db.Model):
	__tablename__ = 'patients_active'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	date = db.Column(db.Date, index=True)
	hour = db.Column(db.Integer, index=True)
	unit_floor = db.Column(db.String(100), index=True)
	number_active = db.Column(db.Integer)

	def __init__(self, date, hour, unit_floor, number_active):
		self.date = date
		self.hour = hour
		self.unit_floor = unit_floor
		self.number_active = number_active

class PatientsActiveJsonSerializer(JsonSerializer):
	__attributes__ = ['date', 'hour', 'unit_floor', 'number_active']
	__required__ = ['date', 'hour', 'unit_floor', 'number_active']
	__attribute_serializer__ = dict()
	__object_class__ = DBPatientsActive

@swagger.model
class DBPatientHistory(db.Model):
	__tablename__ = 'patient_history'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	medical_record_number = db.Column(db.String(100), index=True)
	pa_id = db.Column(db.String(100), index=True)
	gender = db.Column(db.String(10))
	DOB = db.Column(db.Date)
	unit_floor = db.Column(db.String(50))
	bed_type = db.Column(db.String(50))
	ethnicity = db.Column(db.String(50))
	braden_score = db.Column(db.String(50))
	mobility = db.Column(db.String(50))
	diagnosis = db.Column(db.Text)
	incontinence = db.Column(db.String(50))
	medication = db.Column(db.Text)
	weight = db.Column(db.Float)
	height = db.Column(db.Float)
	albumin_level = db.Column(db.String(50))
	A1C = db.Column(db.String(50))
	hemoglobin = db.Column(db.String(50))
	o2_saturation = db.Column(db.String(50))
	blood_pressure = db.Column(db.String(50))
	bmi = db.Column(db.Float)
	user = db.Column(db.String(100), index=True)
	date_of_record = db.Column(db.DateTime, index=True)
	deleted = db.Column(db.Boolean)
	name = db.Column(db.String(100))
	last_name = db.Column(db.String(100))
	date_of_admission = db.Column(db.Date)
	units = db.Column(db.String(50))
	past_diagnosis = db.Column(db.Text)
	room = db.Column(db.Text)

	def __init__(self, pa_id, medical_record_number, user, date_of_record, gender=None, DOB=None, unit_floor=None, bed_type=None,
		ethnicity=None, braden_score=None, mobility=None, diagnosis=None, incontinence=None, medication=None, weight=None, 
		height=None, albumin_level=None, A1C=None, hemoglobin=None, o2_saturation=None, blood_pressure=None, bmi=None, deleted=None, name=None,
		last_name=None, date_of_admission=None, units=None, past_diagnosis=None, room=None):
		self.user = user
		self.date_of_record = date_of_record
		self.medical_record_number = medical_record_number
		self.gender = gender
		self.DOB = DOB
		self.unit_floor = unit_floor
		self.bed_type = bed_type
		self.ethnicity = ethnicity
		self.braden_score = braden_score
		self.mobility = mobility
		self.diagnosis = diagnosis
		self.incontinence = incontinence
		self.medication = medication
		self.weight = weight
		self.height = height
		self.albumin_level = albumin_level
		self.A1C = A1C
		self.hemoglobin = hemoglobin
		self.o2_saturation = o2_saturation
		self.blood_pressure = blood_pressure
		self.bmi = bmi
		self.deleted = deleted
		self.name = name
		self.last_name = last_name
		self.pa_id = pa_id
		self.date_of_admission = date_of_admission
		self.units = units
		self.past_diagnosis = past_diagnosis
		self.room = room

class PatientInfoReportJsonSerializer(JsonSerializer):
	__attributes__ = ['medical_record_number', 'gender', 'DOB', 'unit_floor', 'bed_type', 'ethnicity', 'braden_score', 'mobility', 
	'diagnosis', 'incontinence', 'medication', 'weight', 'height', 'bmi', 'albumin_level', 'A1C', 'hemoglobin', 'o2_saturation',
	'blood_pressure', 'deleted', 'name', 'last_name', 'pa_id', 'date_of_admission', 'units', 'date_of_record', 'user', 'past_diagnosis', 'room']
	__required__ = ['medical_record_number', 'gender', 'DOB', 'unit_floor', 'bed_type', 'ethnicity', 'braden_score', 'mobility', 
	'diagnosis', 'incontinence', 'medication', 'weight', 'height', 'bmi', 'albumin_level', 'A1C', 'hemoglobin', 'o2_saturation',
	'blood_pressure', 'deleted', 'name', 'last_name', 'pa_id', 'date_of_admission', 'units', 'date_of_record', 'user', 'past_diagnosis', 'room']
	__attribute_serializer__ = dict(last_seen='datetime', date_of_admission='date', DOB='date', date_of_record='datetime')
	__object_class__ = DBPatientHistory

@swagger.model
class DBPatientNote(db.Model):
	__tablename__ = 'patient_note'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	pa_id = db.Column(db.String(100), index=True)
	patient_site = db.Column(db.String(100), index=True)
	patient_site_other = db.Column(db.Text)
	dressing_application_surface = db.Column(db.String(100))
	dressing_application_surface_other = db.Column(db.Text)
	device_surrounding_dressing = db.Column(db.String(100))
	device_surrounding_dressing_other = db.Column(db.Text)
	reason_for_dressing_change = db.Column(db.String(100))
	reason_for_dressing_change_other = db.Column(db.Text)
	reason_for_dressing_removal = db.Column(db.String(100))
	reason_for_dressing_removal_other = db.Column(db.Text)
	tablet_issues = db.Column(db.String(100))
	tablet_issues_other = db.Column(db.Text)
	sensor_issues = db.Column(db.String(100))
	sensor_issues_other = db.Column(db.Text)
	support_contacted = db.Column(db.Boolean)
	support_reason = db.Column(db.Text)
	comments = db.Column(db.Text)
	occurred = db.Column(db.DateTime, index=True)
	user = db.Column(db.Text)


	def __init__(self, pa_id, patient_site, dressing_application_surface, device_surrounding_dressing, reason_for_dressing_change,
				reason_for_dressing_removal, tablet_issues, sensor_issues, support_contacted, occurred, user, comments=None, support_reason=None,
				patient_site_other=None, dressing_application_surface_other=None, device_surrounding_dressing_other=None,
				reason_for_dressing_change_other=None, reason_for_dressing_removal_other=None, tablet_issues_other=None, sensor_issues_other=None):
		self.pa_id = pa_id
		self.patient_site = patient_site
		self.dressing_application_surface = dressing_application_surface
		self.device_surrounding_dressing = device_surrounding_dressing
		self.reason_for_dressing_change = reason_for_dressing_change
		self.reason_for_dressing_removal = reason_for_dressing_removal
		self.tablet_issues = tablet_issues
		self.sensor_issues = sensor_issues
		self.support_contacted = support_contacted
		self.occurred = occurred
		self.patient_site = patient_site
		self.occurred = occurred
		self.user = user
		self.patient_site_other = patient_site_other
		self.dressing_application_surface_other = dressing_application_surface_other
		self.device_surrounding_dressing_other = device_surrounding_dressing_other
		self.reason_for_dressing_change_other = reason_for_dressing_change_other
		self.reason_for_dressing_removal_other = reason_for_dressing_removal_other
		self.tablet_issues_other = tablet_issues_other
		self.sensor_issues_other = sensor_issues_other

class PatientNoteJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'pa_id', 'patient_site', 'dressing_application_surface', 'reason_for_dressing_change', 'reason_for_dressing_removal',
					'tablet_issues', 'sensor_issues' , 'support_contacted', 'occurred', 'user', 'comments', 'support_contacted',
					'dressing_application_surface_other', 'device_surrounding_dressing_other', 'reason_for_dressing_change_other',
					'reason_for_dressing_removal_other', 'tablet_issues_other', 'sensor_issues_other']
	__required__ = ['id', 'pa_id', 'patient_site', 'dressing_application_surface', 'reason_for_dressing_change', 'reason_for_dressing_removal',
					'tablet_issues', 'sensor_issues' , 'support_contacted', 'occurred', 'user', 'comments', 'support_contacted',
					'dressing_application_surface_other', 'device_surrounding_dressing_other', 'reason_for_dressing_change_other',
					'reason_for_dressing_removal_other', 'tablet_issues_other', 'sensor_issues_other']
	__attribute_serializer__ = dict(occurred='datetime')
	__object_class__ = DBPatientNote

@swagger.model
class DBRepositionReportData(db.Model):
	__tablename__ = 'reposition_report_data'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	date = db.Column(db.Date, index=True)
	pa_id = db.Column(db.String(100), index=True)
	unit_floor = db.Column(db.String(100), index=True)
	all = db.Column(db.Boolean)
	data = db.Column(db.Text)

	def __init__(self, date, data, pa_id=None, unit_floor=None, all=None):
		self.date = date
		self.data = data
		self.pa_id = pa_id
		self.unit_floor = unit_floor
		self.all = all


class DBRepositionReportDataJsonSerializer(JsonSerializer):
	__attributes__ = ['date', 'pa_id', 'unit_floor', 'data']
	__required__ = ['date', 'pa_id', 'unit_floor', 'data']
	__attribute_serializer__ = dict()
	__object_class__ = DBRepositionReportData

@swagger.model
class DBUser(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	email = db.Column(db.String(150), unique=True, index=True)
	name = db.Column(db.Text)
	password = db.Column(db.String(100))
	phone_number = db.Column(db.String(25))
	eula_accepted = db.Column(db.Boolean)
	role = db.Column(db.String(50))
	previous_sms_sent = db.Column(db.DateTime)
	password_changed = db.Column(db.DateTime)
	deleted = db.Column(db.Boolean)
	email_notification = db.Column(db.Boolean)

	def __init__(self, name, password, email, phone_number, eula_accepted=None, role=None, previous_sms_sent=None, password_changed=None, 
		deleted=None, email_notification=None):
		self.password = password
		self.email = email
		self.name = name
		self.phone_number = phone_number
		self.eula_accepted = eula_accepted
		self.role = role
		self.previous_sms_sent = previous_sms_sent
		self.password_changed = password_changed
		self.deleted = deleted
		self.email_notification = email_notification

class UserJsonSerializer(JsonSerializer):
	__attributes__ = ['id', 'email', 'name', 'phone_number', 'eula_accepted', 'role', 'deleted', 'email_notification']
	__required__ = ['id', 'password', 'email', 'name', 'phone_number', 'eula_accepted', 'role', 'deleted', 'email_notification']
	__attribute_serializer__ = dict(last_seen='datetime', patients='patient')
	__object_class__ = DBUser

	def __init__(self, timezone=None):
		super(UserJsonSerializer, self).__init__(timezone)
		self.serializers['patient'] = dict(
			serialize=lambda x:
				[PatientJsonSerializer(timezone).serialize(xx) for xx in x],
			deserialize=lambda x:
				[PatientJsonSerializer(timezone).deserialize(xx) for xx in x]
		)

