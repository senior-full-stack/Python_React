from dm_app.app import *
from dm_app.models import *
from pprint import pprint
from dm_app.globs import *
from dm_app.rfc3339 import utctotimestamp, utcformysqlfromtimestamp
from dm_app.actions.alert import Alert
from dm_app.objects.event import Event
from dm_app.utils import *


ds = DBDevice.query.filter(DBDevice.patient_id != None, DBDevice.last_seen < (datetime.utcnow() - timedelta(seconds=ALERT_INTERVAL_SECONDS * 3))).all()
c = 0
struct_logger.msg(instance=LOGGING_INSTANCE, message='checking for offline devices')
for d in ds:
	e = DBEvent.query.filter(DBEvent.device_id == d.id, DBEvent.patient_id == d.patient_id, DBEvent.message == 'DEVICE OFFLINE', 
		DBEvent.instance == d.last_seen + timedelta(seconds=ALERT_INTERVAL_SECONDS)).first()
	if not e:
		p = DBPatient.query.filter_by(id=d.patient_id).first()
		if p:
			try:
				subject = '%s: Room %s, device offline' % (FACILITY, p.room)
				message = 'Device %s went offline at %s' % (d.serial, str(Event().convert_date_to_tz(utcformysqlfromtimestamp(utctotimestamp(d.last_seen + timedelta(seconds=ALERT_INTERVAL_SECONDS))))))
				Alert().email_admins(DEVICE_OFFLINE, message, subject)
			except Exception as e:
				struct_logger.error(instance=LOGGING_INSTANCE, method='Offline Device', exception=e.message)
			
			event = {}
			event['medical_record_number'] = p.medical_record_number
			event['unit_floor'] = p.unit_floor
			event['patient_id'] = p.id
			event['device_id'] = d.id
			event['instance'] = utcformysqlfromtimestamp(utctotimestamp(d.last_seen + timedelta(seconds=ALERT_INTERVAL_SECONDS)))
			event['message'] = 'DEVICE OFFLINE'
			e = DBEvent(**event)
			db.session.add(e)

			event_history = {}
			event_history['medical_record_number'] = p.medical_record_number
			event_history['unit_floor'] = p.unit_floor
			event_history['event_type'] = EVENT_HISTORY_DICT['DEVICE OFFLINE']
			event_history['occurred'] = utcformysqlfromtimestamp(utctotimestamp(d.last_seen + timedelta(seconds=ALERT_INTERVAL_SECONDS)))
			eh = DBEventHistory(**event_history)
			db.session.add(eh)
		c += 1

db.session.commit()

struct_logger.msg(instance=LOGGING_INSTANCE, message='%s offline device events written' % (c))
