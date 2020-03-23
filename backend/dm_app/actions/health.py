from dm_app import *
from ..models import *

class Health(Resource):
	def get(self):
		response = None
		status_code = status.HTTP_503_SERVICE_UNAVAILABLE
		default = DBAdminDefault.query.first()
		if default:
			response = 'ok'
			status_code = status.HTTP_200_OK
		return response, status_code