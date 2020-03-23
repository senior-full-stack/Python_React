from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
import copy
from ..rfc3339 import nowtimestamp, utcformysqlfromtimestamp

class BodyLocation(Resource):
	@swagger.operation(
		notes='none',
		responseClass=DBBodyLocation.__name__,
		nickname='get body locations',
		parameters=[
			{
			  "name": "medical_record_number",
			  "description": "a patient's medical record number to filter locations",
			  "required": False,
			  "dataType": "string",
			  "paramType": "url param"
			}
		  ],
		responseMessages=[
			{
			  "code": 200,
			  "message": "An array of body locations, sorted by medical_record_number"
			},
			{
			  "code": 404,
			  "message": "No body locations found"
			}
		  ]
		)
	@validate_jwt_user_token
	def get(self, user=None, sub=None, medical_record_number=None, location=None, role=None):
		status_code = status.HTTP_404_NOT_FOUND
		response = None
		locations = None
		print location
		p = DBPatient.query.filter_by(medical_record_number=medical_record_number).first()
		if p and p.deleted == False and location:
			body_location = DBBodyLocation.query.filter_by(medical_record_number=medical_record_number, JSID=location.upper()).first()
			if body_location:
				response = BodyLocationJsonSerializer().serialize(body_location)
				status_code = status.HTTP_200_OK
		elif p and p.deleted == False:
			locations = DBBodyLocation.query.filter_by(medical_record_number=medical_record_number).all()
			if locations:
				response = []
			for body_location in locations:
				response.append(BodyLocationJsonSerializer().serialize(body_location))
			response = {'BodyLocations' : response}
			status_code = status.HTTP_200_OK

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)
		return response, status_code

	@swagger.operation(
		notes='updates body locations including wound status, also device settings',
		nickname='update body location',
		parameters=[
			{
			  "name": "location",
			  "description": "location to be updated",
			  "required": True,
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
	def put(self, user=None, sub=None, medical_record_number=None, location=None, role=None):
		status_code = status.HTTP_404_NOT_FOUND
		response = None
		try:
			sensor = copy.deepcopy(request.json)

			location = DBBodyLocation.query.filter_by(medical_record_number=medical_record_number, JSID=request.json['body_location'].upper()).first()
			p = DBPatient.query.filter_by(medical_record_number=medical_record_number).first()
			if p and p.deleted == False and location:
				if 'stopped' in sensor: location.stopped = sensor.get('stopped')
				if 'force_state' in sensor: location.force_state = sensor.get('force_state')
				if 'type' in sensor: location.type = sensor.get('type')
				if 'distance' in sensor: location.distance = sensor.get('distance')
				if 'fast_blink' in sensor: location.fast_blink = sensor.get('fast_blink')
				if 'alarm_clear_multiple' in sensor: location.alarm_clear_multiple = sensor.get('alarm_clear_multiple')
				if 'alarm_threshold_minutes' in sensor: location.alarm_threshold_minutes = sensor.get('alarm_threshold_minutes')
				if 'battery' in sensor: location.battery = sensor.get('battery')
				if 'binary_state' in sensor: location.binary_state = sensor.get('binary_state')
				if 'under_pressure_milliseconds' in sensor: location.under_pressure_milliseconds = sensor.get('under_pressure_milliseconds')
				if 'pressure_state' in sensor: location.pressure_state = sensor.get('pressure_state')
				if 'has_previous_alert' in sensor: location.has_previous_alert = sensor.get('has_previous_alert')
				if 'site_assessment' in sensor: location.site_assessment = sensor.get('site_assessment')
				if 'sensor_removal' in sensor: location.sensor_removal = sensor.get('sensor_removal')
				if 'wound_alarm_threshold_minutes' in sensor: location.wound_alarm_threshold_minutes = sensor.get('wound_alarm_threshold_minutes')
				if 'wound_alarm_clear_multiple' in sensor: location.wound_alarm_clear_multiple = sensor.get('wound_alarm_clear_multiple')
				if 'previous_alarm_threshold_hours' in sensor: location.previous_alarm_threshold_hours = sensor.get('previous_alarm_threshold_hours')

				new_wound = False
				is_wound = sensor.get('is_wound', False)
				if is_wound:
					if location.is_wound == None or location.is_wound == False:
						new_wound = True
					location.is_wound = is_wound
				else:
					location.is_wound = False

				if 'wound_stage' in sensor: location.wound_stage = sensor.get('wound_stage')
				if 'wound_measurement' in sensor: location.wound_measurement = sensor.get('wound_measurement')
				if 'wound_outcome' in sensor: location.wound_outcome = sensor.get('wound_outcome')
				if 'wound_acquisition' in sensor: location.wound_acquisition = sensor.get('wound_acquisition')
				location.existing_wound = sensor.get('existing_wound', False)
				if sensor.get('wound_existing_since'):
					location.wound_existing_since = sensor.get('wound_existing_since')
				elif new_wound:
					location.wound_existing_since = datetime.now().isoformat()
				elif not new_wound:
					location.wound_existing_since = sensor.get('wound_existing_since')

				location_dict = dict(vars(location))
				location_dict['body_location_id'] = location.id
				location_dict['user'] = user
				location_dict['date_of_record'] = utcformysqlfromtimestamp(nowtimestamp())
				location_dict.pop('id', None)
				location_dict.pop('patient_id', None)
				location_dict.pop('deleted', None)
				location_dict.pop('_sa_instance_state', None)

				location_history = DBBodyLocationHistory(**location_dict)
				db.session.add(location_history)

				device = DBDevice.query.filter_by(medical_record_number=medical_record_number).first()
				if device:
					device.last_web_change = utcformysqlfromtimestamp(nowtimestamp())
			db.session.commit()
			status_code = status.HTTP_204_NO_CONTENT
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code
