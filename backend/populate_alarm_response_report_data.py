from dm_app.app import db
from dm_app.models import *
from dm_app.rfc3339 import now
from dm_app.utils import *
from pprint import pprint
from dm_app.objects.event import Event
from dm_app.globs import *
from dm_app import *
from dateutil import rrule
from dateutil import tz
import numpy

def run():
	end = now()
	end = end.replace(tzinfo=None, hour=23, minute=59, second=59)
	end -= timedelta(days=1)
	ps = DBPatient.query.all()
	for p in ps:
		pa = DBPatientActivation.query.filter(DBPatientActivation.patient_id==p.id, DBPatientActivation.status.in_(['Activated', 'Reactivated'])).first()
		if pa and p.deleted == False:
			write_data(end, medical_record_number=p.medical_record_number)
	ad = DBAdminDefault.query.first()
	us = json.loads(ad.unit_floor)
	for u in us:
		write_data(end, unit_floor=u)
	write_data(end, all=True)

	db.session.commit()

def write_data(end, medical_record_number=None, unit_floor=None, all=None):
	#try:
	start_time = time.time()

	populate_active_patients()

	from_zone = tz.gettz('UTC')

	if medical_record_number:
		print medical_record_number
		response_query = DBAlarmResponse.query.filter_by(pa_id=medical_record_number).order_by(DBAlarmResponse.date, DBAlarmResponse.hour)
		start = DBPatientActivation.query.join(DBPatient).filter(DBPatient.pa_id==medical_record_number).order_by(DBPatientActivation.occurred).first()

		if start:
			start = start.occurred
			#start = start.replace(tzinfo=from_zone)
			response_query = response_query.filter(DBAlarmResponse.date >= start.date())
		if end:
			#end = end.replace(tzinfo=from_zone)
			response_query = response_query.filter(DBAlarmResponse.date <= end.date())


	elif unit_floor:
		print unit_floor
		response_query = DBAlarmResponse.query.filter_by(unit_floor=unit_floor).order_by(DBAlarmResponse.date, DBAlarmResponse.hour)
		start = DBPatientActivation.query.join(DBPatient).filter(DBPatient.unit_floor==unit_floor).order_by(DBPatientActivation.occurred).first()

		if start:
			start = start.occurred
			#start = start.replace(tzinfo=from_zone)
			response_query = response_query.filter(DBAlarmResponse.date >= start.date())
		if end:
			response_query = response_query.filter(DBAlarmResponse.date <= end.date())
	elif all:
		print 'all'
		response_query = DBAlarmResponse.query.order_by(DBAlarmResponse.date, DBAlarmResponse.hour)
		start = DBPatientActivation.query.order_by(DBPatientActivation.occurred).first()

		if start:
			start = start.occurred
			#start = start.replace(tzinfo=from_zone)
			response_query = response_query.filter(DBAlarmResponse.date >= start.date())
		if end:
			response_query = response_query.filter(DBAlarmResponse.date <= end.date())

	responses = response_query.all()

	if start and end:
		if unit_floor:
			patients_active = DBPatientsActive.query.filter(DBPatientsActive.date >= start.date(), DBPatientsActive.date <= end.date(), 
				DBPatientsActive.unit_floor == unit_floor).order_by(DBPatientsActive.date, DBPatientsActive.hour).all()
		elif medical_record_number:
			patients_active = get_patients_active_patient(medical_record_number, start, end)
		else:
			patients_active = DBPatientsActive.query.filter(DBPatientsActive.date >= start.date(), DBPatientsActive.date <= end.date()).order_by(
				DBPatientsActive.date, DBPatientsActive.hour).all()

		#print patients_active

		for dt in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
			day_json = []
			alarms = [0] * 24
			alarming = [0] * 24
			minutes_alarms = [0] * 24
			active_patients = [0] * 24
			alarmed_patients = [0] * 24
			alarmed_active = [0] * 24
			alarms_alarmed_patients = [0] * 24
			max_alarms = [0] * 24
			min_alarms = [0] * 24
			alarms_top = [0] * 24
			alarms_mid = [0] * 24
			alarms_low = [0] * 24
			minutes_alarmed_patients = [0] * 24
			max_minutes = [0] * 24
			min_minutes = [0] * 24
			minutes_top = [0] * 24
			minutes_mid = [0] * 24
			minutes_low = [0] * 24
			date_exists = [x for x in responses if x.date == dt.date()]
			if date_exists:
				date = dt.date().strftime('%Y-%m-%d')
				for i in range(0, 24):

					minutes_alarming = [x.minutes_alarming.count('1') for x in responses if x.hour == i and x.date == dt.date()]
					if minutes_alarming:
						alarming[i] = sum(minutes_alarming)
						max_minutes[i] = max(minutes_alarming)
						min_minutes[i] = min(minutes_alarming)

						minutes_sorted = sorted(minutes_alarming, reverse=True)
						split_list = numpy.array_split(numpy.array(minutes_sorted),3)
						if len(split_list) > 0 and len(split_list[0]) > 0:
							minutes_top[i] = round(d(sum(split_list[0]), len(split_list[0])), 2)
						if len(split_list) > 1 and len(split_list[1]) > 0:
							minutes_mid[i] = round(d(sum(split_list[1]), len(split_list[1])), 2)
						if len(split_list) > 2 and len(split_list[2]) > 0:
							minutes_low[i] = round(d(sum(split_list[2]), len(split_list[2])), 2)

					alarms_occurred = [x.alarms_occurred for x in responses if x.hour == i and x.date == dt.date()]
					if alarms_occurred:
						alarms[i] = sum(alarms_occurred)
						max_alarms[i] = max(alarms_occurred)
						min_alarms[i] = min(alarms_occurred)

						alarms_sorted = sorted(alarms_occurred, reverse=True)
						split_list = numpy.array_split(numpy.array(alarms_sorted),3)
						if len(split_list) > 0 and len(split_list[0]) > 0:
							alarms_top[i] = round(d(sum(split_list[0]), len(split_list[0])), 2)
						if len(split_list) > 1 and len(split_list[1]) > 0:
							alarms_mid[i] = round(d(sum(split_list[1]), len(split_list[1])), 2)
						if len(split_list) > 2 and len(split_list[2]) > 0:
							alarms_low[i] = round(d(sum(split_list[2]), len(split_list[2])), 2)

					if alarms[i] > 0:
						minutes_alarms[i] = round(d(alarming[i], alarms[i]), 2)

					apatients = [x.pa_id for x in responses if x.hour == i and x.alarms_occurred >= 1 and x.date == dt.date()]
					if apatients:
						alarmed_patients[i] = len(apatients)

						if alarmed_patients[i] > 0:
							minutes_alarmed_patients[i] = round(d(alarming[i], alarmed_patients[i]), 2)
							alarms_alarmed_patients[i] = round(d(alarms[i], alarmed_patients[i]), 2)

					active = [x.number_active for x in patients_active if x.hour == i and x.date == dt.date()]
					if active:
						active_patients[i] = sum(active)

						if active_patients[i] > 0:
							if alarmed_patients[i]:
								alarmed_active[i] = round(d(alarmed_patients[i], active_patients[i]), 2)

				total = sum(alarms)
				average = round(d(total, len(alarms)), 2)
				row = make_row(ALARM_ALARMS, date, alarms[0], alarms[1], alarms[2], alarms[3], alarms[4], alarms[5],
					alarms[6], alarms[7], alarms[8], alarms[9], alarms[10], alarms[11], alarms[12], alarms[13],
					alarms[14], alarms[15], alarms[16], alarms[17], alarms[18], alarms[19], alarms[20],
					alarms[21], alarms[22], alarms[23], total, average)
				day_json.append(row)
				

				total = sum(alarming)
				average = round(d(total, len(alarming)), 2)
				row = make_row(ALARM_MINUTES_ALARMING, date, alarming[0], alarming[1], alarming[2], alarming[3], alarming[4], alarming[5],
					alarming[6], alarming[7], alarming[8], alarming[9], alarming[10], alarming[11], alarming[12], alarming[13],
					alarming[14], alarming[15], alarming[16], alarming[17], alarming[18], alarming[19], alarming[20],
					alarming[21], alarming[22], alarming[23], total, average)
				day_json.append(row)
				

				total = sum(minutes_alarms)
				average = round(d(total, len(minutes_alarms)), 2)
				row = make_row(ALARM_MINUTES_ALARMS, date, minutes_alarms[0], minutes_alarms[1], minutes_alarms[2], minutes_alarms[3], minutes_alarms[4], minutes_alarms[5],
					minutes_alarms[6], minutes_alarms[7], minutes_alarms[8], minutes_alarms[9], minutes_alarms[10], minutes_alarms[11], minutes_alarms[12], minutes_alarms[13],
					minutes_alarms[14], minutes_alarms[15], minutes_alarms[16], minutes_alarms[17], minutes_alarms[18], minutes_alarms[19], minutes_alarms[20],
					minutes_alarms[21], minutes_alarms[22], minutes_alarms[23], total, average)
				day_json.append(row)
				

				total = sum(active_patients)
				average = round(d(total, len(active_patients)), 2)
				row = make_row(ACTIVE_PATIENTS, date, active_patients[0], active_patients[1], active_patients[2], active_patients[3], active_patients[4], active_patients[5],
					active_patients[6], active_patients[7], active_patients[8], active_patients[9], active_patients[10], active_patients[11], active_patients[12], active_patients[13],
					active_patients[14], active_patients[15], active_patients[16], active_patients[17], active_patients[18], active_patients[19], active_patients[20],
					active_patients[21], active_patients[22], active_patients[23], total, average)
				day_json.append(row)

				total = sum(alarmed_patients)
				average = round(d(total, len(alarmed_patients)), 2)
				row = make_row(ALARM_ALARMED_PATIENTS, date, alarmed_patients[0], alarmed_patients[1], alarmed_patients[2], alarmed_patients[3], alarmed_patients[4], alarmed_patients[5],
					alarmed_patients[6], alarmed_patients[7], alarmed_patients[8], alarmed_patients[9], alarmed_patients[10], alarmed_patients[11], alarmed_patients[12], alarmed_patients[13],
					alarmed_patients[14], alarmed_patients[15], alarmed_patients[16], alarmed_patients[17], alarmed_patients[18], alarmed_patients[19], alarmed_patients[20],
					alarmed_patients[21], alarmed_patients[22], alarmed_patients[23], total, average)
				day_json.append(row)

				total = sum(alarmed_active)
				average = round(d(total, len(alarmed_active)), 2)
				row = make_row(ALARM_ALARMED_ACTIVE, date, alarmed_active[0], alarmed_active[1], alarmed_active[2], alarmed_active[3], alarmed_active[4], alarmed_active[5],
					alarmed_active[6], alarmed_active[7], alarmed_active[8], alarmed_active[9], alarmed_active[10], alarmed_active[11], alarmed_active[12], alarmed_active[13],
					alarmed_active[14], alarmed_active[15], alarmed_active[16], alarmed_active[17], alarmed_active[18], alarmed_active[19], alarmed_active[20],
					alarmed_active[21], alarmed_active[22], alarmed_active[23], total, average)
				day_json.append(row)

				total = sum(alarms_alarmed_patients)
				average = round(d(total, len(alarms_alarmed_patients)), 2)
				row = make_row(ALARM_ALARMS_ALARMED, date, alarms_alarmed_patients[0], alarms_alarmed_patients[1], alarms_alarmed_patients[2], alarms_alarmed_patients[3], alarms_alarmed_patients[4], alarms_alarmed_patients[5],
					alarms_alarmed_patients[6], alarms_alarmed_patients[7], alarms_alarmed_patients[8], alarms_alarmed_patients[9], alarms_alarmed_patients[10], alarms_alarmed_patients[11], alarms_alarmed_patients[12], alarms_alarmed_patients[13],
					alarms_alarmed_patients[14], alarms_alarmed_patients[15], alarms_alarmed_patients[16], alarms_alarmed_patients[17], alarms_alarmed_patients[18], alarms_alarmed_patients[19], alarms_alarmed_patients[20],
					alarms_alarmed_patients[21], alarms_alarmed_patients[22], alarms_alarmed_patients[23], total, average)
				day_json.append(row)

				total = sum(max_alarms)
				average = round(d(total, len(max_alarms)), 2)
				row = make_row(ALARM_MAX_ALARMS, date, max_alarms[0], max_alarms[1], max_alarms[2], max_alarms[3], max_alarms[4], max_alarms[5],
					max_alarms[6], max_alarms[7], max_alarms[8], max_alarms[9], max_alarms[10], max_alarms[11], max_alarms[12], max_alarms[13],
					max_alarms[14], max_alarms[15], max_alarms[16], max_alarms[17], max_alarms[18], max_alarms[19], max_alarms[20],
					max_alarms[21], max_alarms[22], max_alarms[23], total, average)
				day_json.append(row)

				total = sum(min_alarms)
				average = round(d(total, len(min_alarms)), 2)
				row = make_row(ALARM_MIN_ALARMS, date, min_alarms[0], min_alarms[1], min_alarms[2], min_alarms[3], min_alarms[4], min_alarms[5],
					min_alarms[6], min_alarms[7], min_alarms[8], min_alarms[9], min_alarms[10], min_alarms[11], min_alarms[12], min_alarms[13],
					min_alarms[14], min_alarms[15], min_alarms[16], min_alarms[17], min_alarms[18], min_alarms[19], min_alarms[20],
					min_alarms[21], min_alarms[22], min_alarms[23], total, average)
				day_json.append(row)

				total = sum(alarms_top)
				average = round(d(total, len(alarms_top)), 2)
				row = make_row(ALARM_AVG_ALARMS_TOP, date, alarms_top[0], alarms_top[1], alarms_top[2], alarms_top[3], alarms_top[4], alarms_top[5],
					alarms_top[6], alarms_top[7], alarms_top[8], alarms_top[9], alarms_top[10], alarms_top[11], alarms_top[12], alarms_top[13],
					alarms_top[14], alarms_top[15], alarms_top[16], alarms_top[17], alarms_top[18], alarms_top[19], alarms_top[20],
					alarms_top[21], alarms_top[22], alarms_top[23], total, average)
				day_json.append(row)

				total = sum(alarms_mid)
				average = round(d(total, len(alarms_mid)), 2)
				row = make_row(ALARM_AVG_ALARMS_MID, date, alarms_mid[0], alarms_mid[1], alarms_mid[2], alarms_mid[3], alarms_mid[4], alarms_mid[5],
					alarms_mid[6], alarms_mid[7], alarms_mid[8], alarms_mid[9], alarms_mid[10], alarms_mid[11], alarms_mid[12], alarms_mid[13],
					alarms_mid[14], alarms_mid[15], alarms_mid[16], alarms_mid[17], alarms_mid[18], alarms_mid[19], alarms_mid[20],
					alarms_mid[21], alarms_mid[22], alarms_mid[23], total, average)
				day_json.append(row)

				total = sum(alarms_low)
				average = round(d(total, len(alarms_low)), 2)
				row = make_row(ALARM_AVG_ALARMS_LOW, date, alarms_low[0], alarms_low[1], alarms_low[2], alarms_low[3], alarms_low[4], alarms_low[5],
					alarms_low[6], alarms_low[7], alarms_low[8], alarms_low[9], alarms_low[10], alarms_low[11], alarms_low[12], alarms_low[13],
					alarms_low[14], alarms_low[15], alarms_low[16], alarms_low[17], alarms_low[18], alarms_low[19], alarms_low[20],
					alarms_low[21], alarms_low[22], alarms_low[23], total, average)
				day_json.append(row)

				total = sum(minutes_alarmed_patients)
				average = round(d(total, len(minutes_alarmed_patients)), 2)
				row = make_row(ALARM_MINUTES_ALARMED_PATIENTS, date, minutes_alarmed_patients[0], minutes_alarmed_patients[1], minutes_alarmed_patients[2], minutes_alarmed_patients[3], minutes_alarmed_patients[4], minutes_alarmed_patients[5],
					minutes_alarmed_patients[6], minutes_alarmed_patients[7], minutes_alarmed_patients[8], minutes_alarmed_patients[9], minutes_alarmed_patients[10], minutes_alarmed_patients[11], minutes_alarmed_patients[12], minutes_alarmed_patients[13],
					minutes_alarmed_patients[14], minutes_alarmed_patients[15], minutes_alarmed_patients[16], minutes_alarmed_patients[17], minutes_alarmed_patients[18], minutes_alarmed_patients[19], minutes_alarmed_patients[20],
					minutes_alarmed_patients[21], minutes_alarmed_patients[22], minutes_alarmed_patients[23], total, average)
				day_json.append(row)

				total = sum(max_minutes)
				average = round(d(total, len(max_minutes)), 2)
				row = make_row(ALARM_MAX_MINUTES, date, max_minutes[0], max_minutes[1], max_minutes[2], max_minutes[3], max_minutes[4], max_minutes[5],
					max_minutes[6], max_minutes[7], max_minutes[8], max_minutes[9], max_minutes[10], max_minutes[11], max_minutes[12], max_minutes[13],
					max_minutes[14], max_minutes[15], max_minutes[16], max_minutes[17], max_minutes[18], max_minutes[19], max_minutes[20],
					max_minutes[21], max_minutes[22], max_minutes[23], total, average)
				day_json.append(row)

				total = sum(min_minutes)
				average = round(d(total, len(min_minutes)), 2)
				row = make_row(ALARM_MIN_MINUTES, date, min_minutes[0], min_minutes[1], min_minutes[2], min_minutes[3], min_minutes[4], min_minutes[5],
					min_minutes[6], min_minutes[7], min_minutes[8], min_minutes[9], min_minutes[10], min_minutes[11], min_minutes[12], min_minutes[13],
					min_minutes[14], min_minutes[15], min_minutes[16], min_minutes[17], min_minutes[18], min_minutes[19], min_minutes[20],
					min_minutes[21], min_minutes[22], min_minutes[23], total, average)
				day_json.append(row)

				total = sum(minutes_top)
				average = round(d(total, len(minutes_top)), 2)
				row = make_row(ALARM_AVG_ALARMS_TOP, date, minutes_top[0], minutes_top[1], minutes_top[2], minutes_top[3], minutes_top[4], minutes_top[5],
					minutes_top[6], minutes_top[7], minutes_top[8], minutes_top[9], minutes_top[10], minutes_top[11], minutes_top[12], minutes_top[13],
					minutes_top[14], minutes_top[15], minutes_top[16], minutes_top[17], minutes_top[18], minutes_top[19], minutes_top[20],
					minutes_top[21], minutes_top[22], minutes_top[23], total, average)
				day_json.append(row)

				total = sum(minutes_mid)
				average = round(d(total, len(minutes_mid)), 2)
				row = make_row(ALARM_AVG_ALARMS_MID, date, minutes_mid[0], minutes_mid[1], minutes_mid[2], minutes_mid[3], minutes_mid[4], minutes_mid[5],
					minutes_mid[6], minutes_mid[7], minutes_mid[8], minutes_mid[9], minutes_mid[10], minutes_mid[11], minutes_mid[12], minutes_mid[13],
					minutes_mid[14], minutes_mid[15], minutes_mid[16], minutes_mid[17], minutes_mid[18], minutes_mid[19], minutes_mid[20],
					minutes_mid[21], minutes_mid[22], minutes_mid[23], total, average)
				day_json.append(row)

				total = sum(minutes_low)
				average = round(d(total, len(minutes_low)), 2)
				row = make_row(ALARM_AVG_ALARMS_LOW, date, minutes_low[0], minutes_low[1], minutes_low[2], minutes_low[3], minutes_low[4], minutes_low[5],
					minutes_low[6], minutes_low[7], minutes_low[8], minutes_low[9], minutes_low[10], minutes_low[11], minutes_low[12], minutes_low[13],
					minutes_low[14], minutes_low[15], minutes_low[16], minutes_low[17], minutes_low[18], minutes_low[19], minutes_low[20],
					minutes_low[21], minutes_low[22], minutes_low[23], total, average)
				day_json.append(row)
			else:
				date = dt.date().strftime('%Y-%m-%d')
				active_patients = [0] * 24
				for i in range(0, 24):
					active = [x.number_active for x in patients_active if x.hour == i and x.date == dt.date()]
					if active:
						active_patients[i] = sum(active)
				if active:
					total = sum(active_patients)
					average = round(d(sum(active_patients),len(active_patients)), 2)
				else:
					total = 0
					average = 0

				row = make_row(ALARM_ALARMS, date)
				day_json.append(row)
				row = make_row(ALARM_MINUTES_ALARMING, date)
				day_json.append(row)
				row = make_row(ALARM_MINUTES_ALARMS, date)
				day_json.append(row)
				row = make_row(ACTIVE_PATIENTS, date, active_patients[0], active_patients[1], active_patients[2], active_patients[3], active_patients[4], active_patients[5], active_patients[6], active_patients[7],
				active_patients[8], active_patients[9], active_patients[10], active_patients[11], active_patients[12], active_patients[13], active_patients[14], active_patients[15], active_patients[16], active_patients[17],
				active_patients[18], active_patients[19], active_patients[20], active_patients[21], active_patients[22], active_patients[23], total, average)
				day_json.append(row)
				row = make_row(ALARM_ALARMED_PATIENTS, date)
				day_json.append(row)
				row = make_row(ALARM_ALARMED_ACTIVE, date)
				day_json.append(row)
				row = make_row(ALARM_ALARMS_ALARMED, date)
				day_json.append(row)
				row = make_row(ALARM_MAX_ALARMS, date)
				day_json.append(row)
				row = make_row(ALARM_MIN_ALARMS, date)
				day_json.append(row)
				row = make_row(ALARM_AVG_ALARMS_TOP, date)
				day_json.append(row)
				row = make_row(ALARM_AVG_ALARMS_MID, date)
				day_json.append(row)
				row = make_row(ALARM_AVG_ALARMS_LOW, date)
				day_json.append(row)
				row = make_row(ALARM_MINUTES_ALARMED_PATIENTS, date)
				day_json.append(row)
				row = make_row(ALARM_MAX_MINUTES, date)
				day_json.append(row)
				row = make_row(ALARM_MIN_MINUTES, date)
				day_json.append(row)
				row = make_row(ALARM_AVG_MINUTES_TOP, date)
				day_json.append(row)
				row = make_row(ALARM_AVG_MINUTES_MID, date)
				day_json.append(row)
				row = make_row(ALARM_AVG_MINUTES_LOW, date)
				day_json.append(row)

			#print json.dumps(day_json)

			write_record(day_json, dt.date(), medical_record_number, unit_floor, all)


def make_row(description, date, hour0=0, hour1=0, hour2=0, hour3=0, hour4=0, hour5=0, hour6=0, hour7=0, hour8=0, hour9=0, hour10=0,
hour11=0, hour12=0, hour13=0, hour14=0, hour15=0, hour16=0, hour17=0, hour18=0, hour19=0, hour20=0, hour21=0, hour22=0, hour23=0,
total=0, average=0):
	row = {'description': description, 'date' : date, 'hour0' : hour0, 'hour1' : hour1, 'hour2' : hour2, 'hour3' : hour3, 'hour4' : hour4, 
		'hour5' : hour5, 'hour6' : hour6, 'hour7' : hour7, 'hour8' : hour8, 'hour9' : hour9, 'hour10' : hour10, 'hour11' : hour11, 
		'hour12' : hour12, 'hour13' : hour13, 'hour14' : hour14, 'hour15' : hour15, 'hour16' : hour16, 'hour17' : hour17, 
		'hour18' : hour18, 'hour19' : hour19, 'hour20' : hour20, 'hour21' : hour21, 'hour22' : hour22, 'hour23' : hour23, 'total' : total, 
		'daily_average' : average}
	return row

def write_record(data, date, medical_record_number=None, unit_floor=None, all=None):
	data = json.dumps(data)
	data = data[1:]
	data = data[:-1]
	r = DBAlarmResponseReportData(date, data, pa_id=medical_record_number, unit_floor=unit_floor, all=all)
	db.session.add(r)



def d(x, y):
	return float(x)/float(y)

def get_patients_active_patient(medical_record_number, start, end):
	response = []
	p = DBPatient.query.filter_by(medical_record_number=medical_record_number).first()
	if p:
		a = DBPatientActivation.query.filter(DBPatientActivation.patient_id==p.id, DBPatientActivation.occurred < start,
			DBPatientActivation.status.in_(['Activated', 'Reactivated'])).order_by(DBPatientActivation.occurred.desc()).first()
		if a:
			i = DBPatientActivation.query.filter(DBPatientActivation.patient_id==p.id, DBPatientActivation.occurred > start,
				DBPatientActivation.occurred < end, DBPatientActivation.status=='Inactivated').first()
			if i:
				response = []
				for dt in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
					for h in range(0,24):
						if dt.date() <= i.occurred.date() and h <= i.occurred.hour:
							response.append(as_object({'date': dt.date(), 'hour': h, 'number_active' : 1}))
						else:
							response.append(as_object({'date': dt.date(), 'hour': h, 'number_active' : 0}))

			else:
				response = []
				for dt in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
					for h in range(0,24):
						response.append(as_object({'date': dt.date(), 'hour': h, 'number_active' : 1}))
		a = DBPatientActivation.query.filter(DBPatientActivation.patient_id==p.id, DBPatientActivation.occurred > start,
			DBPatientActivation.status.in_(['Activated', 'Reactivated'])).order_by(DBPatientActivation.occurred.desc()).first()
		if a:
			i = DBPatientActivation.query.filter(DBPatientActivation.patient_id==p.id, DBPatientActivation.occurred > a.occurred,
				DBPatientActivation.occurred < end, DBPatientActivation.status=='Inactivated').first()
			if i:
				response = []
				for dt in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
					for h in range(0,24):
						if dt.date() >= a.occurred.date() and h >= a.occurred.hour and dt.date() <= i.occurred.date() and h <= i.occurred.hour:
							response.append(as_object({'date': dt.date(), 'hour': h, 'number_active' : 1}))
						else:
							response.append(as_object({'date': dt.date(), 'hour': h, 'number_active' : 0}))
			else:
				response = []
				for dt in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
					for h in range(0,24):
						if dt.date() >= a.occurred.date() and h >= a.occurred.hour:
							response.append(as_object({'date': dt.date(), 'hour': h, 'number_active' : 1}))
						else:
							response.append(as_object({'date': dt.date(), 'hour': h, 'number_active' : 0}))
		else:
			response = []
			for dt in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
				for h in range(0,24):
					response.append(as_object({'date': dt.date(), 'hour': h, 'number_active' : 0}))



	return response

class as_object(object):
	def __init__(self, d):
		self.__dict__ = d



run()