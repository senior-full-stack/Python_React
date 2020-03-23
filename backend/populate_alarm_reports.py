from dm_app.app import db
from dm_app.models import *
from pprint import pprint
from dm_app.objects.event import Event
from dm_app.globs import *
from dm_app import *
from dateutil import rrule
from dateutil import tz

def convert_date_to_tz(date):
	if USE_TIMEZONE:
		to_zone = tz.gettz(TIMEZONE)
		from_zone = tz.gettz('UTC')
		utc = date.replace(tzinfo=from_zone)
		converted_date = utc.astimezone(to_zone)
	else:
		converted_date = date
	return converted_date

def log_turned_response(event, medical_record_number, unit_floor):
	admin_default = DBAdminDefault.query.first()
	window_start = event['instance'] - timedelta(minutes=admin_default.alert_reponse_window)
	previous_turn = DBEvent.query.filter(DBEvent.patient_id==event['patient_id'], DBEvent.range_end >= window_start, 
		DBEvent.range_end <= event['instance'], DBEvent.message == 'PATIENT WAS TURNED BY CAREGIVER').order_by(DBEvent.range_start.desc()).all()
	if not previous_turn:
		previous_events = DBEvent.query.filter(DBEvent.patient_id==event['patient_id'], DBEvent.range_end >= window_start, 
			DBEvent.range_end <= event['instance'], DBEvent.message == 'PRESSURE_ALARM').order_by(DBEvent.range_start.desc()).all()

		dates = {}

		for ev in previous_events:
			converted_date = convert_date_to_tz(ev.range_end)
			date = converted_date.date()
			hour = converted_date.hour
			if date not in dates:
				dates[date] = {}
			if hour not in dates[date]:
				dates[date][hour] = 0
			dates[date][hour] += 1

		for d in dates:
			for h in dates[d]:
				write_response_records(d, h, medical_record_number, unit_floor, caregiver_repositions=dates[d][h], patient_repositions=-1*(dates[d][h]))

def log_alarm(event, medical_record_number, unit_floor):
	log_date = convert_date_to_tz(event['range_start'])

	date = log_date.date()
	hour = log_date.hour

	write_response_records(date, hour, medical_record_number, unit_floor, alarms_occurred=1)

def log_alarm_clear(event, previous_event, medical_record_number, unit_floor):
	converted_event_date = convert_date_to_tz(event['range_start'])
	converted_previous_date = convert_date_to_tz(previous_event.range_start)
	date = converted_event_date.date()
	hour = converted_event_date.hour
	delta = converted_event_date - converted_previous_date
	previous_date = converted_previous_date.date()
	previous_hour = converted_previous_date.hour

	total_repositions = 1

	date_different = False
	hour_different = False

	admin_default = DBAdminDefault.query.first()
	window_start = event['range_start'] - timedelta(minutes=admin_default.alert_reponse_window)
	previous_turn = DBEvent.query.filter(DBEvent.patient_id == event['patient_id'], DBEvent.message == 'PATIENT WAS TURNED BY CAREGIVER',
		DBEvent.instance >= window_start, DBEvent.instance <= event['range_start']).first()
	if previous_turn:
		caregiver_repositions = 1
		patient_repositions = 0
	else:
		caregiver_repositions = 0
		patient_repositions = 1


	if converted_event_date.date() != converted_previous_date.date():
		date_different = True
	if converted_event_date.hour != converted_previous_date.hour:
		hour_different = True

	if not date_different and not hour_different:
		minute_range_start = converted_previous_date.minute
		minute_range_end = converted_event_date.minute

		write_response_records(date, hour, medical_record_number, unit_floor, caregiver_repositions=caregiver_repositions,
			patient_repositions=patient_repositions, total_repositions=total_repositions, minute_range_start=minute_range_start,
			minute_range_end=minute_range_end)

	else:
		for dt in rrule.rrule(rrule.HOURLY, dtstart=converted_previous_date.replace(minute=0, second=0, microsecond=0), until=converted_event_date):
			if dt.date() == previous_date and dt.hour == previous_hour:
				#start
				write_response_records(dt.date(), dt.hour, medical_record_number, unit_floor, 
					minute_range_start=converted_previous_date.minute, minute_range_end=59)
			elif dt.date() == date and dt.hour == hour:
				#end
				write_response_records(dt.date(), dt.hour, medical_record_number, unit_floor, caregiver_repositions=caregiver_repositions,
					patient_repositions=patient_repositions, total_repositions=total_repositions, minute_range_start=0, 
					minute_range_end=converted_event_date.minute)
			else:
				#middle
				write_response_records(dt.date(), dt.hour, medical_record_number, unit_floor, minute_range_start=0, minute_range_end=59)



def write_response_records(date, hour, pa_id, unit_floor, alarms_occurred=None, patient_repositions=None, 
	caregiver_repositions=None, total_repositions=None, minute_range_start=None, minute_range_end=None):

	alarm_response = DBAlarmResponse.query.filter_by(date=date, hour=hour, pa_id=pa_id).first()
	if alarm_response:
		if alarms_occurred:
			alarm_response.alarms_occurred += alarms_occurred
		if patient_repositions:
			alarm_response.patient_repositions += patient_repositions
			if alarm_response.patient_repositions < 0:
				alarm_response.patient_repositions = 0
		if caregiver_repositions:
			alarm_response.caregiver_repositions += caregiver_repositions
		if total_repositions:
			alarm_response.total_repositions += total_repositions
		if minute_range_start != None and minute_range_end != None:
			minutes_list = list(alarm_response.minutes_alarming)
			for x in range(minute_range_start, minute_range_end + 1):
				minutes_list[x] = '1'
			alarm_response.minutes_alarming = "".join(minutes_list)
		alarm_response.unit_floor = unit_floor
		db.session.merge(alarm_response)


	if not alarm_response:
		if not alarms_occurred:
			alarms_occurred = 0
		if not patient_repositions:
			patient_repositions = 0
		elif patient_repositions < 0:
			patient_repositions = 0
		if not caregiver_repositions:
			caregiver_repositions = 0
		if not total_repositions:
			total_repositions = 0
		minutes_alarming = ''
		for x in range(0, 60):
			minutes_alarming += '0'
		minutes_list = list(minutes_alarming)
		if minute_range_start != None and minute_range_end != None:
			for x in range(minute_range_start, minute_range_end + 1):
				minutes_list[x] = '1'
			minutes_alarming = "".join(minutes_list)
		alarm_response = DBAlarmResponse(date, hour, pa_id, alarms_occurred, patient_repositions, 
			caregiver_repositions, total_repositions, minutes_alarming, unit_floor)
		db.session.add(alarm_response)

print 'getting events'
es = DBEvent.query.order_by(DBEvent.id).all()
print 'got events'
print len(es)

latest = {}

for e in es:
	start_time = time.time()
	event = {}
	event['medical_record_number'] = e.medical_record_number
	event['unit_floor'] = e.unit_floor
	event['patient_id'] = e.patient_id
	event['device_id'] = e.device_id
	event['message'] = e.message

	if e.message.upper() == 'PATIENT WAS TURNED BY CAREGIVER':
		event['instance'] = e.instance
		#print '--- %s seconds ---' % (time.time() - start_time) 
		log_turned_response(event, e.medical_record_number, e.unit_floor)
		#print '--- %s seconds ---' % (time.time() - start_time) 
		print 'logged turn'
	else:
		if e.message.upper() in EVENT_TYPE_RANGE:
			if e.medical_record_number not in latest:
				latest[e.medical_record_number] = {}
				for location in BODY_LOCATIONS:
					latest[e.medical_record_number][location] = None


		if e.body_location_id:
			event['body_location_id'] = e.body_location_id
		if e.location:
			event['location'] = e.location

		if e.message.upper() == 'PRESSURE_ALARM':
			event['range_start'] = e.range_start

			#print '--- %s seconds ---' % (time.time() - start_time) 
			log_alarm(event, e.medical_record_number, e.unit_floor)
			latest[e.medical_record_number][e.location] = e
			#print '--- %s seconds ---' % (time.time() - start_time) 
			print 'logged alarm'

		elif e.message.upper() in EVENT_TYPE_RANGE:
			event['range_start'] = e.range_start

			previous_event = latest[e.medical_record_number][e.location]

			#print event
			#print '--- %s seconds ---' % (time.time() - start_time) 
			if previous_event and previous_event.message.upper() == 'PRESSURE_ALARM' and e.message.upper() != 'PRESSURE_ALARM':
				log_alarm_clear(event, previous_event, e.medical_record_number, e.unit_floor)

				#print '--- %s seconds ---' % (time.time() - start_time) 
				print 'logged clear'

			latest[e.medical_record_number][e.location] = e

db.session.commit()
