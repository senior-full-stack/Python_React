from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled, hash_pass
from ..globs import *
import copy

class ChangePassword(Resource):
	@swagger.operation(
	notes='none',
	nickname='change password',
	parameters=[
		{
			"name": "email",
			"description": "to select user",
			"required": True,
			"dataType": "string",
			"paramType": "path"
		},
		{
			"name": "old_password",
			"description": "user's current password",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "new_password",
			"description": "desired new password",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		}
	  ],
	responseMessages=[
		{
			"code": 204,
			"message": "password changed"
		},
		{
			"code": 403,
			"message": "forbidden, old password isn't correct or user is trying to change other user"
		},
		{
			"code": 404,
			"message": "user not found"
		}
	  ]
	)
	@validate_jwt_user_token
	def put(self, user=None, sub=None, medical_record_number=None, location=None, role=None, email=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			data = copy.deepcopy(request.json)
			if email and data.get('old_password') and data.get('new_password'):
				if email != user and role == CAREGIVER:
					status_code = status.HTTP_403_FORBIDDEN
					response = {'error': "You are trying to change another user's password"}
				else:
					change_user = DBUser.query.filter_by(email=email).first()
					if change_user and change_user.deleted == False:
						if hash_pass(data.get('old_password')) == change_user.password:
							change_user.password = hash_pass(data.get('new_password'))
							db.session.commit()
							status_code = status.HTTP_204_NO_CONTENT
						else:
							status_code = status.HTTP_403_FORBIDDEN
							response = {'error': "Incorrect password"}

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code
