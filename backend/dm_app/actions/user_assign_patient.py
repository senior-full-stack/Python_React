from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp
import copy

class UserAssignPatient(Resource):
	@swagger.operation(
	notes='none',
	nickname='assign patient to user',
	parameters=[
		{
			"name": "medical_record_number",
			"description": "patient identifier",
			"required": True,
			"dataType": "string",
			"paramType": "path"
		},
		{
			"name": "email",
			"description": "user identifier",
			"required": True,
			"dataType": "string",
			"paramType": "path"
		}
	  ],
	responseMessages=[
		{
			"code": 204,
			"message": "patient assigned to user"
		},
		{
			"code": 400,
			"message": "bad request or device already assigned"
		},
		{
			"code": 404,
			"message": "patient or user not found"
		}
	  ]
	)
	@validate_jwt_user_token
	def put(self, user=None, sub=None, medical_record_number=None, role=None, email=None):
		#link patient with device
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			patient = DBPatient.query.filter_by(medical_record_number=medical_record_number).first()
			assign_user = DBUser.query.filter_by(email=email).first()
			if patient and assign_user:
				assign_user.patients.append(patient)
				db.session.commit()
				status_code = status.HTTP_204_NO_CONTENT
				assign_user = DBUser.query.filter_by(email=email).first()

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, None, status_code, user=user, device=None)
		return response, status_code
