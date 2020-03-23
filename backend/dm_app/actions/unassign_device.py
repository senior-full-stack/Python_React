from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp
import copy

class UnassignDevice(Resource):
	@swagger.operation(
	notes='none',
	nickname='unassign device from patient',
	parameters=[
		{
			"name": "serial",
			"description": "device serial",
			"required": True,
			"dataType": "string",
			"paramType": "path"
		}
	  ],
	responseMessages=[
		{
			"code": 204,
			"message": "device unassigned from patient"
		},
		{
			"code": 400,
			"message": "bad request or device already unassigned"
		},
		{
			"code": 404,
			"message": "patient or device not found"
		}
	  ]
	)
	@validate_jwt_user_token
	def put(self, user=None, sub=None, role=None, serial=None):
		#link patient with device
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			#patient = DBPatient.query.filter_by(medical_record_number=medical_record_number).first()
			device = DBDevice.query.filter_by(serial=serial).first()
			if device:
				if not device.patient_id:
					status_code = status.HTTP_400_BAD_REQUEST
					response = {'error' : 'device not assigned'}
				else:
					device.patient_id = None
					device.medical_record_number = None
					device.last_web_change = utcformysqlfromtimestamp(nowtimestamp())
					db.session.commit()
					status_code = status.HTTP_204_NO_CONTENT

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, None, status_code, user=user, device=None)
		return response, status_code
