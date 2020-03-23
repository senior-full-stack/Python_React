from dm_app.app import app, db
from dm_app.models import *
from dm_app.rfc3339 import nowtostr, now, strtotimestamp, nowtimestamp, utcformysqlfromtimestamp
from dm_app.utils import hash_pass
#db.drop_all()
#db.create_all()

#seed data
BODY_LOCATIONS = ['SKULL', 'UPPER_SPINE', 'SACRUM', 'LEFT_HIP', 'RIGHT_HIP', 'LEFT_ISCHIA', 'RIGHT_ISCHIA', 'LEFT_ELBOW',
'RIGHT_ELBOW', 'LEFT_HEEL', 'RIGHT_HEEL']

settings = DBGlobalDeviceSettings('2', 'voice', 'loud', 'en')
db.session.add(settings)

for location in BODY_LOCATIONS:
    default_location = DBGlobalLocationSettings(type='SWITCH_TYPE', JSID=location, alarm_clear_multiple=4, alarm_threshold_minutes=60, 
            pressure_state='NO_PRESSURE', wound_stage='', is_wound=False, has_previous_alert=False,
            site_assessment='', sensor_removal=None, wound_measurement='', existing_wound=False, wound_alarm_threshold_minutes=5,
             wound_alarm_clear_multiple=5, previous_alarm_threshold_hours=24)
    db.session.add(default_location)
    db.session.commit()

user = DBUser('Jon', hash_pass('pass'), 'klein1jonathan@gmail.com', '+18478454531', False, 'admin')
db.session.add(user)

matt_user = DBUser('Matt', hash_pass('mattrushesdemos'), 'mtrapani@gmail.com', '+18479244430', False, 'admin')
db.session.add(matt_user)

christina_user = DBUser('Christina Kim', hash_pass('changemetest'), 'ckim1910@gmail.com', '+17732407235', False, 'admin')
db.session.add(christina_user)

patient1 = DBPatient('1')
db.session.add(patient1)
db.session.commit()
patient1 = DBPatient.query.filter_by(medical_record_number='1').first()
for location in BODY_LOCATIONS:
    body_location = DBBodyLocation(patient1.id, location, medical_record_number=patient1.medical_record_number,
        sensor_serial=223344, distance='0.31999734', stopped=False, force_state=0, fast_blink=False, 
        type='SWITCH_TYPE', alarm_clear_multiple=1, alarm_threshold_minutes=1, battery=2880, binary_state=False, last_seen=utcformysqlfromtimestamp(nowtimestamp()),
        under_pressure_milliseconds=0, pressure_state='NO_PRESSURE', wound_stage='3', is_wound=True, has_previous_alert=False,
        site_assessment=None, sensor_removal=None, wound_measurement=None, wound_existing_since=utcformysqlfromtimestamp(nowtimestamp()),
        existing_wound=True)
    db.session.add(body_location)
db.session.commit()

patient2 = DBPatient('2')
db.session.add(patient2)
db.session.commit()
patient2 = DBPatient.query.filter_by(medical_record_number='2').first()
for location in BODY_LOCATIONS:
    body_location = DBBodyLocation(patient2.id, location, medical_record_number=patient2.medical_record_number,
        sensor_serial=223344, distance='0.31999734', stopped=False, force_state=0, fast_blink=False, 
        type='SWITCH_TYPE', alarm_clear_multiple=1, alarm_threshold_minutes=1, battery=2880, binary_state=False, last_seen=utcformysqlfromtimestamp(nowtimestamp()),
        under_pressure_milliseconds=0, pressure_state='NO_PRESSURE', wound_stage='3', is_wound=True, has_previous_alert=False,
        site_assessment=None, sensor_removal=None, wound_measurement=None, wound_existing_since=utcformysqlfromtimestamp(nowtimestamp()),
        existing_wound=True)
    db.session.add(body_location)
db.session.commit()

patient3 = DBPatient('3')
db.session.add(patient3)
db.session.commit()
patient3 = DBPatient.query.filter_by(medical_record_number='3').first()
for location in BODY_LOCATIONS:
    body_location = DBBodyLocation(patient3.id, location, medical_record_number=patient3.medical_record_number,
        sensor_serial=223344, distance='0.31999734', stopped=False, force_state=0, fast_blink=False, 
        type='SWITCH_TYPE', alarm_clear_multiple=1, alarm_threshold_minutes=1, battery=2880, binary_state=False, last_seen=utcformysqlfromtimestamp(nowtimestamp()),
        under_pressure_milliseconds=0, pressure_state='NO_PRESSURE', wound_stage='3', is_wound=True, has_previous_alert=False,
        site_assessment=None, sensor_removal=None, wound_measurement=None, wound_existing_since=utcformysqlfromtimestamp(nowtimestamp()),
        existing_wound=True)
    db.session.add(body_location)
db.session.commit()


device1 = DBDevice('148fbf9c01245354', 'A7B44B7D7AD3AE64E3FD085ED34935A7A5478D445867B7F03B074B7D73E7258A', '148fbf9c01245354', \
                    utcformysqlfromtimestamp(nowtimestamp()), 1, '2', 'voice', 'loud', 'en', patient1.medical_record_number)
db.session.add(device1)


device2 = DBDevice('622526eeff133663', 'A037911FD60A64BA7C1B37C84BC810B6A669EAF88C2DCB25A0894838C3857F7D', '622526eeff133663', \
                    utcformysqlfromtimestamp(nowtimestamp()), 2, '2', 'voice', 'loud', 'en', patient2.medical_record_number)
db.session.add(device2)

device3 = DBDevice('b6d9a086db0f330f', 'E4E1AE93A6AD5E7072B39AD2CB2AEBBB94F8BA32C55305C079F3F5A8FAD091FE', 'b6d9a086db0f330f', \
                    utcformysqlfromtimestamp(nowtimestamp()), 3, '2', 'voice', 'loud', 'en', patient3.medical_record_number)
db.session.add(device3)

db.session.commit()

device1 = DBDevice.query.filter_by(serial='148fbf9c01245354').first()
device2 = DBDevice.query.filter_by(serial='622526eeff133663').first()
device3 = DBDevice.query.filter_by(serial='b6d9a086db0f330f').first()

body_location1 = DBBodyLocation.query.filter_by(medical_record_number=patient1.medical_record_number, JSID='SKULL').first()
event1 = DBEvent(patient1.id, 'PRESSURE_ALARM', body_location1.id, patient1.medical_record_number, device1.id, None,
 utcformysqlfromtimestamp(nowtimestamp()), utcformysqlfromtimestamp(nowtimestamp()), 'SKULL')
db.session.add(event1)

body_location2 = DBBodyLocation.query.filter_by(medical_record_number=patient2.medical_record_number, JSID='SKULL').first()
event2 = DBEvent(patient2.id, 'PRESSURE_ALARM', body_location2.id, patient2.medical_record_number, device2.id, None,
 utcformysqlfromtimestamp(nowtimestamp()), utcformysqlfromtimestamp(nowtimestamp()), 'SKULL')
event3 = DBEvent(patient2.id, 'PRESSURE_ALARM', body_location2.id, patient2.medical_record_number, device2.id, None,
 utcformysqlfromtimestamp(nowtimestamp()), None, 'SKULL')
db.session.add(event2)
db.session.add(event3)

body_location3 = DBBodyLocation.query.filter_by(medical_record_number=patient3.medical_record_number, JSID='SKULL').first()
event3 = DBEvent(patient3.id, 'PRESSURE_ALARM', body_location3.id, patient3.medical_record_number, device3.id, None,
 utcformysqlfromtimestamp(nowtimestamp()), utcformysqlfromtimestamp(nowtimestamp()), 'SKULL')
db.session.add(event3)


db.session.commit()






