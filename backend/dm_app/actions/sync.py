from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp, strtotimestamp, utctotimestamp
import copy
from datetime import datetime

class Sync(Resource):
	@swagger.operation(
		notes='updates body locations including wound status, also device settings',
		nickname='device sync',
		parameters=[
			{
				"name": "sensors",
				"description": "event message",
				"required": True,
				"allowMultiple": True,
				"dataType": DBBodyLocation.__name__,
				"paramType": "body"
			}
		  ],
		responseMessages=[
			{
				"code": 204,
				"message": "Events successfully created"
			},
			{
				"code": 400,
				"message": "Bad request"
			}
		  ]
		)
	@validate_jwt_user_token
	def post(self, user=None, sub=None, device_id=None, patient_id=None, medical_record_number=None, device_serial=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			data = copy.deepcopy(request.json)
			device = DBDevice.query.filter_by(id=device_id).first()
			if device and not device.deleted: # and (device.last_web_change and device.last_device_sync and device.last_web_change > device.last_device_sync) or (device.last_web_change and not device.last_device_sync):
				if 'sensors' in data:
					p = DBPatient.query.filter_by(id=patient_id).first()
					if p and not p.deleted:
						for sensor in data['sensors']:
							self.process_sensor(device, sensor, p, medical_record_number)

						if device and 'globals' in data:
							glob = data['globals']
							if glob.get('language'): device.language = glob['language']
							if glob.get('alarm_volume'): device.alarm_volume = glob['alarm_volume']
							if glob.get('alarm_sound'): device.alarm_sound = glob['alarm_sound']
							if glob.get('alarm_duration'): device.alarm_duration = glob['alarm_duration']

						status_code = status.HTTP_204_NO_CONTENT
						device.last_device_sync = utcformysqlfromtimestamp(nowtimestamp())
						#db.session.commit()
					else:
						response = {'error' : "DEVICE NOT ASSIGNED"}
					db.session.commit()
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=None, device=device_serial, 
			device_header=request.headers.get(DEVICE_ID_HEADER), version_header=request.headers.get(ANDROID_VERSION_HEADER))
		return response, status_code

	# device polls server for settings changes every so often and if there's a change, it adopts these changes
	@validate_jwt_user_token
	def get(self, device_id=None, device_serial=None, patient_id=None, medical_record_number=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			device = DBDevice.query.filter_by(serial=device_serial).first()
			if device and not device.deleted:
				bl = DBBodyLocation.query.filter_by(patient_id=device.patient_id).all()
				if bl:
					response = {}
					response['sensors'] = []
					for x in range(len(bl)):
						dict = {}
						dict['JSID'] = bl[x].JSID
						dict['alarm_clear_multiple'] = bl[x].alarm_clear_multiple
                                                dict['alarm_threshold_minutes'] = bl[x].alarm_threshold_minutes
                                                dict['wound_stage'] = bl[x].wound_stage
                                                dict['is_wound'] = bl[x].is_wound
                                                dict['wound_measurement'] = bl[x].wound_measurement
                                                dict['wound_existing_since'] = bl[x].wound_existing_since.strftime('%Y.%m.%d') if bl[x].wound_existing_since else None
                                                dict['wound_outcome'] = bl[x].wound_outcome
                                                dict['wound_acquisition'] = bl[x].wound_acquisition

						response['sensors'].append(dict)

					response['globals'] = {}
					response['globals']['language'] = device.language
					response['globals']['alarm_volume'] = device.alarm_volume
					response['globals']['alarm_sound'] = device.alarm_sound
					response['globals']['alarm_duration'] = device.alarm_duration
					status_code = status.HTTP_200_OK
					device.last_device_sync = utcformysqlfromtimestamp(nowtimestamp())
				else:
					response = {'error' : UNASSIGNED_DEVICE_ERROR}
				db.session.commit()
			else:
				response = {'error' : DEVICE_DELETED}
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST
		return response, status_code

	def return_sync(self, patient_id, device, medical_record_number):
		struct_logger.msg(instance=LOGGING_INSTANCE, device_serial=device.serial, event='return sync')
		sensors = []
		for JSID in BODY_LOCATIONS:
			location = DBBodyLocation.query.filter_by(patient_id=patient_id, JSID=JSID).first()
			location_dict = BodyLocationJsonSerializer().serialize(location)
			location_dict.pop('medical_record_number')
			sensors.append(location_dict)
		glob = {}
		glob['language'] = device.language
		glob['alarm_volume'] = device.alarm_volume
		glob['alarm_sound'] = device.alarm_sound
		glob['alarm_duration'] = device.alarm_duration
		glob['medical_record_number'] = medical_record_number

		p = DBPatient.query.filter_by(id=patient_id).first()
		glob['name'] = p.name

		device.last_device_sync = utcformysqlfromtimestamp(nowtimestamp())
		db.session.commit()

		response = { 'sensors' : sensors, 'globals' : glob}

		return response

	def process_sensor(self, device, sensor, patient, medical_record_number):
		location = DBBodyLocation.query.filter_by(patient_id=patient.id, JSID=sensor['JSID'].upper()).first()
		if location:
			sensor_added = False
			sensor_removed = False
			location_changed = False
			pressure_doesnt_match = False
			sensor_inactive = False

			location.last_seen = utcformysqlfromtimestamp(nowtimestamp())

			if 'JSID' in sensor: location.JSID = sensor.get('JSID').upper()
			#if 'type' in sensor: location.type = sensor.get('type')
			if 'stopped' in sensor: location.stopped = sensor.get('stopped')
			if 'force_state' in sensor: location.force_state = sensor.get('force_state')
			if 'distance' in sensor: location.distance = sensor.get('distance')
			if 'fast_blink' in sensor: location.fast_blink = sensor.get('fast_blink')
			if 'battery' in sensor: location.battery = sensor.get('battery')
			if 'binary_state' in sensor: location.binary_state = sensor.get('binary_state')
			if 'under_pressure_milliseconds' in sensor: location.under_pressure_milliseconds = sensor.get('under_pressure_milliseconds')
			if 'has_previous_alert' in sensor: location.has_previous_alert = sensor.get('has_previous_alert')
			if 'sensor_removal' in sensor: location.sensor_removal = sensor.get('sensor_removal')

			if 'sensor_serial' in sensor: 
				if sensor.get('sensor_serial') == SENSOR_UNASSIGNED and sensor.get('sensor_serial') != location.sensor_serial:
					sensor_removed = True
					location_changed = True
				elif location.sensor_serial == SENSOR_UNASSIGNED and sensor.get('sensor_serial') != location.sensor_serial:
					sensor_added = True
					location_changed = True
				if sensor.get('sensor_serial') == SENSOR_UNASSIGNED:
					latest = DBEvent.query.filter_by(patient_id=patient.id, location=location.JSID, latest=str(
					medical_record_number) + str(location.JSID)).first()
					if latest and latest.message != SENSOR_REMOVED:
						struct_logger.msg(instance=LOGGING_INSTANCE, event='Removed because latest does not match', location=location.JSID,
							medical_record_number=medical_record_number, sensor_serial=location.sensor_serial)
						sensor_removed = True
				location.sensor_serial = sensor.get('sensor_serial')
			
			if 'alarm_clear_multiple' in sensor: 
				if location.alarm_clear_multiple != sensor.get('alarm_clear_multiple'):
					location_changed = True
				location.alarm_clear_multiple = sensor.get('alarm_clear_multiple')

			if 'alarm_threshold_minutes' in sensor: 
				if location.alarm_threshold_minutes != sensor.get('alarm_threshold_minutes'):
					location_changed = True
				location.alarm_threshold_minutes = sensor.get('alarm_threshold_minutes')
			
			if 'pressure_state' in sensor:
				latest_active = DBEvent.query.filter_by(
					patient_id=patient.id,
					location=location.JSID
				).filter(
					DBEvent.message.in_(('PRESSURE_RISING', 'PRESSURE_ALARM', 'PRESSURE_RECURRING', 'SENSOR CHANGED'))
				).order_by('id desc').first()
				pre_latest = DBEvent.query.filter_by(patient_id=patient.id, location=location.JSID)[-2]
				latest = DBEvent.query.filter_by(patient_id=patient.id, location=location.JSID, latest=str(
					medical_record_number) + str(location.JSID)).first()
				if(latest_active and latest and
						(latest_active.message == 'SENSOR CHANGED' and latest_active.instance < datetime.now() - timedelta(days=1)
						 or latest_active.range_start and latest_active.range_start < datetime.now() - timedelta(days=1))
				   and latest.message != "INACTIVE_FOR_24H"):
					sensor_inactive = True
				elif (latest and (latest.message.upper() != sensor.get('pressure_state').upper()) and latest.message.upper() != "INACTIVE_FOR_24H"
					or latest and latest.message.upper() == "INACTIVE_FOR_24H" and pre_latest and (pre_latest.message.upper() != sensor.get('pressure_state').upper())):
					pressure_doesnt_match = True
				location.pressure_state = sensor.get('pressure_state')

			
			if 'site_assessment' in sensor: 
				if location.site_assessment != sensor.get('site_assessment'):
					location_changed = True
				location.site_assessment = sensor.get('site_assessment')
			
			if 'wound_alarm_threshold_minutes' in sensor: 
				if location.wound_alarm_threshold_minutes != sensor.get('wound_alarm_threshold_minutes'):
					location_changed = True
				location.wound_alarm_threshold_minutes = sensor.get('wound_alarm_threshold_minutes')

			if 'wound_alarm_clear_multiple' in sensor: 
				if location.wound_alarm_clear_multiple != sensor.get('wound_alarm_clear_multiple'):
					location_changed = True
				location.wound_alarm_clear_multiple = sensor.get('wound_alarm_clear_multiple')

			if 'previous_alarm_threshold_hours' in sensor: 
				if location.previous_alarm_threshold_hours != sensor.get('previous_alarm_threshold_hours'):
					location_changed = True
				location.previous_alarm_threshold_hours = sensor.get('previous_alarm_threshold_hours')


			new_wound = False
			new_existing_wound = False
			if 'is_wound' in sensor:
				if location.is_wound != sensor.get('is_wound'):
					location_changed = True
					if sensor.get('is_wound') == True:
						new_wound = True
				location.is_wound = sensor.get('is_wound')

			if sensor.get('wound_stage'):
				if location.wound_stage != sensor.get('wound_stage'):
					location_changed = True
				location.wound_stage = sensor.get('wound_stage')

			if sensor.get('wound_measurement'):
				if location.wound_measurement != sensor.get('wound_measurement'):
					location_changed = True
				location.wound_measurement = sensor.get('wound_measurement')

			if 'wound_outcome' in sensor: 
				if location.wound_outcome != sensor.get('wound_outcome'):
					location_changed = True
				location.wound_outcome = sensor.get('wound_outcome')

			if 'wound_acquisition' in sensor: 
				if location.wound_acquisition != sensor.get('wound_acquisition'):
					location_changed = True
				location.wound_acquisition = sensor.get('wound_acquisition')

			existing_wound = sensor.get('existing_wound', False)
			if existing_wound:
				if location.existing_wound != sensor.get('existing_wound'):
					location_changed = True
					if sensor.get('existing_wound') == True:
						new_existing_wound = True
				location.existing_wound = existing_wound

			if 'wound_existing_since' in sensor and sensor.get('wound_existing_since'):
				compare_sync = strtotimestamp(sensor.get('wound_existing_since').replace('.', '-'))
				compare_location = None
				if location.wound_existing_since:
					compare_location = utctotimestamp(location.wound_existing_since)
				if compare_location != compare_sync:
					location_changed = True
				time = sensor.get('wound_existing_since').replace('.', '-')

				location.wound_existing_since = utcformysqlfromtimestamp(strtotimestamp(time))
			elif new_wound or new_existing_wound:
				location.wound_existing_since = datetime.now().isoformat()

			location_copy = copy.deepcopy(location)

			if sensor_removed:
				self.record_event(patient, device.id, location_copy, SENSOR_REMOVED)

			#if location_changed:
				#TODO
				#print str(device.serial) + ' record location history '
				#self.record_location_history(dict(vars(location)), location.id, sensor['JSID'])

			if pressure_doesnt_match:
				self.record_event(patient, device.id, location_copy, sensor.get('pressure_state'))

			if sensor_inactive:
				self.record_event(patient, device.id, location_copy, 'INACTIVE_FOR_24H')

			if sensor_added:
				if sensor.get('pressure_state'):
					message = sensor.get('pressure_state')
				else:
					message = 'NO_PRESSURE'
				self.record_event(patient, device.id, location_copy, message)

			db.session.commit()

	def record_event(self, patient, device_id, body_location, message):
		struct_logger.msg(instance=LOGGING_INSTANCE, device=device_id, event='record event',message=message)
		record_history = True

		previous_event = DBEvent.query.filter_by(patient_id=patient.id, location=body_location.JSID.upper(),
			latest=str(patient.medical_record_number) + str(body_location.JSID.upper())).first()
		if previous_event:
			previous_event.range_end = utcformysqlfromtimestamp(nowtimestamp())
			previous_event.latest = None
			db.session.commit()
		else:
			struct_logger.msg(instance=LOGGING_INSTANCE, event='No Previous Event', medical_record_number=patient.medical_record_number,
			 location=body_location.JSID.upper())

		event_json = {}
		event_json['medical_record_number'] = patient.medical_record_number
		event_json['unit_floor'] = patient.unit_floor
		event_json['patient_id'] = patient.id
		event_json['device_id'] = device_id
		event_json['location'] = body_location.JSID
		event_json['message'] = message
		event_json['range_start'] = utcformysqlfromtimestamp(nowtimestamp())
		event_json['latest'] = str(patient.medical_record_number) + str(body_location.JSID)
		event_json['body_location_id'] = body_location.id
		event = DBEvent(**event_json)
		try:
			db.session.add(event)
		except Exception as e:
			if 'Duplicate' in e.message:
				struct_logger.msg(instance=LOGGING_INSTANCE, event='duplicate ignored', message=e.message)
				record_history = False
				db.session.rollback()
			else:
				raise e

		if record_history:
			event_history = {}
			event_history['unit_floor'] = patient.unit_floor
			event_history['medical_record_number'] = patient.medical_record_number
			event_history['event_type'] = EVENT_HISTORY_DICT[message.upper()]
			event_history['occurred'] = utcformysqlfromtimestamp(nowtimestamp())
			event_history['sensor_serial'] = body_location.sensor_serial
			event_history['location'] = body_location.JSID
			event_history['battery'] = body_location.battery
			event_history['distance'] = body_location.distance
			event_history['alarm_threshold_minutes'] = body_location.alarm_threshold_minutes
			event_history['alarm_clear_multiple'] = body_location.alarm_clear_multiple
			event_history['site_assessment'] = body_location.site_assessment
			event_history['sensor_removal'] = body_location.sensor_removal
			event_history['wound_alarm_threshold_minutes'] = body_location.wound_alarm_threshold_minutes
			event_history['wound_alarm_clear_multiple'] = body_location.wound_alarm_clear_multiple
			event_history['previous_alarm_threshold_hours'] = body_location.previous_alarm_threshold_hours
			history = DBEventHistory(**event_history)
			db.session.add(history)

		try:
			db.session.commit()
		except Exception as e:
			if not 'Duplicate' in e.message:
				raise e
			else:
				struct_logger.msg(instance=LOGGING_INSTANCE, event='duplicate ignored', message=e.message)
				db.session.rollback()

	def record_location_history(self, location_dict, location_id, JSID):
		location_dict['JSID'] = JSID
		location_dict['body_location_id'] = location_id
		location_dict['user'] = 'Sync'
		location_dict['date_of_record'] = utcformysqlfromtimestamp(nowtimestamp())
		location_dict.pop('id', None)
		location_dict.pop('patient_id', None)
		location_dict.pop('deleted', None)
		location_dict.pop('_sa_instance_state', None)

		location_history = DBBodyLocationHistory(**location_dict)
		db.session.add(location_history)
		db.session.commit()
