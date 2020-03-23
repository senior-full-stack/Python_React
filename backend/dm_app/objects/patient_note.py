from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp, strtotimestamp
import copy

class PatientNote(Resource):
	@swagger.operation(
		notes='none',
		responseClass=DBPatientNote.__name__,
		nickname='get patient notes',
		parameters=[
			{
				"name": "pa_id",
				"description": "patient identifier",
				"required": True,
				"dataType": "string",
				"paramType": "url param"
			},
			{
				"name": "patient_site",
				"description": "location",
				"required": False,
				"dataType": "string",
				"paramType": "url param"
			}
		  ],
		responseMessages=[
			{
				"code": 200,
				"message": "An array of patient notes, sorted by occurred date"
			},
			{
				"code": 404,
				"message": "No notes found"
			}
		  ]
		)
	@validate_jwt_user_token
	def get(self, user=None, sub=None, pa_id=None, role=None, patient_site=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			if patient_site:
				assessments = DBPatientNote.query.filter_by(pa_id=pa_id, patient_site=patient_site).order_by(
					DBPatientNote.occurred.desc()).all()
			else:
				assessments = DBPatientNote.query.filter_by(pa_id=pa_id).order_by(
					DBPatientNote.occurred.desc()).all()
			if assessments:
				response = []
				for assessment in assessments:
					response.append(PatientNoteJsonSerializer().serialize(assessment))

				status_code = status.HTTP_200_OK

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)
		return response, status_code


	@validate_jwt_user_token
	@swagger.operation(
	notes='none',
	nickname='create patient note',
	parameters=[
		{
			"name": "pa_id",
			"description": "patient identifier",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "patient_site",
			"description": "location",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "occurred",
			"description": "note time",
			"required": True,
			"dataType": "datetime",
			"paramType": "body"
		},
		{
			"name": "dressing_application_surface",
			"description": "dressing application surface",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "device_surrounding_dressing",
			"description": "device surrounding dressing",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "reason_for_dressing_change",
			"description": "reason for dressing change",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "reason_for_dressing_removal",
			"description": "reason for dressing removal",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "tablet_issues",
			"description": "tablet issues",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "sensor_issues",
			"description": "sensor issues",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "support_contacted",
			"description": "support contacted",
			"required": True,
			"dataType": "boolean",
			"paramType": "body"
		},
		{
			"name": "comments",
			"description": "comments",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "support_reason",
			"description": "support reason",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "patient_site_other",
			"description": "patient site other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "dressing_application_surface_other",
			"description": "dressing application surface other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "device_surrounding_dressing_other",
			"description": "device surrounding dressing other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "reason_for_dressing_change_other",
			"description": "reason for dressing change other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "reason_for_dressing_removal_other",
			"description": "reason for dressing removal other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "tablet_issues_other",
			"description": "tablet issues other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "sensor_issues_other",
			"description": "sensor issues other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		}
	  ],
	responseMessages=[
		{
			"code": 204,
			"message": "Site assessment record created"
		},
		{
			"code": 400,
			"message": "Bad request"
		}
	  ]
	)
	def post(self, user=None, sub=None, role=None):
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			data = copy.deepcopy(request.json)
			if data:
				note_json = {}
				note_json['pa_id'] = data['pa_id']
				note_json['patient_site'] = data['patient_site']
				note_json['dressing_application_surface'] = data['dressing_application_surface']
				note_json['device_surrounding_dressing'] = data['device_surrounding_dressing']
				note_json['reason_for_dressing_change'] = data['reason_for_dressing_change']
				note_json['reason_for_dressing_removal'] = data['reason_for_dressing_removal']
				note_json['tablet_issues'] = data['tablet_issues']
				note_json['sensor_issues'] = data['sensor_issues']
				note_json['support_contacted'] = data['support_contacted']
				note_json['occurred'] = utcformysqlfromtimestamp(strtotimestamp(data['occurred']))
				if 'comments' in data:
					note_json['comments'] = data['comments']
				if 'support_reason' in data:
					note_json['support_reason'] = data['support_reason']
				if 'patient_site_other' in data:
					note_json['patient_site_other'] = data['patient_site_other']
				if 'dressing_application_surface_other' in data:
					note_json['dressing_application_surface_other'] = data['dressing_application_surface_other']
				if 'device_surrounding_dressing_other' in data:
					note_json['device_surrounding_dressing_other'] = data['device_surrounding_dressing_other']
				if 'reason_for_dressing_change_other' in data:
					note_json['reason_for_dressing_change_other'] = data['reason_for_dressing_change_other']
				if 'reason_for_dressing_removal_other' in data:
					note_json['reason_for_dressing_removal_other'] = data['reason_for_dressing_removal_other']
				if 'tablet_issues_other' in data:
					note_json['tablet_issues_other'] = data['tablet_issues_other']
				if 'sensor_issues_other' in data:
					note_json['sensor_issues_other'] = data['sensor_issues_other']

				note_json['user'] = user
				note = DBPatientNote(**note_json)
				db.session.add(note)

				db.session.commit()
				status_code = status.HTTP_204_NO_CONTENT
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code


	@validate_jwt_user_token
	@swagger.operation(
	notes='none',
	nickname='update site assessment',
	parameters=[
		{
			"name": "pa_id",
			"description": "patient identifier",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "patient_site",
			"description": "location",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "occurred",
			"description": "note time",
			"required": True,
			"dataType": "datetime",
			"paramType": "body"
		},
		{
			"name": "dressing_application_surface",
			"description": "dressing application surface",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "device_surrounding_dressing",
			"description": "device surrounding dressing",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "reason_for_dressing_change",
			"description": "reason for dressing change",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "reason_for_dressing_removal",
			"description": "reason for dressing removal",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "tablet_issues",
			"description": "tablet issues",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "sensor_issues",
			"description": "sensor issues",
			"required": True,
			"dataType": "string",
			"paramType": "body"
		},
		{
			"name": "support_contacted",
			"description": "support contacted",
			"required": True,
			"dataType": "boolean",
			"paramType": "body"
		},
		{
			"name": "comments",
			"description": "comments",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "support_reason",
			"description": "support reason",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "patient_site_other",
			"description": "patient site other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "dressing_application_surface_other",
			"description": "dressing application surface other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "device_surrounding_dressing_other",
			"description": "device surrounding dressing other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "reason_for_dressing_change_other",
			"description": "reason for dressing change other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "reason_for_dressing_removal_other",
			"description": "reason for dressing removal other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "tablet_issues_other",
			"description": "tablet issues other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		},
		{
			"name": "sensor_issues_other",
			"description": "sensor issues other",
			"required": False,
			"dataType": "Text",
			"paramType": "body"
		}
	  ],
	responseMessages=[
		{
			"code": 204,
			"message": "Patient note updated"
		},
		{
			"code": 400,
			"message": "Bad request"
		},
		{
			"code": 404,
			"message": "Note not found"
		}
	  ]
	)
	def put(self, user=None, sub=None, medical_record_number=None, role=None, body_location_id=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			data = copy.deepcopy(request.json)
			if data and 'id' in data:
				note = DBPatientNote.query.filter_by(id=data['id']).first()
				if note:
					note.patient_site = data['patient_site']
					note.dressing_application_surface = data['dressing_application_surface']
					note.device_surrounding_dressing = data['device_surrounding_dressing']
					note.reason_for_dressing_change = data['reason_for_dressing_change']
					note.reason_for_dressing_removal = data['reason_for_dressing_removal']
					note.tablet_issues = data['tablet_issues']
					note.sensor_issues = data['sensor_issues']
					note.support_contacted = data['support_contacted']
					note.occurred = utcformysqlfromtimestamp(strtotimestamp(data['occurred']))

					if 'comments' in data:
						note.comments = data['comments']
					if 'support_reason' in data:
						note.support_reason = data['support_reason']
					if 'patient_site_other' in data:
						note.patient_site_other = data['patient_site_other']
					if 'dressing_application_surface_other' in data:
						note.dressing_application_surface_other = data['dressing_application_surface_other']
					if 'device_surrounding_dressing_other' in data:
						note.device_surrounding_dressing_other = data['device_surrounding_dressing_other']
					if 'reason_for_dressing_change_other' in data:
						note.reason_for_dressing_change_other = data['reason_for_dressing_change_other']
					if 'reason_for_dressing_removal_other' in data:
						note.reason_for_dressing_removal_other = data['reason_for_dressing_removal_other']
					if 'tablet_issues_other' in data:
						note.tablet_issues_other = data['tablet_issues_other']
					if 'sensor_issues_other' in data:
						note.sensor_issues_other = data['sensor_issues_other']

					note.user = user

					db.session.commit()
					status_code = status.HTTP_204_NO_CONTENT
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code
