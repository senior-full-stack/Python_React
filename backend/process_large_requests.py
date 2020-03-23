from dm_app.app import *
from dm_app import db, struct_logger, LOGGING_INSTANCE
from dm_app.models import *
from dm_app.globs import *
from dm_app.objects.event import Event
from dm_app.rfc3339 import utctotimestamp, utcformysqlfromtimestamp
import json

def process_event_post(large_request):
	p = DBPatient.query.filter_by(id=large_request.patient_id).first()
	data = json.loads(large_request.request)
	data['pressure_events'] = sorted(data['pressure_events'], key=lambda x: x['epoch_timestamp'], reverse=False)
	for event in data['pressure_events']:
		Event().process_event(event, p.medical_record_number, p.unit_floor, p.id, large_request.device_id)
	db.session.delete(large_request)
	db.session.commit()

#@timer(5, target='mule')
#def check_table(signum):
struct_logger.msg(instance=LOGGING_INSTANCE, message='checking for queued requests')
lr = DBLargeRequest.query.filter_by(processing=False, error=None).order_by(DBLargeRequest.occurred).first()

if lr:
	try:
		lr_id = lr.id
		struct_logger.msg(instance=LOGGING_INSTANCE, message='processing request: ' + str(lr_id))
		lr.processing=True
		db.session.commit()
		lr = DBLargeRequest.query.filter_by(id=lr_id).one()
		if lr.request_class == 'event' and lr.request_action == 'post':
			process_event_post(lr)
	except Exception as e:
		struct_logger.msg(instance=LOGGING_INSTANCE, message='job error: ' + str(e.message))
		lr.error = e.message
		db.session.commit()