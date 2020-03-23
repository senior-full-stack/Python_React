from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled, hash_pass
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp
import copy

class User(Resource):
	@swagger.operation(
		notes='none',
		responseClass=DBUser.__name__,
		nickname='delete user',
		parameters=[
			{
				"name": "email",
				"description": "user's identifier",
				"required": True,
				"dataType": "string",
				"paramType": "path"
			}
		  ],
		responseMessages=[
			{
				"code": 204,
				"message": "user deleted"
			},
			{
				"code": 403,
				"message": "user trying to delete not admin"
			},
			{
				"code": 404,
				"message": "User not found"
			}
		  ]
		)
	@validate_jwt_user_token
	def delete(self, user=None, sub=None, role=None, email=None):
		webuser = user
		status_code = status.HTTP_404_NOT_FOUND
		response = None
		if email and role == ADMIN:
			user = DBUser.query.filter_by(email=email).first()
			if user:
				user.deleted = True
				db.session.commit()
				status_code = status.HTTP_204_NO_CONTENT
		elif role == CAREGIVER:
			status_code = status.HTTP_403_FORBIDDEN

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=webuser, device=None)
		return response, status_code

	@validate_jwt_user_token
	@swagger.operation(
		notes='none',
		responseClass=DBUser.__name__,
		nickname='get users',
		parameters=[
			{
				"name": "email",
				"description": "user's unique identifier, all users returned if not present. if user unique identifer is 'current' then returns object of user making the request",
				"required": False,
				"dataType": "string",
				"paramType": "path"
			},
			{
				"name": "show_all",
				"description": "send 'True' to include all users, including those who have been deleted",
				"required": False,
				"dataType": "boolean",
				"paramType": "url param"
			}
		  ],
		responseMessages=[
			{
				"code": 200,
				"message": "An array of users"
			},
			{
				"code": 404,
				"message": "No users found"
			}
		  ]
		)
	def get(self, user=None, sub=None, role=None, email=None):
		webuser = user
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			if email:
				if email == "current":
					email = user
				user = DBUser.query.filter_by(email=email, deleted=False).first()
				if user:
					response = UserJsonSerializer().serialize(user)
					status_code = status.HTTP_200_OK
			else:
				if request.args.get('show_all'):
					users = DBUser.query.order_by(DBUser.email).all()
				else:
					users = DBUser.query.filter_by(deleted=False).order_by(DBUser.email).all()
				response = []
				for user in users:
					response.append(UserJsonSerializer().serialize(user))
				response = {'users' : response}
				status_code = status.HTTP_200_OK
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_404_NOT_FOUND
		log(request.remote_addr, request.path, request.method, request.args, status_code, user=webuser, device=None)
		return response, status_code

	@swagger.operation(
		notes='none',
		nickname='create user',
		parameters=[
			{
				"name": "email",
				"description": "user's unique identifier",
				"required": True,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "password",
				"description": "password",
				"required": True,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "name",
				"description": "name",
				"required": True,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "phone_number",
				"description": "phone number",
				"required": True,
				"dataType": "string",
				"paramType": "body"
			}
		  ],
		responseMessages=[
			{
				"code": 204,
				"message": "User successfully created"
			},
			{
				"code": 200,
				"message": "User already exists, based on email provided"
			},
			{
				"code": 400,
				"message": "Bad request"
			}
		  ]
		)
	@validate_jwt_user_token
	def post(self, user=None, sub=None, role=None, email=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			data = copy.deepcopy(request.json)
			if 'email' in data and data['email']:
				user = DBUser.query.filter_by(email=data['email']).first()
				if user:
					if user.deleted == True:
						user.deleted = False
						user.name = data['name']
						user.password = hash_pass(data['password'])
						user.phone_number = data['phone_number']
						user.eula_accepted = False
						user.email_notification = False
						if role == ADMIN and 'role' in data:
							user.role = data['role']
						else:
							user.role = CAREGIVER
						db.session.commit()
						status_code = status.HTTP_204_NO_CONTENT

					else:
						status_code = status.HTTP_200_OK
				else:
					email_notification = None
					if role == ADMIN:
						if 'role' in data:
							role_param = data['role']
						else:
							role_param = CAREGIVER
						if 'email_notification' in data:
							email_notification = data['email_notification']
						else:
							email_notification = False
						user = DBUser(data['name'], hash_pass(data['password']), data['email'], data['phone_number'], False, 
							role_param, email_notification=email_notification, deleted=False)
					else:
						user = DBUser(data['name'], hash_pass(data['password']), data['email'], data['phone_number'], False, 
							CAREGIVER, email_notification=email_notification, deleted=False)

					db.session.add(user)
					db.session.commit()
					status_code = status.HTTP_204_NO_CONTENT
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=UNKNOWN, device=None)
		return response, status_code

	@swagger.operation(
		notes='none',
		nickname='update user',
		parameters=[
			{
				"name": "email",
				"description": "email, user's uniqe identifier",
				"required": True,
				"dataType": "string",
				"paramType": "path or body"
			},
			{
				"name": "name",
				"description": "name",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "phone_number",
				"description": "phone number",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "eula_accepted",
				"description": "flag for eula",
				"required": False,
				"dataType": "boolean",
				"paramType": "body"
			},
			{
				"name": "password",
				"description": "can only be modified by an admin",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			}
		  ],
		responseMessages=[
			{
				"code": 204,
				"message": "User successfully updated"
			},
			{
				"code": 400,
				"message": "Bad request"
			},
			{
				"code": 403,
				"message": "Forbidden, non admin user trying to change other user's data"
			},
			{
				"code": 404,
				"message": "User not found"
			}
		  ]
		)
	@validate_jwt_user_token
	def put(self, user=None, sub=None, role=None, email=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			data = copy.deepcopy(request.json)
			if email:
				change_user = DBUser.query.filter_by(email=email).first()
			else:
				change_user = DBUser.query.filter_by(email=data['email']).first()
			if change_user:
				if role != ADMIN and user != change_user.email:
					status_code = status.HTTP_403_FORBIDDEN
					response = {'error': "You do not have permission to change another user"}
				elif role == ADMIN:
					if data.get('password'): change_user.password = hash_pass(data['password'])
					if data.get('role') and (data['role'] == CAREGIVER or data['role'] == ADMIN): change_user.role = data['role']
					if data.get('name'): change_user.name = data['name']
					if data.get('email'): change_user.email = data['email']
					if data.get('phone_number'): change_user.phone_number = data['phone_number']
					if data.get('eula_accepted'): change_user.eula_accepted = data['eula_accepted']
					if 'email_notification' in data: change_user.email_notification = data['email_notification']
					db.session.commit()
					status_code = status.HTTP_204_NO_CONTENT

					#log(request.remote_addr, request.path, request.method, data, status_code, user=user, device=None)
				else:
					if data.get('name'): change_user.name = data['name']
					if data.get('phone_number'): change_user.phone_number = data['phone_number']
					if data.get('eula_accepted'): change_user.eula_accepted = data['eula_accepted']
					if data.get('email'): change_user.email = data['email']
					log_user = UserJsonSerializer().serialize(change_user)
					db.session.commit()
					status_code = status.HTTP_204_NO_CONTENT

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST
		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code
