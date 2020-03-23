from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp
import copy

class Device(Resource):
	@swagger.operation(
		notes='none',
		responseClass=DBDevice.__name__,
		nickname='delete device',
		parameters=[
			{
				"name": "serial",
				"description": "to select device to be deleted",
				"required": True,
				"dataType": "string",
				"paramType": "path"
			}
		  ],
		responseMessages=[
			{
				"code": 204,
				"message": "device deleted"
			},
			{
				"code": 404,
				"message": "No device found"
			}
		  ]
		)
	@validate_jwt_user_token
	def delete(self, user=None, sub=None, medical_record_number=None, serial=None, role=None):
		status_code = status.HTTP_404_NOT_FOUND
		response = None
		if serial:
			device = DBDevice.query.filter_by(serial=serial).first()
			if device:
				device.patient_id = None
				device.medical_record_number = None
				device.deleted = True
				device.serial = device.serial + 'deleted' + str(uuid.uuid4())
#				device.secret = device.secret + 'deleted' + str(uuid.uuid4())
				db.session.commit()

				status_code = status.HTTP_204_NO_CONTENT

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)
		return response, status_code

	@swagger.operation(
		notes='none',
		nickname='create device',
		parameters=[
			{
				"name": "serial",
				"description": "unique device serial number",
				"required": True,
				"dataType": "string",
				"paramType": "body"
			}
		  ],
		responseMessages=[
			{
				"code": 204,
				"message": "Device successfully created"
			},
			{
				"code": 200,
				"message": "Device already exists, based on serial provided"
			},
			{
				"code": 404,
				"message": "Bad request"
			}
		  ]
		)
	@validate_jwt_user_token
	def post(self, user=None, sub=None, serial=None):
		#register device in system
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			data = copy.deepcopy(request.json)
			device = DBDevice.query.filter_by(serial=data['serial']).first()
			settings = DBGlobalDeviceSettings.query.first()
			if device:
				if device.deleted == True:
					device.deleted = False
					device.last_seen = utcformysqlfromtimestamp(nowtimestamp())
					device.alarm_duration = settings.alarm_duration
					device.alarm_sound = settings.alarm_sound
					device.alarm_volume = settings.alarm_volume
					device.language = settings.language
					#device.secret = data['secret']
					device.name = data['serial']
					device.serial = data['serial']
					db.session.commit()
					status_code = status.HTTP_204_NO_CONTENT
				else:
					patient = DBPatient.query.filter_by(id=device.patient_id).first()
					status_code = status.HTTP_200_OK
					if patient:
						response = {"patient_id" : str(patient.pa_id)}
					else:
						response = {"patient_id":UNASSIGNED_DEVICE_ERROR}
			else:
#				data['secret'] = "HELLO"
				data['last_seen'] = utcformysqlfromtimestamp(nowtimestamp())
				data['alarm_duration'] = settings.alarm_duration
				data['alarm_sound'] = settings.alarm_sound
				data['alarm_volume'] = settings.alarm_volume
				data['language'] = settings.language
				data['name'] = data['serial']
				data['deleted'] = False
				device = DBDevice(**data)

				db.session.add(device)
				db.session.commit()

				status_code = status.HTTP_200_OK
				response = {"patient_id":UNASSIGNED_DEVICE_ERROR}

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=None, device=UNKNOWN)
		return response, status_code

	@swagger.operation(
		notes='none',
		nickname='update device',
		parameters=[
			{
				"name": "serial",
				"description": "unique device serial number to select device to modify",
				"required": True,
				"dataType": "string",
				"paramType": "path"
			},
			{
				"name": "name",
				"description": "name",
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
			},
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
			}
		  ],
		responseMessages=[
			{
				"code": 204,
				"message": "Device successfully created"
			},
			{
				"code": 200,
				"message": "Device already exists, based on serial provided"
			},
			{
				"code": 404,
				"message": "Not found"
			},
			{
				"code": 400,
				"message": "Bad request"
			}
		  ]
		)
	@validate_jwt_user_token
	def put(self, user=None, sub=None, serial=None, role=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			data = copy.deepcopy(request.json)
			device = DBDevice.query.filter_by(serial=serial).first()
			if device:
				if data.get('alarm_duration'): device.alarm_duration = data['alarm_duration']
				if data.get('alarm_sound'): device.alarm_sound = data['alarm_sound']
				if data.get('alarm_volume'): device.alarm_volume = data['alarm_volume']
				if data.get('language'): device.language = data['language']
				if data.get('name'): device.name = data['name']
				device.last_web_change = utcformysqlfromtimestamp(nowtimestamp())
				db.session.commit()

				status_code = status.HTTP_204_NO_CONTENT

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code

	@validate_jwt_user_token
	@swagger.operation(
		notes='none',
		responseClass=DBDevice.__name__,
		nickname='get devices',
		parameters=[
			{
				"name": "unassigned",
				"description": "flag to return only devices unassigned to patients",
				"required": False,
				"dataType": "boolean",
				"paramType": "url param"
			},
			{
				"name": "serial",
				"description": "device serial to return single device",
				"required": False,
				"dataType": "string",
				"paramType": "path"
			},
			{
				"name": "show_all",
				"description": "send 'True' to include all devices, including those who have been deleted",
				"required": False,
				"dataType": "boolean",
				"paramType": "url param"
			}
		  ],
		responseMessages=[
			{
				"code": 200,
				"message": "An array of devices, sorted last seen date, or single device"
			},
			{
				"code": 404,
				"message": "No devices found"
			}
		  ]
		)
	def get(self, user=None, sub=None, role=None, serial=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		device = None
		if request.args.get('unassigned'):
			devices = DBDevice.query.filter_by(patient_id=None, deleted=False).all()
			response = []
			for device in devices:
				response.append(DeviceJsonSerializer().serialize(device))
			response = {'devices' : response}
			status_code = status.HTTP_200_OK
		elif serial:
			device = DBDevice.query.filter_by(serial=serial, deleted=False).first()
			if device:
				response = DeviceJsonSerializer().serialize(device)
				status_code = status.HTTP_200_OK
		else:
			if request.args.get('show_all'):
				devices = DBDevice.query.order_by(DBDevice.last_seen).all()
			else:
				devices = DBDevice.query.filter_by(
					deleted=False
				).filter(
					DBDevice.last_seen >= (datetime.now() - timedelta(days=365))
				).order_by(DBDevice.last_seen.desc()).all()
			response = []
			for device in devices:
				device_json = DeviceJsonSerializer().serialize(device)
				if device.patient_id:
					patient = DBPatient.query.filter_by(id=device.patient_id).first()
					device_json['patient_name'] = patient.name
					device_json['patient_last_name'] = patient.last_name
				response.append(device_json)
			response = {'devices' : response}
			status_code = status.HTTP_200_OK
		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)
		return response, status_code
