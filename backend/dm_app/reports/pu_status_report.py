from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token_reports, profiled
from ..globs import *
import io
import csv

class PUStatusReport(Resource):
	@swagger.operation(
		notes='none',
		responseClass=DBBodyLocation.__name__,
		nickname='get pressure injury status reports',
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
				"message": "An array of pressure injury status reports, sorted by name"
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

			report_query = DBBodyLocation.query.join(DBPatient).add_columns(DBPatient.name, DBPatient.last_name)

			if medical_record_number:
				medical_record_number = medical_record_number.split(',')
				report_query = report_query.filter(DBBodyLocation.medical_record_number.in_(medical_record_number))
			if start:
				report_query = report_query.filter(DBBodyLocation.wound_existing_since >= start)
			if end:
				report_query = report_query.filter(DBBodyLocation.wound_existing_since < end)
			if unit_floor:
				report_query = report_query.filter(DBPatient.unit_floor == unit_floor)

			wounds = report_query.order_by(DBPatient.name).all()

			response = []
			if wounds:
				for wound, name, last_name in wounds:
					wound_json = PUStatusReportJsonSerializer().serialize(wound)
					wound_json['location'] = wound_json.get('JSID')
					wound_json['name'] = name
					wound_json['last_name'] = last_name


					response.append(wound_json)

			response = {'pu_status_reports' : response, 'total_amount': len(response)}
			status_code = status.HTTP_200_OK

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)

		format = request.args.get('format')
		if status_code == status.HTTP_200_OK and format and format.lower() == CSV:
			return self.output_csv(response['pu_status_reports'], status_code, CSV_HEADERS)
		else:
			response['pu_status_reports'] = response['pu_status_reports'][:1000]
			return response, status_code

	@api.representation('text/csv')
	def output_csv(self, data, code, headers=None):
		csv_output = io.BytesIO()
		for d in data:
			if 'medical_record_number' in d: d.pop('medical_record_number')
			if 'is_wound' in d: d.pop('is_wound')
			if 'location' in d: d.pop('location')

		display_field_names = ['Patient Name', 'Patient Last Name', 'Wound Location', 'Existing Wound', 'Wound Existing Since', 'Wound Stage', 'Wound Measurement',
		'Outcome']
		writer = csv.DictWriter(csv_output, display_field_names)
		writer.writeheader()

		field_names = ['name', 'last_name', 'JSID', 'existing_wound', 'wound_existing_since', 'wound_stage', 'wound_measurement', 'wound_outcome']
		writer = csv.DictWriter(csv_output, field_names)

		writer.writerows(data)

		return Response(response=csv_output.getvalue(), status=code, headers=headers, content_type='text/csv')
