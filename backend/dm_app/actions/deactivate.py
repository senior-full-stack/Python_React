from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, strtotimestamp, nowtimestamp
import copy

class Deactivate(Resource):
	@validate_jwt_user_token
	@swagger.operation(
	notes='none',
	nickname='deactivate patient',
	parameters=[
		{
			"name": "medical_record_number",
			"description": "patient's unique identifier",
			"required": True,
			"dataType": "string",
			"paramType": "url param"
		},
		{
			"name": "status",
			"description": "Inactivated in this case",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "occurred",
			"description": "time patient was deactivated",
			"required": True,
			"dataType": "datetime",
			"paramType": "body"
		},
		{
			"name": "reason",
			"description": "reason for deactivation",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "sensors_collected",
			"description": "were the sensors collected",
			"required": False,
			"dataType": "bool",
			"paramType": "body"
		},
		{
			"name": "sensors_not_collected_reason",
			"description": "reason if sensors not collected",
			"required": False,
			"dataType": "string",
			"paramType": "body"
		}
	  ],
	responseMessages=[
		{
			"code": 204,
			"message": "Deactivation record created"
		},
		{
			"code": 400,
			"message": "Bad request"
		}
	  ]
	)
	def post(self, user=None, sub=None, medical_record_number=None, role=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			data = copy.deepcopy(request.json)
			if medical_record_number:
				patient = DBPatient.query.filter_by(pa_id=medical_record_number).first()
				if patient and patient.deleted == False:
					sensors_not_collected_reason = data.get('sensors_not_collected_reason', None)
					reason_other = data.get('reason_other', None)
					activation = DBPatientActivation.query.filter_by(patient_id=patient.id, status=INACTIVATED_STATUS, 
						occurred=utcformysqlfromtimestamp(strtotimestamp(data['occurred']))).first()
					if not activation:
						activation = DBPatientActivation(patient.id, INACTIVATED_STATUS, utcformysqlfromtimestamp(strtotimestamp(data['occurred'])), data['reason'], 
							utcformysqlfromtimestamp(nowtimestamp()), data['sensors_collected'], sensors_not_collected_reason, reason_other)
						db.session.add(activation)

						device = DBDevice.query.filter_by(medical_record_number=medical_record_number).first()
						if device:
							device.patient_id = None
							device.medical_record_number = None

						db.session.commit()
						status_code = status.HTTP_204_NO_CONTENT
					else:
						status_code = status.HTTP_200_OK
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code
