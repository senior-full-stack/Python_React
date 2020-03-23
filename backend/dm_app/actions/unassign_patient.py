from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp
import copy

class UnassignPatient(Resource):
	@swagger.operation(
	notes='none',
	nickname='unassign device from patient',
	parameters=[
		{
			"name": "medical_record_number",
			"description": "patient identifier",
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
			"message": "bad request or patient already unassigned"
		},
		{
			"code": 404,
			"message": "patient or device not found"
		}
	  ]
	)
	@validate_jwt_user_token
	def put(self, user=None, sub=None, role=None, medical_record_number=None):
		#link patient with device
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			patient = DBPatient.query.filter_by(pa_id=medical_record_number).first()
			device = DBDevice.query.filter_by(medical_record_number=medical_record_number).first()
			if patient:
				if not patient.device or not device:
					status_code = status.HTTP_400_BAD_REQUEST
					response = {'error' : 'patient not assigned'}
				else:
					device.patient_id = None
					device.medical_record_number = None
					db.session.commit()
					status_code = status.HTTP_204_NO_CONTENT

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, None, status_code, user=user, device=None)
		return response, status_code
