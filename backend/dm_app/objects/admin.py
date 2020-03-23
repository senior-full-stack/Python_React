from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
import copy

class Admin(Resource):
	@swagger.operation(
	notes='none',
	responseClass=DBAdminDefault.__name__,
	nickname='get admin defaults',
	parameters=[
			{
				"name": "unit_floor",
				"description": "a string of possible unit/floor values",
				"required": True,
				"dataType": "string",
				"paramType": "url param"
			}
		  ],
	responseMessages=[
		{
			"code": 200,
			"message": "admin defaults returned"
		}
	  ]
	)
	@validate_jwt_user_token
	def get(self, user=None, sub=None, device_id=None, medical_record_number=None, patient_id=None, role=None, device_serial=None):
		defaults = DBAdminDefault.query.first()
		defaults = AdminDefaultJsonSerializer().serialize(defaults)

		log(request.remote_addr, request.path, request.method, request.args, status.HTTP_200_OK, user=user, device=None)
		return defaults, status.HTTP_200_OK

	@swagger.operation(
		notes='none',
		nickname='update admin defaults',
		parameters=[
			{
				"name": "unit_floor",
				"description": "unit floor",
				"required": True,
				"dataType": "json string",
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
			},
			{
				"code": 403,
				"message": "Forbidden, user not admin"
			}
		  ]
		)
	@validate_jwt_user_token
	def put(self, user=None, sub=None, role=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			data = copy.deepcopy(request.json)
			if role == ADMIN:
				if data:
					defaults = DBAdminDefault.query.first()

					defaults.unit_floor = data['unit_floor']

					db.session.commit()

					status_code = status.HTTP_204_NO_CONTENT
			else:
				status_code = status.HTTP_403_FORBIDDEN

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code
