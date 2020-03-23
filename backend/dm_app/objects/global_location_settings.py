from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, validate_jwt_device_or_user_token, profiled
from ..globs import *
import copy

class GlobalLocationSettings(Resource):  
	@swagger.operation(
	notes='none',
	responseClass=DBGlobalLocationSettings.__name__,
	nickname='get global location settings',
	responseMessages=[
		{
			"code": 200,
			"message": "global device settings"
		}
	  ]
	)
	@validate_jwt_device_or_user_token
	def get(self, user=None, sub=None, device_id=None, medical_record_number=None, patient_id=None, location=None, role=None, device_serial=None):
		settings = DBGlobalLocationSettings.query.filter_by(JSID=location).first()
		settings = settings.as_dict()
		if user:
			log(request.remote_addr, request.path, request.method, request.args, status.HTTP_200_OK, user=user, device=None)
		else:
			log(request.remote_addr, request.path, request.method, request.args, status.HTTP_200_OK, user=None, device=device_serial, 
			device_header=request.headers.get(DEVICE_ID_HEADER), version_header=request.headers.get(ANDROID_VERSION_HEADER))
		return settings, status.HTTP_200_OK

	@swagger.operation(
		notes='none',
		nickname='update global location settings',
		parameters=[
			{
			  "name": "type",
			  "description": "sensor type",
			  "required": False,
			  "dataType": "int",
			  "paramType": "body"
			},
			{
			  "name": "alarm_clear_multiple",
			  "description": "alarm clear multiple",
			  "required": False,
			  "dataType": "int",
			  "paramType": "body"
			},
			{
			  "name": "alarm_threshold_minutes",
			  "description": "alarm threshold minutes",
			  "required": False,
			  "dataType": "int",
			  "paramType": "body"
			},
			{
			  "name": "pressure_state",
			  "description": "pressure state",
			  "required": False,
			  "dataType": "string",
			  "paramType": "body"
			},
			{
			  "name": "wound_stage",
			  "description": "wound stage",
			  "required": False,
			  "dataType": "string",
			  "paramType": "body"
			},
			{
			  "name": "is_wound",
			  "description": "is wound",
			  "required": False,
			  "dataType": "bool",
			  "paramType": "body"
			},
			{
			  "name": "has_previous_alert",
			  "description": "has previous alert",
			  "required": False,
			  "dataType": "bool",
			  "paramType": "body"
			},
			{
			  "name": "site_assessment",
			  "description": "site assessment",
			  "required": False,
			  "dataType": "string",
			  "paramType": "body"
			},
			{
			  "name": "sensor_removal",
			  "description": "sensor removal",
			  "required": False,
			  "dataType": "string",
			  "paramType": "body"
			},
			{
			  "name": "wound_measurement",
			  "description": "wound measurement",
			  "required": False,
			  "dataType": "string",
			  "paramType": "body"
			},
			{
			  "name": "existing_wound",
			  "description": "existing wound",
			  "required": False,
			  "dataType": "bool",
			  "paramType": "body"
			},
			{
			  "name": "wound_alarm_threshold_minutes",
			  "description": "wound alarm threshold minutes",
			  "required": False,
			  "dataType": "int",
			  "paramType": "body"
			},
			{
			  "name": "wound_alarm_clear_multiple",
			  "description": "wound alarm clear multiple",
			  "required": False,
			  "dataType": "int",
			  "paramType": "body"
			},
			{
			  "name": "previous_alarm_threshold_hours",
			  "description": "previous alarm threshold hours",
			  "required": False,
			  "dataType": "int",
			  "paramType": "body"
			}
		  ],
		responseMessages=[
			{
			  "code": 204,
			  "message": "settings updated"
			},
			{
			  "code": 400,
			  "message": "Bad request"
			}
		  ]
		)
	@validate_jwt_user_token
	def put(self, user=None, sub=None, location=None, role=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			data = copy.deepcopy(request.json)
			settings = DBGlobalLocationSettings.query.filter_by(JSID=location).first()
			if settings:
				#if data.get('type'): settings.type = data['type'] 
				if data.get('alarm_clear_multiple'): settings.alarm_clear_multiple = data['alarm_clear_multiple'] 
				if data.get('alarm_threshold_minutes'): settings.alarm_threshold_minutes = data['alarm_threshold_minutes'] 
				if data.get('pressure_state'): settings.pressure_state = data['pressure_state'] 
				if data.get('wound_stage'): settings.wound_stage = data['wound_stage'] 
				if data.get('is_wound'): settings.is_wound = data['is_wound'] 
				if data.get('has_previous_alert'): settings.has_previous_alert = data['has_previous_alert'] 
				if data.get('site_assessment'): settings.site_assessment = data['site_assessment'] 
				if data.get('sensor_removal'): settings.sensor_removal = data['sensor_removal'] 
				if data.get('wound_measurement'): settings.wound_measurement = data['wound_measurement'] 
				if data.get('existing_wound'): settings.existing_wound = data['existing_wound'] 
				if data.get('wound_alarm_threshold_minutes'): settings.wound_alarm_threshold_minutes = data['wound_alarm_threshold_minutes'] 
				if data.get('wound_alarm_clear_multiple'): settings.wound_alarm_clear_multiple = data['wound_alarm_clear_multiple'] 
				if data.get('previous_alarm_threshold_hours'): settings.previous_alarm_threshold_hours = data['previous_alarm_threshold_hours'] 

				db.session.commit()

				status_code = status.HTTP_204_NO_CONTENT
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code
