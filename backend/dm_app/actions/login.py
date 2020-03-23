from dm_app import *
from ..models import *
from ..utils import log, profiled, hash_pass, SECRET
from ..globs import *
from ..rfc3339 import nowtimestamp
import copy
import jwt

class Login(Resource):
	def post(self):
		creds = request.json
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			user = self.authenticate(creds)
			if user:
				response = self.create_jwt_token(creds)
				status_code = status.HTTP_200_OK
			else:
				response = {'error' : 'authentication failed'}
				status_code = status.HTTP_401_UNAUTHORIZED
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=UNKNOWN, device=None)

		return response, status_code


	def authenticate(self, credentials):
		#returns user to reduce database calls
		result = None
                #if 'device_id' not in credentials:
                #        return result
                if 'email' in credentials and 'password' in credentials:
                        user = DBUser.query.filter_by(email=credentials['email']).first()
                        if user and hash_pass(credentials['password']) == user.password:
                                result = user
                return result

        def create_jwt_token(self, creds):
                token = jwt.encode({'org':'TEST', 'user': creds['email'],  'sub' :creds['serial'], 'iat': nowtimestamp()}, # 'sub' :creds['device_id']
                           SECRET,
                           algorithm='HS256')
                return {'token' : token}

