from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp
import copy

class TimeLine(Resource):
	@validate_jwt_user_token
	@swagger.operation(
		notes='none',
		responseClass=DBEvent.__name__,
		nickname='get timeline events',
		parameters=[
			{
				"name": "medical_record_number",
				"description": "a patient's medical record number to filter timeline events",
				"required": True,
				"dataType": "string",
				"paramType": "url arg"
			}
		  ],
		responseMessages=[
			{
				"code": 200,
				"message": "An array of events"
			},
			{
				"code": 404,
				"message": "No events found"
			}
		  ]
		)
	def get(self, user=None, sub=None, event=None, role=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			if request.args.get('medical_record_number'):
				result = DBEvent.query.filter_by(medical_record_number=request.args.get('medical_record_number')).all()
				response = []
				for item in result:
					response.append(EventJsonSerializer().serialize(item))
			if response:
				p = DBPatient.query.filter_by(medical_record_number=request.args.get('medical_record_number')).first()
				response = {'events' : response }
				response['name'] = p.name
				status_code = status.HTTP_200_OK
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)
		return response, status_code
