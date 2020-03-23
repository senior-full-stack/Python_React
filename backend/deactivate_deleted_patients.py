from dm_app.app import db
from dm_app.models import *
from pprint import pprint
from dm_app.objects.event import Event
from dm_app.globs import *
from dm_app import *
from dateutil import rrule
from dateutil import tz
from dm_app.rfc3339 import utcformysqlfromtimestamp, nowtimestamp

ps = DBPatient.query.filter_by(deleted=True).all()

for p in ps:
	a = DBPatientActivation.query.filter_by(patient_id=p.id).order_by(DBPatientActivation.occurred.desc()).first()
	if a: 
		if a.status == ACTIVATED_STATUS or a.status == REACTIVATED_STATUS:
			print p.name
			mrn = p.medical_record_number.split('deleted')[0]
			date = a.occurred

			ph = DBPatientHistory.query.filter_by(medical_record_number=mrn).order_by(DBPatientHistory.date_of_record).first()

			if ph and ph.date_of_record > date:
				date = ph.date_of_record

			eh = DBEventHistory.query.filter_by(medical_record_number=mrn).order_by(DBEventHistory.occurred.desc()).first()

			if eh and eh.occurred > date:
				date = eh.occurred

			date += timedelta(seconds=1)

			activation = DBPatientActivation(p.id, INACTIVATED_STATUS, date, INACTIVATED_REASON_DELETED, 
							utcformysqlfromtimestamp(nowtimestamp()), False, INACTIVATED_REASON_DELETED, None)
			db.session.add(activation)
			db.session.commit()