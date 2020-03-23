from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, validate_jwt_device_or_user_token, profiled
from ..globs import *
import copy


class GlobalDeviceSettings(Resource):
	@swagger.operation(
	notes='none',
	responseClass=DBGlobalDeviceSettings.__name__,
	nickname='get global device settings',
	responseMessages=[
		{
			"code": 200,
			"message": "global device settings"
		}
	  ]
	)
	@validate_jwt_device_or_user_token
	def get(self, user=None, sub=None, device_id=None, medical_record_number=None, patient_id=None, role=None, device_serial=None):
		settings = DBGlobalDeviceSettings.query.first()
		settings = settings.as_dict()
		if user:
			log(request.remote_addr, request.path, request.method, request.args, status.HTTP_200_OK, user=user, device=None)
		else:
			log(request.remote_addr, request.path, request.method, request.args, status.HTTP_200_OK, user=None, device=device_serial, 
			device_header=request.headers.get(DEVICE_ID_HEADER), version_header=request.headers.get(ANDROID_VERSION_HEADER))
		return settings, status.HTTP_200_OK

	@swagger.operation(
		notes='none',
		nickname='update global device settings',
		parameters=[
			{
				"name": "alarm_duration",
				"description": "alarm duration",
				"required": False,
				"dataType": "int",
				"paramType": "body"
			},
			{
				"name": "alarm_sound",
				"description": "alarm sound",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "alarm_volume",
				"description": "alarm volume",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "language",
				"description": "language",
				"required": False,
				"dataType": "string",
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
	def put(self, user=None, sub=None, role=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			data = copy.deepcopy(request.json)
			if data:
				settings = DBGlobalDeviceSettings.query.first()

				settings.alarm_duration = data['alarm_duration']
				settings.alarm_sound = data['alarm_sound']
				settings.alarm_volume = data['alarm_volume']
				settings.language = data['language']

				db.session.commit()

				status_code = status.HTTP_204_NO_CONTENT
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code
