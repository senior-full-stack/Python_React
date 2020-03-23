from dm_app.app import db
from dm_app.models import *
from pprint import pprint
from dm_app.objects.event import Event
from dm_app.globs import *
from dm_app import *
from dateutil import rrule
from dateutil import tz
from dm_app.rfc3339 import utcformysqlfromtimestamp, nowtimestamp

es = DBEvent.query.filter_by(unit_floor=None).all()
print len(es)
c = 0
for e in es:
	if e.range_start:
		ph = DBPatientHistory.query.filter(DBPatientHistory.medical_record_number == e.medical_record_number, 
			DBPatientHistory.date_of_record < e.range_start).order_by(DBPatientHistory.date_of_record.desc()).first()
		if ph:
			e.unit_floor = ph.unit_floor
			c += 1
	if e.instance:
		ph = DBPatientHistory.query.filter(DBPatientHistory.medical_record_number == e.medical_record_number, 
			DBPatientHistory.date_of_record < e.instance).order_by(DBPatientHistory.date_of_record.desc()).first()
		if ph:
			e.unit_floor = ph.unit_floor
			c += 1

print c
db.session.commit()