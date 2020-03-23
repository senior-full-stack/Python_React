import requests
from pytz import timezone as pytimezone
from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token_reports, profiled
from ..globs import *
import io
import csv


class PatientInfoReport(Resource):
	@swagger.operation(
		notes='none',
		responseClass=DBPatientHistory.__name__,
		nickname='get patient info reports',
		parameters=[
			{
				"name": "medical_record_number",
				"description": "a patient's medical record number to filter reports",
				"required": False,
				"dataType": "string",
				"paramType": "url param"
			}
		  ],
		responseMessages=[
			{
				"code": 200,
				"message": "An array of patient info reports, sorted by name"
			},
			{
				"code": 400,
				"message": "Bad request"
			}
		  ]
		)
	@validate_jwt_user_token_reports
	def get(self, user=None, sub=None, medical_record_number=None, role=None):
		response = None
		format = request.args.get('format')
		try:
			start = None
			if request.args.get('start'):
				start = datetime.strptime(request.args.get('start'), '%Y-%m-%d %H:%M')

			end = None
			if request.args.get('end'):
				end = datetime.strptime(request.args.get('end'), '%Y-%m-%d %H:%M')
				end += timedelta(days=1)

			if not medical_record_number:
				medical_record_number = request.args.get('medical_record_number', None)

			unit_floor = request.args.get('unit_floor')

			report_query = DBPatientHistory.query.join(DBPatient, 
						DBPatient.medical_record_number == DBPatientHistory.medical_record_number).filter(DBPatient.deleted == False)

			if medical_record_number:
				medical_record_number = medical_record_number.split(',')
				report_query = report_query.filter(DBPatientHistory.medical_record_number.in_(medical_record_number))
			if start:
				report_query = report_query.filter(DBPatientHistory.date_of_record >= start)
			if end:
				report_query = report_query.filter(DBPatientHistory.date_of_record < end)
			if unit_floor:
				report_query = report_query.filter(DBPatientHistory.unit_floor == unit_floor)

			patients = report_query.order_by(DBPatientHistory.name).all()

			response = []
			if patients:
				timezone = None
				if format and format.lower() == CSV:
					try:
						timezone = pytimezone(
							requests.get('http://freegeoip.net/json/' + str(request.remote_addr)).json().get(
								'time_zone'))
					except:
						timezone = None
				for patient in patients:
					patient_json = PatientInfoReportJsonSerializer(
						timezone=timezone,
						format='csv' if format and format.lower() == CSV else 'json'
					).serialize(patient)
					patient_json['username'] = patient_json['user']
					response.append(patient_json)

			response = {'patient_reports' : response, 'total_amount': len(response)}
			status_code = status.HTTP_200_OK

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)


		if status_code == status.HTTP_200_OK and format and format.lower() == CSV:
			return self.output_csv(response['patient_reports'], status_code, CSV_HEADERS)
		else:
			response['patient_reports'] = response['patient_reports'][:1000]
			return response, status_code

	@api.representation('text/csv')
	def output_csv(self, data, code, headers=None):
		csv_output = io.BytesIO()
		for d in data:
			if 'user' in d: d.pop('user')
			if 'incontinence' in d: d.pop('incontinence')
			if 'medical_record_number' in d: d.pop('medical_record_number')
			if 'pa_id' in d: d.pop('pa_id')
			if 'deleted' in d: d.pop('deleted')

		display_field_names = ['Name', 'Last Name', 'Date of Record', 'Username', 'Gender', 'DOB', 'Date of Admission', 'Room', 'Units', 'Unit/Floor',
		'Bed Type', 'Ethnicity', 'Braden Score', 'Mobility', 'Diagnosis', 'Past Diagnosis', 'Medication', 'Weight', 'Height', 'BMI',  
		'Albumin Level', 'A1C', 'Hemoglobin', 'O2 Saturation', 'Blood Pressure']
		writer = csv.DictWriter(csv_output, display_field_names)
		writer.writeheader()

		field_names = ['name', 'last_name', 'date_of_record', 'username', 'gender', 'DOB', 'date_of_admission', 'room', 'units', 'unit_floor',
		'bed_type', 'ethnicity', 'braden_score', 'mobility', 'diagnosis', 'past_diagnosis', 'medication', 'weight', 'height', 'bmi',  
		'albumin_level', 'A1C', 'hemoglobin', 'o2_saturation', 'blood_pressure']
		writer = csv.DictWriter(csv_output, field_names)

		writer.writerows(data)

		return Response(response=csv_output.getvalue(), status=code, headers=headers, content_type='text/csv')


