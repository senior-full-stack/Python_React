from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp
import copy

class Outcome(Resource):
	@validate_jwt_user_token
	@swagger.operation(
		notes='none',
		responseClass=DBPatient.__name__,
		nickname='get outcome',
		parameters=[
			{
				"name": "medical_record_number",
				"description": "to identify the patient whose outcome information to get",
				"required": True,
				"dataType": "string",
				"paramType": "url param"
			}
		  ],
		responseMessages=[
			{
				"code": 200,
				"message": "Outcome information for the patient"
			},
			{
				"code": 400,
				"message": "Bad request"
			},
			{
				"code": 404,
				"message": "No patients found"
			}
		  ]
		)
	def get(self, user=None, sub=None, medical_record_number=None, role=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			if medical_record_number:
				patient = DBPatient.query.filter_by(pa_id=medical_record_number).first()
				if patient and patient.deleted == False:
					wounds = DBBodyLocation.query.filter(DBBodyLocation.medical_record_number==medical_record_number, 
						DBBodyLocation.is_wound==True).all()

					activations = DBPatientActivation.query.filter_by(patient_id=patient.id).order_by(DBPatientActivation.id.desc()).all()
					response = {}

					patient.diagnosis = None
					patient.past_diagnosis = None
					patient.medication = None
					response['patient'] = PatientJsonSerializer().serialize(patient)

					response['pressure_injuries'] = []
					if wounds:
						for wound in wounds:
							response['pressure_injuries'].append(PUStatusReportJsonSerializer().serialize(wound))

					response['activations'] = []
					if activations:
						for activation in activations:
							response['activations'].append(PatientActivationJsonSerializer().serialize(activation))

					#TODO FIX
					activation = DBPatientActivation.query.filter_by(patient_id=patient.id).order_by(DBPatientActivation.id.desc()).first()

					if activation:
						response['activation_status'] = activation.status
					else:
						response['activation_status'] = INACTIVATED_STATUS

					status_code = status.HTTP_200_OK
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)
		return response, status_code
