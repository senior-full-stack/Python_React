from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
import copy

class DefaultSync(Resource):
	@swagger.operation(
	notes='none',
	responseClass=DBGlobalDeviceSettings.__name__,
	nickname='get default sync',
	responseMessages=[
		{
			"code": 200,
			"message": "default sync"
		},
		{
			"code": 503,
			"message": "service unavailable"
		}
	  ]
	)
	@validate_jwt_user_token
	def get(self, device_id=None, patient_id=None, medical_record_number=None, device_serial=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			device_settings = DBGlobalDeviceSettings.query.first()
			locations = []
			for JSID in BODY_LOCATIONS:
				location = DBGlobalLocationSettings.query.filter_by(JSID=JSID).first()
				locations.append(location.as_dict())
			glob = {}
			glob['language'] = device_settings.language
			glob['alarm_volume'] = device_settings.alarm_volume
			glob['alarm_sound'] = device_settings.alarm_sound
			glob['alarm_duration'] = device_settings.alarm_duration
			response = { 'sensors' : locations, 'globals' : glob}
			status_code = status.HTTP_200_OK

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_503_SERVICE_UNAVAILABLE

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=None, device=device_serial, 
			device_header=request.headers.get(DEVICE_ID_HEADER), version_header=request.headers.get(ANDROID_VERSION_HEADER))
		return response, status_code
