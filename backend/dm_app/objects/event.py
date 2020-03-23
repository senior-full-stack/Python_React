from dm_app import *
from ..actions.alert import Alert
from ..models import *
from ..globs import *
from ..utils import validate_jwt_user_token, log, profiled, validate_jwt_device_token, offload_request
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp
from dateutil import rrule
from dateutil import tz
import copy

class Event(Resource):
	@swagger.operation(
		notes='none',
		responseClass=DBEvent.__name__,
		nickname='get events',
		parameters=[
			{
				"name": "medical_record_number",
				"description": "a patient's medical record number to filter events",
				"required": False,
				"dataType": "string",
				"paramType": "url param"
			}
		  ],
		responseMessages=[
			{
				"code": 200,
				"message": "An array of events"
			},
			{
				"code": 400,
				"message": "Bad request"
			}
		  ]
		)
	@validate_jwt_user_token
	def get(self, user=None, sub=None, event=None, role=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			if event:
				response = DBEvent.query.filter_by(id=event).all()
			elif request.args.get('medical_record_number'):
				result = DBEvent.query.filter_by(medical_record_number=request.args.get('medical_record_number')).all()
				response = []
				for item in result:
					response.append(EventJsonSerializer().serialize(item))
				response = {'events' : response }
				status_code = status.HTTP_200_OK
			else:
				result = DBEvent.query.all()
				response = []
				for item in result:
					response.append(EventJsonSerializer().serialize(item))
				response = {'events' : response }
				status_code = status.HTTP_200_OK
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)
		return response, status_code

	@swagger.operation(
		notes='will trigger sms alerts',
		nickname='post events',
		parameters=[
			{
			  "name": "pressure_events",
			  "description": "event message",
			  "required": True,
			  "allowMultiple": True,
			  "dataType": DBEvent.__name__,
			  "paramType": "body"
			},
			{
			  "name": "message",
			  "description": "event message",
			  "required": True,
			  "dataType": "string",
			  "paramType": "body"
			},
			{
			  "name": "instance",
			  "description": "is event instance",
			  "required": False,
			  "dataType": "boolean",
			  "paramType": "body"
			},
			{
			  "name": "range_start",
			  "description": "event start time",
			  "required": False,
			  "dataType": "DateTime",
			  "paramType": "body"
			},
			{
			  "name": "range_end",
			  "description": "event end time",
			  "required": False,
			  "dataType": "DateTime",
			  "paramType": "body"
			},
			{
			  "name": "location",
			  "description": "event location",
			  "required": False,
			  "dataType": "string",
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
	def post(self, device_id=None, patient_id=None, medical_record_number=None, device_serial=None, user=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			p = DBPatient.query.filter_by(id=patient_id).first()
			if p and p.deleted == False:
				if request.content_length > MAX_CONTENT_LENGTH:
					offload_request(device_id, patient_id, request.data, 'event', 'post')
					status_code = status.HTTP_204_NO_CONTENT
					log_request = {'message' : 'request too long, sent to table',  'length' : request.content_length}
				else:
					data = copy.deepcopy(request.json)
					log_request = request.json
					#sort events by time
					data['pressure_events'] = sorted(data['pressure_events'], key=lambda x: x['epoch_timestamp'], reverse=False)
					for event in data['pressure_events']:
						self.process_event(event, p, device_id)
						status_code = status.HTTP_204_NO_CONTENT
			else:
				response = {'error' : UNASSIGNED_DEVICE_ERROR}
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=None, device=device_serial, 
			device_header=request.headers.get(DEVICE_ID_HEADER), version_header=request.headers.get(ANDROID_VERSION_HEADER))
		return response, status_code

	def process_event(self, event, patient, device_id):
		#TODO send patient object in
		event_obj = None

		event['medical_record_number'] = patient.medical_record_number
		event['unit_floor'] = patient.unit_floor
		event['patient_id'] = patient.id
		event['device_id'] = device_id

		body_location = None

		if 'location' in event:
			event['location'] = event['location'].upper()
			body_location = DBBodyLocation.query.filter_by(medical_record_number=patient.medical_record_number, 
				JSID=event['location']).first()
			if body_location:
				event['body_location_id'] = body_location.id

		if event['message'].upper() in EVENT_TYPE_SINGLE_POINT or 'SENSOR CHANGED' in event['message'].upper():
			event['instance'] = utcformysqlfromtimestamp(event['epoch_timestamp'])

			if event['message'].upper() == 'PATIENT WAS TURNED BY CAREGIVER':
				self.log_turned_response(event, patient.medical_record_number, patient.unit_floor)

			if 'SENSOR CHANGED' in event['message'].upper():
				m = event['message']
				body_location.sensor_serial = m.split(' - ')[1]
				event['message'] = 'SENSOR CHANGED'

			if 'DEVICE IS UNPLUGGED FROM POWER' in event['message'].upper():
				previous_unplugged = DBEvent.query.filter(DBEvent.medical_record_number == patient.medical_record_number, DBEvent.message.in_(['DEVICE IS PLUGGED INTO POWER', 
					'DEVICE IS UNPLUGGED FROM POWER'])).order_by(DBEvent.instance.desc()).first()
				if not previous_unplugged or previous_unplugged.message.upper() != event['message'].upper():
					d = DBDevice.query.filter_by(id=device_id).first()
					subject = '%s: Room %s, device unplugged' % (FACILITY, patient.room)
					message = 'Device %s unplugged from power at %s' % (d.serial, str(self.convert_date_to_tz(event['instance'])))
					Alert().email_admins(DEVICE_UNPLUGGED, message, subject)

			if 'DEVICE IS PLUGGED INTO POWER' in event['message'].upper():
				previous_unplugged = DBEvent.query.filter(DBEvent.medical_record_number == patient.medical_record_number, DBEvent.message.in_(['DEVICE IS PLUGGED INTO POWER', 
					'DEVICE IS UNPLUGGED FROM POWER'])).order_by(DBEvent.instance.desc()).first()
				if not previous_unplugged or previous_unplugged.message.upper() != event['message'].upper():
					d = DBDevice.query.filter_by(id=device_id).first()
					subject = '%s: Room %s, device plugged in' % (FACILITY, patient.room)
					message = 'Device %s plugged into power at %s' % (d.serial, str(self.convert_date_to_tz(event['instance'])))
					Alert().email_admins(DEVICE_PLUGGED_IN, message, subject)

			if 'epoch_timestamp' in event:
				event.pop('epoch_timestamp')
			event_obj = DBEvent(**event)
			db.session.add(event_obj)
			process_history = True


		elif event['message'].upper() in EVENT_TYPE_RANGE:
			time = utcformysqlfromtimestamp(event['epoch_timestamp'])
			event['range_start'] = time

			duplicate_event = DBEvent.query.filter_by(patient_id=patient.id, range_start=time, location=event['location'].upper()).first()
			if not duplicate_event:
				if event['message'].upper() == 'PRESSURE_ALARM':
						self.log_alarm(event, patient.medical_record_number, patient.unit_floor)

				previous_event = DBEvent.query.filter_by(patient_id=patient.id, location=event['location'].upper(), 
					latest=str(patient.medical_record_number) + str(event['location'].upper())).first()
				if previous_event:
					if previous_event.message.upper() == 'PRESSURE_ALARM' and event['message'].upper() != 'PRESSURE_ALARM':
						self.log_alarm_clear(event, previous_event, patient.medical_record_number, patient.unit_floor)

					previous_event.range_end = utcformysqlfromtimestamp(event['epoch_timestamp'])
					previous_event.latest = None
					db.session.commit()
				else:
					struct_logger.msg(instance=LOGGING_INSTANCE, event='No Previous Event', medical_record_number=patient.medical_record_number, location=event['location'].upper(), message=event['message'])

				event['latest'] = str(patient.medical_record_number) + str(event['location'].upper())

				event.pop('epoch_timestamp')
				event_obj = DBEvent(**event)
				try:
					db.session.add(event_obj)
					db.session.commit()
				except Exception as e:
					if 'Duplicate' in e.message:
						struct_logger.msg(instance=LOGGING_INSTANCE, event='duplicate ignored', exception=e.message)
						event_obj = None
					else:
						raise e
			else:
				struct_logger.msg(instance=LOGGING_INSTANCE, event='Event Duplicate', medical_record_number=patient.medical_record_number, 
					location=event['location'].upper(), message=event['message'], time=time)

		#don't process if duplicate
		if event_obj:
			activation = DBPatientActivation.query.filter_by(patient_id=patient.id).order_by(DBPatientActivation.id.desc()).first()

			if not activation:
				new_activation = DBPatientActivation(patient.id, ACTIVATED_STATUS, utcformysqlfromtimestamp(nowtimestamp()), ACTIVATED_REASON, 
					utcformysqlfromtimestamp(nowtimestamp()), None, None)
				db.session.add(new_activation)
			elif activation.status == INACTIVATED_STATUS:
				reactivation = DBPatientActivation(patient.id, REACTIVATED_STATUS, utcformysqlfromtimestamp(nowtimestamp()), REACTIVATED_REASON, 
					utcformysqlfromtimestamp(nowtimestamp()), None, None)
				db.session.add(reactivation)


			# log
			event_history = {}
			event_history['medical_record_number'] = patient.medical_record_number
			event_history['unit_floor'] = patient.unit_floor

			message = event['message'].upper()

			if message in EVENT_TYPE_SINGLE_POINT and not 'SENSOR ' in event['message'].upper():
				event_history['event_type'] = EVENT_HISTORY_DICT[message]
				event_history['occurred'] = event['instance']

			elif 'SENSOR ' in event['message'].upper():
				event_history['event_type'] = EVENT_HISTORY_DICT[message]
				event_history['occurred'] = event['instance']
				event_history['sensor_serial'] = body_location.sensor_serial
				event_history['location'] = body_location.JSID


			elif 'PRESSURE_ALARM' in message or 'NO_PRESSURE' in message or 'PRESSURE_RISING' in message or 'PRESSURE_FALLING' in message or \
			'SENSOR_STOPPED' in message or 'PRESSURE_RECURRING' in message or 'RECENT_PRESSURE' in message:
				event_history['event_type'] = EVENT_HISTORY_DICT[message]
				event_history['occurred'] = event['range_start']
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

			if 'event_type' in event_history:
				history = DBEventHistory(**event_history)
				db.session.add(history)

			db.session.commit()

	def convert_date_to_tz(self, date):
		if USE_TIMEZONE:
			to_zone = tz.gettz(TIMEZONE)
			from_zone = tz.gettz('UTC')
			utc = date.replace(tzinfo=from_zone)
			converted_date = utc.astimezone(to_zone)
		else:
			converted_date = date
		return converted_date

	def log_turned_response(self, event, medical_record_number, unit_floor):
		admin_default = DBAdminDefault.query.first()
		window_start = event['instance'] - timedelta(minutes=admin_default.alert_reponse_window)
		previous_turn = DBEvent.query.filter(DBEvent.patient_id==event['patient_id'], DBEvent.range_end >= window_start, 
			DBEvent.range_end <= event['instance'], DBEvent.message == 'PATIENT WAS TURNED BY CAREGIVER').order_by(DBEvent.range_start.desc()).all()
		if not previous_turn:
			previous_events = DBEvent.query.filter(DBEvent.patient_id==event['patient_id'], DBEvent.range_end >= window_start, 
				DBEvent.range_end <= event['instance'], DBEvent.message == 'PRESSURE_ALARM').order_by(DBEvent.range_start.desc()).all()

			dates = {}

			for ev in previous_events:
				converted_date = self.convert_date_to_tz(ev.range_end)
				date = converted_date.date()
				hour = converted_date.hour
				if date not in dates:
					dates[date] = {}
				if hour not in dates[date]:
					dates[date][hour] = 0
				dates[date][hour] += 1

			for d in dates:
				for h in dates[d]:
					self.write_response_records(d, h, medical_record_number, unit_floor, caregiver_repositions=dates[d][h], patient_repositions=-1*(dates[d][h]))




	def log_alarm(self, event, medical_record_number, unit_floor):
		log_date = self.convert_date_to_tz(event['range_start'])

		date = log_date.date()
		hour = log_date.hour

		self.write_response_records(date, hour, medical_record_number, unit_floor, alarms_occurred=1)


	def log_alarm_clear(self, event, previous_event, medical_record_number, unit_floor):
		converted_event_date = self.convert_date_to_tz(event['range_start'])
		converted_previous_date = self.convert_date_to_tz(previous_event.range_start)
		date = converted_event_date.date()
		hour = converted_event_date.hour
		delta = converted_event_date - converted_previous_date
		previous_date = converted_previous_date.date()
		previous_hour = converted_previous_date.hour

		total_repositions = 1

		date_different = False
		hour_different = False

		admin_default = DBAdminDefault.query.first()
		window_start = event['range_start'] - timedelta(minutes=admin_default.alert_reponse_window)
		previous_turn = DBEvent.query.filter(DBEvent.patient_id == event['patient_id'], DBEvent.message == 'PATIENT WAS TURNED BY CAREGIVER',
			DBEvent.instance >= window_start, DBEvent.instance <= event['range_start']).first()
		if previous_turn:
			caregiver_repositions = 1
			patient_repositions = 0
		else:
			caregiver_repositions = 0
			patient_repositions = 1


		if converted_event_date.date() != converted_previous_date.date():
			date_different = True
		if converted_event_date.hour != converted_previous_date.hour:
			hour_different = True

		if not date_different and not hour_different:
			minute_range_start = converted_previous_date.minute
			minute_range_end = converted_event_date.minute

			self.write_response_records(date, hour, medical_record_number, unit_floor, caregiver_repositions=caregiver_repositions,
				patient_repositions=patient_repositions, total_repositions=total_repositions, minute_range_start=minute_range_start,
				minute_range_end=minute_range_end)

			#response_patient = DBAlarmResponsePatient.query.filter_by(date=date, hour=hour, pa_id=medical_record_number)

		else:
			for dt in rrule.rrule(rrule.HOURLY, dtstart=converted_previous_date.replace(minute=0, second=0, microsecond=0), until=converted_event_date):
				if dt.date() == previous_date and dt.hour == previous_hour:
					#start
					self.write_response_records(dt.date(), dt.hour, medical_record_number, unit_floor, 
						minute_range_start=converted_previous_date.minute, minute_range_end=59)
				elif dt.date() == date and dt.hour == hour:
					#end
					self.write_response_records(dt.date(), dt.hour, medical_record_number, unit_floor, caregiver_repositions=caregiver_repositions,
						patient_repositions=patient_repositions, total_repositions=total_repositions, minute_range_start=0, 
						minute_range_end=converted_event_date.minute)
				else:
					#middle
					self.write_response_records(dt.date(), dt.hour, medical_record_number, unit_floor, minute_range_start=0, minute_range_end=59)


	def write_response_records(self, date, hour, pa_id, unit_floor, alarms_occurred=None, patient_repositions=None, 
		caregiver_repositions=None, total_repositions=None, minute_range_start=None, minute_range_end=None):

		alarm_response = DBAlarmResponse.query.filter_by(date=date, hour=hour, pa_id=pa_id).first()
		if alarm_response:
			if alarms_occurred:
				alarm_response.alarms_occurred += alarms_occurred
			if patient_repositions:
				alarm_response.patient_repositions += patient_repositions
				if alarm_response.patient_repositions < 0:
					alarm_response.patient_repositions = 0
			if caregiver_repositions:
				alarm_response.caregiver_repositions += caregiver_repositions
			if total_repositions:
				alarm_response.total_repositions += total_repositions
			if minute_range_start != None and minute_range_end != None:
				minutes_list = list(alarm_response.minutes_alarming)
				for x in range(minute_range_start, minute_range_end + 1):
					minutes_list[x] = '1'
				alarm_response.minutes_alarming = "".join(minutes_list)
			alarm_response.unit_floor = unit_floor

		if not alarm_response:
			if not alarms_occurred:
				alarms_occurred = 0
			if not patient_repositions:
				patient_repositions = 0
			elif patient_repositions < 0:
				patient_repositions = 0
			if not caregiver_repositions:
				caregiver_repositions = 0
			if not total_repositions:
				total_repositions = 0
			minutes_alarming = ''
			for x in range(0, 60):
				minutes_alarming += '0'
			minutes_list = list(minutes_alarming)
			if minute_range_start != None and minute_range_end != None:
				for x in range(minute_range_start, minute_range_end + 1):
					minutes_list[x] = '1'
				minutes_alarming = "".join(minutes_list)
			alarm_response = DBAlarmResponse(date, hour, pa_id, alarms_occurred, patient_repositions, 
				caregiver_repositions, total_repositions, minutes_alarming, unit_floor)
			db.session.add(alarm_response)
		db.session.commit()



