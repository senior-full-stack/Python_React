import requests
from pytz import timezone as pytimezone

from ..models import *
from ..utils import log, validate_jwt_user_token_reports, profiled
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from ..globs import *
import io
import csv

class EventReport(Resource):
	@swagger.operation(
		notes='none',
		responseClass=DBEventHistory.__name__,
		nickname='get event reports',
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
				"message": "An array of event reports, sorted by occurred date"
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
		events = None
		format = request.args.get('format')
		try:
			start_time = time.time()

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

			report_query = DBEventHistory.query.with_entities(DBEventHistory.unit_floor, DBEventHistory.event_type, DBEventHistory.occurred, DBEventHistory.location,
				DBEventHistory.sensor_serial, DBEventHistory.battery, DBEventHistory.distance, DBEventHistory.alarm_threshold_minutes,
				DBEventHistory.alarm_clear_multiple, DBEventHistory.previous_alarm_threshold_hours, DBEventHistory.wound_alarm_threshold_minutes,
				DBEventHistory.wound_alarm_clear_multiple).join(DBPatient, DBPatient.medical_record_number == DBEventHistory.medical_record_number).filter(
				DBPatient.deleted == False).add_columns(DBPatient.name, DBPatient.last_name).filter(DBEventHistory.event_type != 'Sensor Stopped')

			if medical_record_number:
				medical_record_number = medical_record_number.split(',')
				report_query = report_query.filter(DBEventHistory.medical_record_number.in_(medical_record_number))
				if start:
					report_query = report_query.filter(DBEventHistory.occurred >= start)
				if end:
					report_query = report_query.filter(DBEventHistory.occurred < end)
				if unit_floor:
					report_query = report_query.filter(DBEventHistory.unit_floor == unit_floor)

				events = report_query.order_by(DBEventHistory.occurred.desc()).all()

			else:
				struct_logger.msg(instance=LOGGING_INSTANCE, time='--- %s seconds ---' % (time.time() - start_time))
				#with profiled():

				engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=False)
				conn = engine.connect()
				start = None
				if request.args.get('start'):
					start = datetime.strptime(request.args.get('start'), '%Y-%m-%d %H:%M')
					start = start.strftime('%Y-%m-%d %H:%M:%S')
				end = None
				if request.args.get('end'):
					end = datetime.strptime(request.args.get('end'), '%Y-%m-%d %H:%M')
					end += timedelta(days=1)
					end = end.strftime('%Y-%m-%d %H:%M:%S')

				unit_floor = request.args.get('unit_floor')
				query_string = 'SELECT event_history.event_type AS event_type, event_history.unit_floor AS unit_floor, event_history.occurred AS occurred, event_history.location AS location, event_history.sensor_serial AS sensor_serial, event_history.battery AS battery, event_history.distance AS distance, event_history.alarm_threshold_minutes AS alarm_threshold_minutes, event_history.alarm_clear_multiple AS alarm_clear_multiple, event_history.previous_alarm_threshold_hours AS previous_alarm_threshold_hours, event_history.wound_alarm_threshold_minutes AS wound_alarm_threshold_minutes, event_history.wound_alarm_clear_multiple AS wound_alarm_clear_multiple, patient.name AS name, patient.last_name AS last_name FROM event_history INNER JOIN patient ON patient.medical_record_number = event_history.medical_record_number and patient.deleted = false '

				if start or end or unit_floor:
					query_string += 'WHERE '

				AND = False
				if start:
					query_string += 'event_history.occurred >= "' + start + '" '
					AND = True
				if end:
					if AND:
						query_string += 'and '
					else:
						AND = True
					query_string += 'event_history.occurred < "' + end + '" '
				if unit_floor:
					if AND:
						query_string += 'and '
					else:
						AND = True
					query_string += 'event_history.unit_floor = "' + unit_floor + '" '

				query_string += 'ORDER BY event_history.occurred DESC'

				result = conn.execute(query_string)

				struct_logger.msg(instance=LOGGING_INSTANCE, time='--- %s seconds ---' % (time.time() - start_time))
				events = result.fetchall()

			response = []
			if events:
				timezone = None
				if format and format.lower() == CSV:
					try:
						timezone = pytimezone(requests.get('http://freegeoip.net/json/' + str(request.remote_addr)).json().get('time_zone'))
					except:
						timezone = None
				prev_event = None
				for event in events:
					if (event.event_type not in ('Sensor came online', 'Device is plugged into power')
					    or not prev_event or prev_event and event.occurred - prev_event.occurred > timedelta(seconds=15) and
                            (prev_event.event_type == 'Sensor went offline' and event.event_type == 'Sensor came online' or
							    prev_event.event_type == 'Device is unplugged from power' and event.event_type == 'Device is plugged into power'
					        )):
						event_json = EventHistoryReportJsonSerializer(
								timezone=timezone,
								format='csv' if format and format.lower() == CSV else 'json'
						).serialize(event)
						response.append(event_json)
					else:
						response.pop()
					prev_event = event

			response = {'event_reports' : response, 'total_amount': len(response)}
			status_code = status.HTTP_200_OK


		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)

		if status_code == status.HTTP_200_OK and format and format.lower() == CSV:
			return self.output_csv(response['event_reports'], status_code, CSV_HEADERS)
		else:
			struct_logger.msg(instance=LOGGING_INSTANCE, time='--- %s seconds ---' % (time.time() - start_time))
			response['event_reports'] = response['event_reports'][:1000]
			return response, status_code

	@api.representation('text/csv')
	def output_csv(self, data, code, headers=None):
		csv_output = io.BytesIO()
		for d in data:
			if 'site_assessment' in d: d.pop('site_assessment')
			if 'sensor_removal' in d: d.pop('sensor_removal')
			if 'medical_record_number' in d: d.pop('medical_record_number')

		display_field_names = ['Patient Name', 'Patient Last Name', 'Unit Floor', 'Event Type', 'Event Occurred', 'Body Location', 'Sensor ID', 'Sensor Battery', 'Sensor Distance',
	'Alarm Threshold (minutes)', 'Alarm Clear Multiple', 'Previous Alarm Indicator Duration (hours)',
		'Wound Alarm Threshold (minutes)', 'Wound Alarm Clear Multiple']
		writer = csv.DictWriter(csv_output, display_field_names)
		writer.writeheader()

		field_names = ['name', 'last_name', 'unit_floor', 'event_type', 'occurred', 'location', 'sensor_serial', 'battery', 'distance',
	'alarm_threshold_minutes', 'alarm_clear_multiple', 'previous_alarm_threshold_hours',
		'wound_alarm_threshold_minutes', 'wound_alarm_clear_multiple']
		writer = csv.DictWriter(csv_output, field_names)

		writer.writerows(data)

		return Response(response=csv_output.getvalue(), status=code, headers=headers, content_type='text/csv')
