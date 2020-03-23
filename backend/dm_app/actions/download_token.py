from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled, SECRET
from ..globs import *
import copy
import hashlib, hmac

class DownloadToken(Resource):
	@validate_jwt_user_token
	@swagger.operation(
		notes='send back jwt token with short expiration to use to download report',
		nickname='get token',
		parameters=[
		  ],
		responseMessages=[
			{
				"code": 200,
				"message": "The token, user's email, and expiration time"
			},
			{
				"code": 400,
				"message": "bad request"
			},
			{
				"code": 401,
				"message": "not authorized"
			}
		  ]
		)
	def get(self, user=None, sub=None, role=None, serial=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			expiration = int(time.time()) + 10
			token = hmac.new(SECRET, user + '_' + str(expiration), hashlib.sha256).hexdigest()
			response = {'email': user, 'expiration': expiration, 'token': token}
			status_code = status.HTTP_200_OK

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST
		return response, status_code
