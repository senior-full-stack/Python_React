from dateutil import rrule, tz
from datetime import datetime, time, timedelta
from ..globs import *
from ..models import *
from ..rfc3339 import now
from dm_app import *
import uwsgi
from uwsgidecorators import cron

def convert_date_to_tz(date):
	if USE_TIMEZONE:
		to_zone = tz.gettz(TIMEZONE)
		from_zone = tz.gettz('UTC')
		utc = date.replace(tzinfo=from_zone)
		converted_date = utc.astimezone(to_zone).replace(tzinfo=None)
	else:
		converted_date = date
	return converted_date

def convert_date_to_utc(date):
	if USE_TIMEZONE:
		to_zone = tz.gettz('UTC')
		from_zone = tz.gettz(TIMEZONE)
		utc = date.replace(tzinfo=from_zone)
		converted_date = utc.astimezone(to_zone).replace(tzinfo=None)
	else:
		converted_date = date
	return converted_date

@cron(0, -1, -1, -1, -1)
def populate_active_patients_hourly(signum):
	import datetime as dt
	l = DBPatientsActive.query.order_by(DBPatientsActive.date.desc(), DBPatientsActive.hour.desc()).first()
	if l:
		start_date = dt.datetime.combine(l.date, dt.time(hour=l.hour)) + dt.timedelta(hours=1)
		start_date_utc = convert_date_to_utc(start_date)
		until = convert_date_to_tz(now())
		if start_date_utc <= now().replace(tzinfo=None, minute=0, second=0, microsecond=0):
			ps = DBPatient.query.filter_by(deleted=False).all()
			c = 0
			for p in ps:
				c += 1
				print c
				stop = False
				search_date = None
				a = DBPatientActivation.query.filter(DBPatientActivation.patient_id == p.id, DBPatientActivation.occurred < start_date_utc, 
					DBPatientActivation.status.in_(['Activated', 'Reactivated'])).order_by(DBPatientActivation.occurred.desc()).first()
				if a:
					d = DBPatientActivation.query.filter(DBPatientActivation.patient_id == p.id, DBPatientActivation.status == 'Inactivated', 
						DBPatientActivation.occurred > a.occurred).first()
					if d:
						search_date = d.occurred
						a_occurred_converted = convert_date_to_tz(a.occurred)
						end_date = convert_date_to_tz(d.occurred)
						for dt in rrule.rrule(rrule.HOURLY, dtstart=start_date, until=end_date):
							po = DBPatientsActive.query.filter_by(date=dt.date(), hour=dt.hour, unit_floor=p.unit_floor).first()
							if po:
								po.number_active += 1
								db.session.merge(po)
							else:
								po = DBPatientsActive(dt.date(), dt.hour, p.unit_floor, 1)
								db.session.add(po)
					else:
						stop = True
						for dt in rrule.rrule(rrule.HOURLY, dtstart=start_date, until=until):
							po = DBPatientsActive.query.filter_by(date=dt.date(), hour=dt.hour, unit_floor=p.unit_floor).first()
							if po:
								po.number_active += 1
								db.session.merge(po)
							else:
								po = DBPatientsActive(dt.date(), dt.hour, p.unit_floor, 1)
								db.session.add(po)
				else:
					stop = True

				while not stop:
					a = DBPatientActivation.query.filter(DBPatientActivation.patient_id == p.id, 
					DBPatientActivation.status.in_(['Activated', 'Reactivated']), DBPatientActivation.occurred > search_date).order_by(
					DBPatientActivation.occurred).first()

					if a:
						d = DBPatientActivation.query.filter(DBPatientActivation.patient_id == p.id, DBPatientActivation.status == 'Inactivated', 
							DBPatientActivation.occurred > a.occurred).first()
						if d:
							search_date = d.occurred
							a_occurred_converted = convert_date_to_tz(a.occurred.replace(minute=0, second=0, microsecond=0))
							if a_occurred_converted > start_date:
								new_start = a_occurred_converted
							else:
								new_start = start_date
							end_date = convert_date_to_tz(d.occurred)
							for dt in rrule.rrule(rrule.HOURLY, dtstart=new_start, until=end_date):
								pa = DBPatientsActive.query.filter_by(date=dt.date(), hour=dt.hour, unit_floor=p.unit_floor).first()
								if pa:
									pa.number_active += 1
									db.session.merge(po)
								else:
									pa = DBPatientsActive(dt.date(), dt.hour, p.unit_floor, 1)
									db.session.add(po)
						else:
							stop = True
							a_occurred_converted = convert_date_to_tz(a.occurred.replace(minute=0, second=0, microsecond=0))
							if a_occurred_converted > start_date:
								new_start = a_occurred_converted
							else:
								new_start = start_date
							for dt in rrule.rrule(rrule.HOURLY, dtstart=new_start, until=until):
								pa = DBPatientsActive.query.filter_by(date=dt.date(), hour=dt.hour, unit_floor=p.unit_floor).first()
								if po:
									pa.number_active += 1
									db.session.merge(po)
								else:
									pa = DBPatientsActive(dt.date(), dt.hour, p.unit_floor, 1)
									db.session.add(po)
					else:
						stop = True
		db.session.commit()


