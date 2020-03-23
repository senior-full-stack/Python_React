from dm_app import *
from ..models import *
from ..utils import log, validate_jwt_user_token, profiled
from ..globs import *
from ..rfc3339 import datetimetostr
import copy

class StatusApp(Resource):
	#@validate_jwt_user_token
	@swagger.operation(
		notes='none',
		responseClass=DBBodyLocation.__name__,
		nickname='get status station data',
		responseMessages=[
			{
				"code": 200,
				"message": "An array of status station data"
			},
			{
				"code": 404,
				"message": "No status station data found"
			}
		  ]
		)
	def get(self, user=None, sub=None, role=None):
		response = None
		status_code = status.HTTP_404_NOT_FOUND
		try:
			patients = {}

			e = DBEvent.query.join(DBBodyLocation, DBBodyLocation.id == DBEvent.body_location_id).join(
			DBDevice, DBDevice.id == DBEvent.device_id).join(DBPatient, 
			DBPatient.id == DBDevice.patient_id).filter(DBEvent.instance == None, DBEvent.range_end == None, 
			DBEvent.latest != None, DBDevice.last_seen > (datetime.utcnow() - timedelta(seconds=ALERT_INTERVAL_SECONDS)), DBDevice.patient_id != None, 
			DBBodyLocation.sensor_serial != SENSOR_UNASSIGNED, DBPatient.deleted == False, DBEvent.message != SENSOR_REMOVED,
			DBPatient.medical_record_number == DBEvent.medical_record_number).add_columns(
			DBPatient.unit_floor, DBPatient.name, DBPatient.medical_record_number, DBBodyLocation.battery, DBPatient.room).all()
			if e:
				for v in e:
					if not v.medical_record_number in patients:
						patients[v.medical_record_number] = {}
						patients[v.medical_record_number]['events'] = []
					patients[v.medical_record_number]['unit_floor'] = v.unit_floor
					patients[v.medical_record_number]['name'] = deidentify(v.name)
					patients[v.medical_record_number]['online'] = True
					patients[v.medical_record_number]['room'] = v.room
					v[0].battery = v.battery
					if 'events' in patients[v.medical_record_number] and \
					len(filter(lambda event: event['id'] == v[0].id, patients[v.medical_record_number]['events'])) == 0:
						patients[v.medical_record_number]['events'].append(StatusEventJsonSerializer().serialize(v[0]))


			ps = DBPatient.query.join(DBDevice).filter(DBDevice.patient_id != None, DBDevice.last_seen < 
				(datetime.utcnow() - timedelta(seconds=ALERT_INTERVAL_SECONDS))).add_columns(DBDevice.last_seen).all()

			for p, last_seen in ps:
				if not p.medical_record_number in patients:
					patients[p.medical_record_number] = {}
					patients[p.medical_record_number]['events'] = []
				patients[p.medical_record_number]['unit_floor'] = p.unit_floor
				patients[p.medical_record_number]['name'] = deidentify(p.name)
				patients[p.medical_record_number]['online'] = False
				patients[p.medical_record_number]['last_online'] = datetimetostr(last_seen)
				patients[p.medical_record_number]['room'] = p.room

			for p in patients:
				if patients[p]['online'] == True:
					unplugged = DBEvent.query.filter(DBEvent.medical_record_number == p, DBEvent.message.in_(['DEVICE IS PLUGGED INTO POWER', 
						'DEVICE IS UNPLUGGED FROM POWER'])).order_by(DBEvent.instance.desc(), DBEvent.message).first()
					if unplugged and unplugged.message.upper() == 'DEVICE IS UNPLUGGED FROM POWER':
						patients[p]['unplugged'] = True
						patients[p]['unplugged_time'] = datetimetostr(unplugged.instance)
					else:
						patients[p]['unplugged'] = False
				else:
					patients[p]['unplugged'] = False

			response = patients
			response = {'patients' : response }
			status_code = status.HTTP_200_OK

		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		log(request.remote_addr, request.path, request.method, request.args, status_code, user=user, device=None)
		return response, status_code

def deidentify(name):
	pieces = name.split()
	string = ''
	for p in pieces:
		string += p[:3]
	return string
