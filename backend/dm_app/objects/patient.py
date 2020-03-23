from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import utcformysqlfromtimestamp, nowtimestamp
from ..field_names import DIAGNOSIS_FIELD_NAMES, MEDICATION_FIELD_NAMES
import copy
from datetime import datetime

class Patient(Resource):
	@swagger.operation(
		notes='none',
		responseClass=DBDevice.__name__,
		nickname='delete patient',
		parameters=[
			{
				"name": "medical_record_number",
				"description": "to select patient to be deleted",
				"required": True,
				"dataType": "string",
				"paramType": "path"
			}
		  ],
		responseMessages=[
			{
				"code": 204,
				"message": "patient deleted"
			},
			{
				"code": 404,
				"message": "No patient found"
			}
		  ]
		)
	@validate_jwt_user_token
	def delete(self, user=None, sub=None, medical_record_number=None, role=None):
		status_code = status.HTTP_404_NOT_FOUND
		# status_code = status.HTTP_204_NO_CONTENT
		response = None
		if medical_record_number:
			patient = DBPatient.query.filter_by(pa_id=medical_record_number).first()
			if patient:
				device = DBDevice.query.filter_by(medical_record_number=medical_record_number).first()
				if device:
					device.patient_id = None
					device.medical_record_number = None
				patient.deleted = True
				deleted_string = 'deleted' + str(uuid.uuid4())
				patient.pa_id = patient.pa_id + deleted_string
				patient.medical_record_number = patient.medical_record_number + deleted_string

				activation = DBPatientActivation(patient.id, INACTIVATED_STATUS, utcformysqlfromtimestamp(nowtimestamp()), INACTIVATED_REASON_DELETED, 
							utcformysqlfromtimestamp(nowtimestamp()), False, INACTIVATED_REASON_DELETED, None)
				db.session.add(activation)
				db.session.commit()

				status_code = status.HTTP_204_NO_CONTENT

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)
		return response, status_code

	@validate_jwt_user_token
	@swagger.operation(
		notes='none',
		responseClass=DBPatient.__name__,
		nickname='get patients',
		parameters=[
			{
				"name": "unassigned",
				"description": "flag to return only patients without assigned devices",
				"required": False,
				"dataType": "boolean",
				"paramType": "url arg"
			},
			{
				"name": "medical_record_number",
				"description": "a patient's medical record number to filter by",
				"required": False,
				"dataType": "string",
				"paramType": "url param"
			},
			{
				"name": "show_all",
				"description": "send 'True' to include all patients, including those who have been deleted",
				"required": False,
				"dataType": "boolean",
				"paramType": "url arg"
			},
			{
				"name": "unit_floor",
				"description": "get patients by unit_floor",
				"required": False,
				"dataType": "string",
				"paramType": "url arg"
			}
		  ],
		responseMessages=[
			{
				"code": 200,
				"message": "An array of patients, sorted by medical record number"
			},
			{
				"code": 400,
				"message": "Bad request"
			},
			{
				"code": 404,
				"message": "No patient found"
			}
		  ]
		)
	def get(self, user=None, sub=None, medical_record_number=None, role=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			if medical_record_number:
				patient = DBPatient.query.filter_by(pa_id=medical_record_number, deleted=False).first()
				if patient:
					response = [self.serialize(patient) if sub.upper() == 'N/A' else self.serialize_for_mobile(patient)]
				response = {'patients' : response}
				status_code = status.HTTP_200_OK
			elif request.args.get('medical_record_number'):
				patient = DBPatient.query.filter_by(pa_id=request.args.get('medical_record_number'), deleted=False).first()
				if patient:
					response = [self.serialize(patient) if sub.upper() == 'N/A' else self.serialize_for_mobile(patient)]
                                response = {'patients' : response}
                                status_code = status.HTTP_200_OK
			elif request.args.get('unassigned'):
				patients = DBPatient.query.filter_by(device=None, deleted=False).all()
				response = []
				for patient in patients:
					result = self.serialize(patient) if sub.upper() == 'N/A' else self.serialize_for_mobile(patient)
					response.append(result)
				response = {'patients' : response}
				status_code = status.HTTP_200_OK
			elif request.args.get('unit_floor'):
				patients = DBPatient.query.filter_by(unit_floor=request.args.get('unit_floor'), deleted=False).all()
				response = []
				for patient in patients:
                                        result = self.serialize(patient) if sub.upper() == 'N/A' else self.serialize_for_mobile(patient)
                                        response.append(result)
				response = {'patients' : response}
				status_code = status.HTTP_200_OK
			else:
				if request.args.get('show_all'):
					patients = DBPatient.query.order_by(DBPatient.medical_record_number).order_by(DBPatient.name).all()
				else:
					patients = DBPatient.query.filter_by(deleted=False).order_by(DBPatient.name).all()
				response = []
				for patient in patients:
                                        result = self.serialize(patient) if sub.upper() == 'N/A' else self.serialize_for_mobile(patient)
                                        response.append(result)
				response = {'patients' : response}
				status_code = status.HTTP_200_OK

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)
		return response, status_code

	def serialize_for_mobile(self, patient):
		new_patient = {
				'pa_id': patient.pa_id,
				'name': patient.name,
				'last_name': patient.last_name,
				'gender': patient.gender,
				'DOB': str(patient.DOB),
				'unit_floor': patient.unit_floor,
				'braden_score': patient.braden_score,
				'room': patient.room,
				'mobility': patient.mobility,
				'body_locations': []
			      }

		body_locations = DBBodyLocation.query.filter_by(patient_id=patient.id).all()
		for x in body_locations:
			device = {
					'JSID': x.JSID,
					'sensor_serial': x.sensor_serial,
					'is_wound': x.is_wound,
					'wound_existing_since': x.wound_existing_since.strftime("%Y.%m.%d") if x.wound_existing_since else None,
					'wound_stage': x.wound_stage,
					'alarm_threshold_minutes': x.alarm_threshold_minutes,
					'alarm_clear_multiple': x.alarm_clear_multiple,
					'wound_measurement': x.wound_measurement,
					'wound_acquisition': x.wound_acquisition,
					'wound_outcome': x.wound_outcome
				 }
			new_patient['body_locations'].append(device)
		return new_patient

	def serialize(self, patient):
		if patient.diagnosis:
			diagnosis = patient.diagnosis
			patient.diagnosis = None
		else:
			diagnosis = {}

		if patient.past_diagnosis:
			past_diagnosis = patient.past_diagnosis
			patient.past_diagnosis = None
		else:
			past_diagnosis = {}

		if patient.medication:
			medication = patient.medication
			patient.medication = None
		else:
			medication = {}

		patient_json = PatientJsonSerializer().serialize(patient)


		diagnosis_list = []
		past_diagnosis_list = []
		medication_list = []

		if diagnosis:
			diagnosis = DiagnosisJsonSerializer().serialize(diagnosis)
			diagnosis.pop('id', None)
			diagnosis.pop('patient_id', None)


			for d in DIAGNOSIS_FIELD_NAMES:
				value = {}
				value['name'] = d['name']
				value['value'] = diagnosis[d['name']]
				value['display_name'] = d['display_name']
				diagnosis_list.append(value)

		patient_json['diagnosis'] = diagnosis_list

		if past_diagnosis:
			past_diagnosis = DiagnosisJsonSerializer().serialize(past_diagnosis)
			past_diagnosis.pop('id', None)
			past_diagnosis.pop('patient_id', None)

			for d in DIAGNOSIS_FIELD_NAMES:
				value = {}
				value['name'] = d['name']
				value['value'] = past_diagnosis[d['name']]
				value['display_name'] = d['display_name']
				past_diagnosis_list.append(value)

		patient_json['past_diagnosis'] = past_diagnosis_list


		if medication:
			medication = MedicationJsonSerializer().serialize(medication)
			medication.pop('id', None)
			medication.pop('patient_id', None)

			for m in MEDICATION_FIELD_NAMES:
				value = {}
				value['name'] = m['name']
				value['value'] = medication[m['name']]
				value['display_name'] = m['display_name']
				medication_list.append(value)

		patient_json['medication'] = medication_list

		#TODO FIX
		activation = DBPatientActivation.query.filter_by(patient_id=patient.id).order_by(DBPatientActivation.id.desc()).first()

		if activation:
			patient_json['activation_status'] = activation.status
		else:
			patient_json['activation_status'] = INACTIVATED_STATUS
		if not patient_json.get('last_name'):
			patient_json['last_name'] = ''

		return patient_json

	@validate_jwt_user_token
	@swagger.operation(
		notes='none',
		nickname='create patient',
		parameters=[
			{
				"name": "medical_record_number",
				"description": "patient identifier",
				"required": True,
				"dataType": "int",
				"paramType": "body"
			},
			{
				"name": "gender",
				"description": "gender",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "DOB",
				"description": "date of birth",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "unit_floor",
				"description": "patient location",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "bed_type",
				"description": "bed type",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "ethnicity",
				"description": "ethnicity",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "braden_score",
				"description": "braden score",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "mobility",
				"description": "mobility",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "diagnosis",
				"description": "diagnosis",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "medication",
				"description": "medication",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "height",
				"description": "height",
				"required": False,
				"dataType": "float",
				"paramType": "body"
			},
			{
				"name": "weight",
				"description": "weight",
				"required": False,
				"dataType": "float",
				"paramType": "body"
			},
			{
				"name": "albumin_level",
				"description": "albumin level",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "A1C",
				"description": "A1C",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "hemoglobin",
				"description": "hemoglobin",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "o2_saturation",
				"description": "o2 saturation",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "blood_pressure",
				"description": "blood pressure",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "incontinence",
				"description": "incontinence",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "room",
				"description": "room",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			}
		  ],
		responseMessages=[
			{
				"code": 204,
				"message": "patient created"
			},
			{
				"code": 200,
				"message": "Patient already exists, based on medical record number provided"
			},
			{
				"code": 400,
				"message": "Bad request"
			}
		  ]
		)
	def post(self, user=None, sub=None, role=None):
		#register patient in system
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			data = copy.deepcopy(request.json)

			patient_dict = {}

			if 'medical_record_number' in data:
				new_patient_id = data.get('pa_id')
			else:
				new_patient_id = str(uuid.uuid4())

			patient_dict['deleted'] = False
			patient_dict['pa_id'] = new_patient_id
			patient_dict['medical_record_number'] = new_patient_id
			patient_dict['name'] = data.get('name')
			patient_dict['last_name'] = data.get('last_name')
			patient_dict['gender'] = data.get('gender')
			patient_dict['DOB'] = data.get('DOB')
			patient_dict['unit_floor'] = data.get('unit_floor')
			patient_dict['bed_type'] = data.get('bed_type')
			patient_dict['ethnicity'] = data.get('ethnicity')
			patient_dict['braden_score'] = data.get('braden_score')
			patient_dict['mobility'] = data.get('mobility')
			patient_dict['weight'] = data.get('weight')
			patient_dict['height'] = data.get('height')
			patient_dict['albumin_level'] = data.get('albumin_level')
			patient_dict['A1C'] = data.get('A1C')
			patient_dict['hemoglobin'] = data.get('hemoglobin')
			patient_dict['o2_saturation'] = data.get('o2_saturation')
			patient_dict['blood_pressure'] = data.get('blood_pressure')
			patient_dict['incontinence'] = data.get('incontinence')
			patient_dict['units'] = data.get('units')
			patient_dict['date_of_admission'] = data.get('date_of_admission')
			patient_dict['room'] = data.get('room')
			if data.get('weight') and data.get('height'):
				if data.get('height') != '0':
					height = float(data.get('height')) / 100
					patient_dict['bmi'] = float(data.get('weight'))/(height * height)

			patient = DBPatient(**patient_dict)
			db.session.add(patient)
			db.session.flush()

			patient = DBPatient.query.filter_by(pa_id=new_patient_id).first()

			diagnosis_history = ''
			past_diagnosis_history = ''
			medication_history = ''

			diagnosis_dict = None
			past_diagnosis_dict = None
			medication_dict = None


			if 'diagnosis' in data:
				diagnosis_dict = {}
				diagnosis_dict['patient_id'] = patient.id
				for d in data['diagnosis']:
					if d['value']:
						diagnosis_history = diagnosis_history + d['display_name'] + ', '
					d.pop('display_name')
					diagnosis_dict[d['name']] = d['value']
				#remove last comma
				if len(diagnosis_history) > 0:
					diagnosis_history = diagnosis_history[:-2]

			if 'past_diagnosis' in data:
				past_diagnosis_dict = {}
				past_diagnosis_dict['past_diagnosis_patient_id'] = patient.id
				for d in data['past_diagnosis']:
					if d['value']:
						past_diagnosis_history = past_diagnosis_history + d['display_name'] + ', '
					d.pop('display_name')
					past_diagnosis_dict[d['name']] = d['value']
				#remove last comma
				if len(diagnosis_history) > 0:
					past_diagnosis_history = past_diagnosis_history[:-2]


			if 'medication' in data:
				medication_dict = {}
				medication_dict['patient_id'] = patient.id
				for m in data['medication']:
					if m['value']:
						medication_history = medication_history + m['display_name'] + ', '
					m.pop('display_name')
					medication_dict[m['name']] = m['value']
				#remove last comma
				if len(medication_history) > 0:
					medication_history = medication_history[:-2]

			if diagnosis_dict:
				patient.diagnosis = DBDiagnosis(**diagnosis_dict)
			if past_diagnosis_dict:
				patient.past_diagnosis = DBDiagnosis(**past_diagnosis_dict)
			if medication_dict:
				patient.medication = DBMedication(**medication_dict)

			patient_dict['user'] = user
			patient_dict['date_of_record'] = utcformysqlfromtimestamp(nowtimestamp())
			patient_dict['diagnosis'] = diagnosis_history
			patient_dict['past_diagnosis'] = past_diagnosis_history
			patient_dict['medication'] = medication_history
			patient_history = DBPatientHistory(**patient_dict)
			db.session.add(patient_history)
			db.session.flush()



			for location in BODY_LOCATIONS:
				default_location = DBGlobalLocationSettings.query.filter_by(JSID=location).first()
				default_location_dict = default_location.__dict__
				default_location_dict['patient_id'] = patient.id
				default_location_dict['medical_record_number'] = patient.medical_record_number
				default_location_dict['sensor_serial'] = SENSOR_UNASSIGNED
				default_location_dict.pop('_sa_instance_state')
				default_location_dict.pop('id')
				body_location = DBBodyLocation(**default_location_dict)
				db.session.add(body_location)
			db.session.commit()

			status_code = status.HTTP_200_OK
			response = {'pa_id' : patient.pa_id }

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code

	@validate_jwt_user_token
	@swagger.operation(
		notes='none',
		nickname='update patient',
		parameters=[
			{
				"name": "medical_record_number",
				"description": "patient identifier",
				"required": True,
				"dataType": "int",
				"paramType": "body"
			},
			{
				"name": "gender",
				"description": "gender",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "DOB",
				"description": "date of birth",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "unit_floor",
				"description": "patient location",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "bed_type",
				"description": "bed type",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "ethnicity",
				"description": "ethnicity",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "braden_score",
				"description": "braden score",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "mobility",
				"description": "mobility",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "diagnosis",
				"description": "diagnosis",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "medication",
				"description": "medication",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "height",
				"description": "height",
				"required": False,
				"dataType": "float",
				"paramType": "body"
			},
			{
				"name": "weight",
				"description": "weight",
				"required": False,
				"dataType": "float",
				"paramType": "body"
			},
			{
				"name": "albumin_level",
				"description": "albumin level",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "A1C",
				"description": "A1C",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "hemoglobin",
				"description": "hemoglobin",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "o2_saturation",
				"description": "o2 saturation",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "blood_pressure",
				"description": "blood pressure",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "incontinence",
				"description": "incontinence",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			},
			{
				"name": "room",
				"description": "room",
				"required": False,
				"dataType": "string",
				"paramType": "body"
			}
		  ],
		responseMessages=[
			{
				"code": 204,
				"message": "patient created"
			},
			{
				"code": 400,
				"message": "Bad request"
			},
			{
				"code": 404,
				"message": "patient not found"
			}
		  ]
		)
	def put(self, user=None, sub=None, role=None, medical_record_number=None):
		#link patient with device
		response = None
		status_code = status.HTTP_400_BAD_REQUEST
		try:
			data = copy.deepcopy(request.json)
			patient = DBPatient.query.filter_by(pa_id=data.get('pa_id')).first()
			device = DBDevice.query.filter_by(patient_id=patient.id).first()

			# only a device associated with a patient should be able to update
			if patient and device and (device.serial == sub or sub.upper() == "N/A"):
				patient.medical_record_number = data.get('pa_id')
				patient.name = data.get('name')
				patient.last_name = data.get('last_name')
				patient.gender = data.get('gender')
				patient.DOB = data.get('DOB')
				patient.unit_floor = data.get('unit_floor')
				patient.bed_type = data.get('bed_type')
				patient.ethnicity = data.get('ethnicity')
				patient.braden_score = data.get('braden_score')
				patient.mobility = data.get('mobility')
				patient.weight = data.get('weight')
				patient.height = data.get('height')
				patient.albumin_level = data.get('albumin_level')
				patient.A1C = data.get('A1C')
				patient.hemoglobin = data.get('hemoglobin')
				patient.o2_saturation = data.get('o2_saturation')
				patient.blood_pressure = data.get('blood_pressure')
				patient.incontinence = data.get('incontinence')
				patient.units = data.get('units')
				patient.date_of_admission = data.get('date_of_admission')
				patient.room = data.get('room')

				if data.get('weight') and data.get('height'):
					if data.get('height') != '0':
						height = float(data.get('height')) / 100
						patient.bmi = float(data.get('weight'))/(height * height)

				patient_dict = dict(vars(patient))

				diagnosis_history = ''
				past_diagnosis_history = ''
				medication_history = ''

				diagnosis_dict = None
				past_diagnosis_dict = None
				medication_dict = None


				if 'diagnosis' in data:
					diagnosis_dict = {}
					diagnosis_dict['patient_id'] = patient.id
					for d in data['diagnosis']:
						if d['value']:
							diagnosis_history = diagnosis_history + d['display_name'] + ', '
						d.pop('display_name')
						diagnosis_dict[d['name']] = d['value']
					if len(diagnosis_history) > 0:
						diagnosis_history = diagnosis_history[:-2]

				if 'past_diagnosis' in data:
					past_diagnosis_dict = {}
					past_diagnosis_dict['past_diagnosis_patient_id'] = patient.id
					for d in data['past_diagnosis']:
						if d['value']:
							past_diagnosis_history = past_diagnosis_history + d['display_name'] + ', '
						d.pop('display_name')
						past_diagnosis_dict[d['name']] = d['value']
					if len(past_diagnosis_history) > 0:
						past_diagnosis_history = past_diagnosis_history[:-2]

				if 'medication' in data:
					medication_dict = {}
					medication_dict['patient_id'] = patient.id
					for m in data['medication']:
						if m['value']:
							medication_history = medication_history + m['display_name'] + ', '
						m.pop('display_name')
						medication_dict[m['name']] = m['value']
					if len(medication_history) > 0:
						medication_history = medication_history[:-2]

				if diagnosis_dict:
					patient.diagnosis = DBDiagnosis(**diagnosis_dict)
				if past_diagnosis_dict:
					patient.past_diagnosis = DBDiagnosis(**past_diagnosis_dict)
				if medication_dict:
					patient.medication = DBMedication(**medication_dict)

				db.session.flush()

				patient_dict.pop('id', None)
				patient_dict.pop('device', None)
				patient_dict.pop('events', None)
				patient_dict.pop('diagnosis', None)
				patient_dict.pop('past_diagnosis', None)
				patient_dict.pop('medication', None)
				patient_dict.pop('body_locations', None)
				patient_dict.pop('activations', None)
				patient_dict.pop('_sa_instance_state', None)
				patient_dict['user'] = user
				patient_dict['date_of_record'] = utcformysqlfromtimestamp(nowtimestamp())
				patient_dict['diagnosis'] = diagnosis_history
				patient_dict['past_diagnosis'] = past_diagnosis_history
				patient_dict['medication'] = medication_history

				patient_history = DBPatientHistory(**patient_dict)
				db.session.add(patient_history)

				db.session.commit()
				status_code = status.HTTP_204_NO_CONTENT
			else:
				status_code = status.HTTP_404_NOT_FOUND

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

#		log(request.remote_addr, request.path, request.method, request.json, status_code, user=user, device=None)
		return response, status_code
