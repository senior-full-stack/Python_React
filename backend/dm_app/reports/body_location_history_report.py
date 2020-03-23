from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token_reports, profiled
from ..globs import *
import io
import csv

class BodyLocationHistoryReport(Resource):
	@swagger.operation(
		notes='none',
		responseClass=DBBodyLocationHistory.__name__,
		nickname='get body location history reports',
		parameters=[
			{
				"name": "medical_record_number",
				"description": "a patient's medical record number to filter records",
				"required": False,
				"dataType": "string",
				"paramType": "url param"
			},
			{
				"name": "format",
				"description": "json or csv, defaults to json",
				"required": False,
				"dataType": "string",
				"paramType": "url args"
			}
		  ],
		responseMessages=[
			{
				"code": 200,
				"message": "An array of location history reports"
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

			if not medical_record_number:
				medical_record_number = request.args.get('medical_record_number', None)

			unit_floor = request.args.get('unit_floor')

			report_query = DBBodyLocationHistory.query.join(DBPatient, 
				DBPatient.medical_record_number == DBBodyLocationHistory.medical_record_number).filter(DBPatient.deleted == False).add_columns(DBPatient.name)

			if medical_record_number:
				medical_record_number = medical_record_number.split(',')
				report_query = report_query.filter(DBBodyLocationHistory.medical_record_number.in_(medical_record_number))
			if start:
				report_query = report_query.filter(DBBodyLocationHistory.date_of_record >= start)
			if end:
				report_query = report_query.filter(DBBodyLocationHistory.date_of_record < end)
			if unit_floor:
				report_query = report_query.filter(DBPatient.unit_floor == unit_floor)

			location_history = report_query.order_by(DBBodyLocationHistory.date_of_record.desc()).all()

			response = []
			if location_history:
				for history, name in location_history:
					history_json = BodyLocationHistoryJsonSerializer().serialize(history)
					history_json['name'] = name
					response.append(history_json)
			response = {'body_location_history_reports' : response, 'total_amount': len(response)}
			status_code = status.HTTP_200_OK

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)

		format = request.args.get('format')
		if status_code == status.HTTP_200_OK and format and format.lower() == CSV:
			return self.output_csv(response['body_location_history_reports'], status_code, CSV_HEADERS)
		else:
			response['body_location_history_reports'] = response['body_location_history_reports'][:1000]
			return response, status_code

	@api.representation('text/csv')
	def output_csv(self, data, code, headers=None):
		csv_output = io.BytesIO()
		for d in data:
			if 'id' in d: d.pop('id')
			if 'sensor_removal' in d: d.pop('sensor_removal')
			if 'medical_record_number' in d: d.pop('medical_record_number')
			if 'stopped' in d: d.pop('stopped')
			if 'force_state' in d: d.pop('force_state')
			if 'fast_blink' in d: d.pop('fast_blink')
			if 'distance' in d: d.pop('distance')
#			if 'type' in d: d.pop('type')
			if 'battery' in d: d.pop('battery')
			if 'last_seen' in d: d.pop('last_seen')
			if 'under_pressure_milliseconds' in d: d.pop('under_pressure_milliseconds')
			if 'pressure_state' in d: d.pop('pressure_state')
			if 'has_previous_alert' in d: d.pop('has_previous_alert')
			if 'site_assessment' in d: d.pop('site_assessment')
			if 'binary_state' in d: d.pop('binary_state')

		display_field_names = ['Patient Name', 'Location', 'Sensor Serial', 'Alarm Threshold (minutes)', 'Alarm Clear Multiple (x Threshold)', 
		'Previous alarm indicator duration (hours)', 'Body Location has a wound', 'Wound Alarm Threshold (minutes)',
		'Wound Alarm Clear Multiple (x Threshold)', 'Wound Stage', 'Wound dimensions', 'Existing Wound', 'Existing wound since',
		'Wound Outcome', 'Reason for removal', 'sensor_removal']
		writer = csv.DictWriter(csv_output, display_field_names)
		writer.writeheader()

		field_names = ['name', 'JSID', 'sensor_serial', 'alarm_threshold_minutes', 'alarm_clear_multiple', 'previous_alarm_threshold_hours', 
		'is_wound', 'wound_alarm_threshold_minutes', 'wound_alarm_clear_multiple', 'wound_stage', 'wound_measurement',
		'existing_wound', 'wound_existing_since', 'wound_outcome']
		writer = csv.DictWriter(csv_output, field_names)

		writer.writerows(data)

		return Response(response=csv_output.getvalue(), status=code, headers=headers, content_type='text/csv')
