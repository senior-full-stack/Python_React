from dm_app.app import db
from dm_app.models import *
from pprint import pprint
from dm_app.objects.event import Event
from dm_app.globs import *
from dm_app import *
from dateutil import rrule
from dateutil import tz
from dm_app.rfc3339 import now

def convert_date_to_tz(date):
	if USE_TIMEZONE:
		to_zone = tz.gettz(TIMEZONE)
		from_zone = tz.gettz('UTC')
		utc = date.replace(tzinfo=from_zone)
		converted_date = utc.astimezone(to_zone).replace(tzinfo=None)
	else:
		converted_date = date
	return converted_date

ps = DBPatient.query.all()
until = convert_date_to_tz(now())
print len(ps)
c = 0
for p in ps:
	c += 1
	print c
	if p.unit_floor and p.deleted == False:
		stop = False
		search_date = None

		a = DBPatientActivation.query.filter(DBPatientActivation.patient_id == p.id, 
			DBPatientActivation.status.in_(['Activated', 'Reactivated'])).order_by(DBPatientActivation.occurred).first()
		if a:
			d = DBPatientActivation.query.filter(DBPatientActivation.patient_id == p.id, DBPatientActivation.status == 'Inactivated', 
				DBPatientActivation.occurred > a.occurred).first()
			if d:
				search_date = d.occurred
				start_date = convert_date_to_tz(a.occurred)
				end_date = convert_date_to_tz(d.occurred)
				for dt in rrule.rrule(rrule.HOURLY, dtstart=start_date.replace(minute=0, second=0, microsecond=0), until=end_date):
					po = DBPatientsActive.query.filter_by(date=dt.date(), hour=dt.hour, unit_floor=p.unit_floor).first()
					if po:
						po.number_active += 1
						db.session.merge(po)
					else:
						po = DBPatientsActive(dt.date(), dt.hour, p.unit_floor, 1)
						db.session.add(po)
			else:
				stop = True
				start_date = convert_date_to_tz(a.occurred)
				for dt in rrule.rrule(rrule.HOURLY, dtstart=start_date.replace(minute=0, second=0, microsecond=0), until=until):
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
					start_date = convert_date_to_tz(a.occurred)
					end_date = convert_date_to_tz(d.occurred)
					for dt in rrule.rrule(rrule.HOURLY, dtstart=start_date.replace(minute=0, second=0, microsecond=0), until=end_date):
						po = DBPatientsActive.query.filter_by(date=dt.date(), hour=dt.hour, unit_floor=p.unit_floor).first()
						if po:
							po.number_active += 1
							db.session.merge(po)
						else:
							po = DBPatientsActive(dt.date(), dt.hour, p.unit_floor, 1)
							db.session.add(po)
				else:
					stop = True
					start_date = convert_date_to_tz(a.occurred)
					for dt in rrule.rrule(rrule.HOURLY, dtstart=start_date.replace(minute=0, second=0, microsecond=0), until=until):
						po = DBPatientsActive.query.filter_by(date=dt.date(), hour=dt.hour, unit_floor=p.unit_floor).first()
						if po:
							po.number_active += 1
							db.session.merge(po)
						else:
							po = DBPatientsActive(dt.date(), dt.hour, p.unit_floor, 1)
							db.session.add(po)
			else:
				stop = True
db.session.commit()