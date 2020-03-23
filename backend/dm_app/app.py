from dm_app import *
from models import *
from actions.alert import Alert
from actions.change_password import ChangePassword
from actions.deactivate import Deactivate
from actions.download_token import DownloadToken
from actions.health import Health
from actions.login import Login
from actions.patient_assign_device import PatientAssignDevice
from actions.sync import Sync
from actions.unassign_device import UnassignDevice
from actions.unassign_patient import UnassignPatient
from actions.user_assign_patient import UserAssignPatient

from objects.admin import Admin
from objects.body_location import BodyLocation
from objects.default_sync import DefaultSync
from objects.device import Device
from objects.event import Event
from objects.global_device_settings import GlobalDeviceSettings
from objects.global_location_settings import GlobalLocationSettings
from objects.outcome import Outcome
from objects.patient import Patient
from objects.patient_note import PatientNote
from objects.status_app import StatusApp
from objects.status_station import StatusStation
from objects.timeline import TimeLine
from objects.user import User

from reports.alarm_response_report import AlarmResponseReport
from reports.body_location_history_report import BodyLocationHistoryReport
from reports.event_report import EventReport
from reports.patient_info_report import PatientInfoReport
from reports.pu_status_report import PUStatusReport
from reports.reposition_report import RepositionReport

try:
    import jobs.process_large_requests
except Exception as e:
    print "large request job import failed"
    print e.message
    pass

try:
    import jobs.create_offline_device_events
except Exception as e:
    print "offline device job import failed"
    print e.message
    pass

try:
    import jobs.populate_active_patients_hourly
except Exception as e:
    print "populate active patients job import failed"
    print e.message
    pass

try:
    import jobs.populate_report_data_daily
except Exception as e:
    print "populate report data job import failed"
    print e.message
    pass

import ujson


class Role(Resource):
    def get(self):
        return { 'Roles': [ { 'Name': 'Admin', 'Access': 'All'} ] }

''' MAPPINGS '''

app.url_map.strict_slashes = False
api.add_resource(Admin, '/admin/')
api.add_resource(AlarmResponseReport, '/alarmresponsereports/<medical_record_number>', '/alawhrmresponsereports')
api.add_resource(Alert, '/alerts')
api.add_resource(BodyLocation, '/patients/<medical_record_number>/bodylocations/<location>/', '/patients/<medical_record_number>/bodylocations/')
api.add_resource(BodyLocationHistoryReport, '/bodylocationhistoryreports/<medical_record_number>', '/bodylocationhistoryreports')
api.add_resource(ChangePassword, '/users/<email>/password/')
api.add_resource(Deactivate, '/deactivate/<medical_record_number>/')
api.add_resource(DefaultSync, '/default/sync/')
api.add_resource(DownloadToken, '/download-token/')
api.add_resource(Device, '/devices/<serial>/', '/devices')
api.add_resource(Event, '/events', '/events/<event>')
api.add_resource(EventReport, '/eventreports/<medical_record_number>', '/eventreports')
api.add_resource(GlobalDeviceSettings, '/default/devices/settings')
api.add_resource(GlobalLocationSettings, '/default/bodylocations/<location>/')
api.add_resource(Health, '/health')
api.add_resource(Login, '/api/v1/users/login')
api.add_resource(Patient, '/patients/<medical_record_number>', '/patients')
api.add_resource(PatientAssignDevice, '/patients/<medical_record_number>/assign/<serial>')
api.add_resource(PatientInfoReport, '/patientinforeports/<medical_record_number>', '/patientinforeports')
api.add_resource(PatientNote, '/patientnotes/<pa_id>/<patient_site>/', '/patientnotes/<pa_id>/', '/patientnotes/')
api.add_resource(PUStatusReport, '/pustatusreports/<medical_record_number>', '/pustatusreports')
api.add_resource(RepositionReport, '/repositionreports/<medical_record_number>', '/repositionreports')
api.add_resource(Role, '/roles')
api.add_resource(StatusApp, '/status-app')
api.add_resource(StatusStation, '/status-station')
api.add_resource(TimeLine, '/timelines')
api.add_resource(Sync, '/devices/sync')
api.add_resource(UnassignDevice, '/devices/<serial>/unassign/')
api.add_resource(UnassignPatient, '/patients/<medical_record_number>/unassign/')
api.add_resource(User, '/users/<email>', '/users')
api.add_resource(UserAssignPatient, '/users/<email>/patients/<medical_record_number>')
#print app.url_map



def main():
    set_secret()
    app.run()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5666)

@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(ujson.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp

