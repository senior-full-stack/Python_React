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

jesus_user = DBUser('Jesus Flores', hash_pass('pasuccess1'), 'jflores@digitalhealths.com', '+8473289540', False, 'admin', deleted=False)
db.session.add(jesus_user)

ad = DBAdminDefault('["1"]', 15)
db.session.add(ad)

db.session.commit()