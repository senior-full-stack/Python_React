from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp
import copy

class PatientAssignDevice(Resource):
	@swagger.operation(
	notes='none',
	nickname='assign device to patient',
	parameters=[
		{
			"name": "medical_record_number",
			"description": "patient identifier",
			"required": True,
			"dataType": "string",
			"paramType": "path"
		},
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
			"message": "device assigned to patient"
		},
		{
			"code": 400,
			"message": "bad request or device already assigned"
		},
		{
			"code": 404,
			"message": "patient or device not found"
		}
	  ]
	)
	@validate_jwt_user_token
	def put(self, medical_record_number=None, user=None, sub=None, role=None, serial=None):
		#link patient with device
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			data = request.path.split("/")
			patient = DBPatient.query.filter_by(pa_id=data[2]).first()
			device = DBDevice.query.filter_by(serial=data[4]).first()
			if patient and device and patient.deleted == False and device.deleted == False:
				if patient.device:
					status_code = status.HTTP_400_BAD_REQUEST
					response = {'error' : 'patient' + str(patient.id) + 'is already assigned'}
				else:
					device.patient_id = patient.id
					device.medical_record_number = patient.medical_record_number
					device.last_web_change = utcformysqlfromtimestamp(nowtimestamp())
					db.session.commit()
					status_code = status.HTTP_204_NO_CONTENT
					response = "patient id: " + str(patient.id)

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

#		log(request.remote_addr, request.path, request.method, None, status_code, user=user, device=None)
		return response, status_code
