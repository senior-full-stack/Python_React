
#csv
global CSV
CSV = 'csv'
global CSV_HEADERS
CSV_HEADERS = {
    'Content-Disposition' : 'attachment; filename=export.csv',
    'Content-type' : 'text/csv'
}

global MAX_CONTENT_LENGTH
MAX_CONTENT_LENGTH = 500

#twilio
global TWILIO_PHONE_NUMBER
TWILIO_PHONE_NUMBER = '+17085807324'
global TWILIO_SID
TWILIO_SID = 'AC822e386c4876d8b960c7068fb3c0caf7'
global TWILIO_AUTH_TOKEN
TWILIO_AUTH_TOKEN = '11da82efd25c53523c7d118d2bbcf4d7'

#alert types
global DEVICE_UNPLUGGED
DEVICE_UNPLUGGED = 'DEVICE_UNPLUGGED'
global DEVICE_PLUGGED_IN
DEVICE_PLUGGED_IN = 'DEVICE_PLUGGED_IN'
global DEVICE_OFFLINE
DEVICE_OFFLINE = 'DEVICE_OFFLINE'
global DEVICE_ONLINE
DEVICE_ONLINE = 'DEVICE_ONLINE'

#roles
global CAREGIVER
CAREGIVER = 'caregiver'
global ADMIN
ADMIN = 'admin'
global PATIENT
PATIENT = 'PATIENT'

#device headers
global DEVICE_ID_HEADER
DEVICE_ID_HEADER = 'X-PAS-ANDROID-DEVICE-ID'
global ANDROID_VERSION_HEADER
ANDROID_VERSION_HEADER = 'X-PAS-ANDROID-VERSION'

#locations and events
global BODY_LOCATIONS
BODY_LOCATIONS = ['SKULL', 'UPPER_SPINE', 'SACRUM', 'LEFT_HIP', 'RIGHT_HIP', 'LEFT_ISCHIA', 'RIGHT_ISCHIA', 'LEFT_ELBOW',
'RIGHT_ELBOW', 'LEFT_HEEL', 'RIGHT_HEEL']

global EVENT_TYPE_RANGE
EVENT_TYPE_RANGE = ['SENSOR_STOPPED', 'NO_PRESSURE', 'PRESSURE_RISING', 'PRESSURE_ALARM',
                    'PRESSURE_FALLING', 'PRESSURE_RECURRING', 'RECENT_PRESSURE', 'INACTIVE_FOR_24H']

global EVENT_TYPE_SINGLE_POINT
EVENT_TYPE_SINGLE_POINT = ['PATIENT WAS TURNED BY CAREGIVER', 'MONITORING WAS PAUSED',
    'MONITORING WAS RESUMED', 'DEVICE OFFLINE', 'DEVICE ONLINE', 'APP WAS STARTED', 'DEVICE IS PLUGGED INTO POWER',
    'DEVICE IS UNPLUGGED FROM POWER', 'SENSOR CHANGED', 'SENSOR WENT OFFLINE', 'SENSOR CAME ONLINE']

global EVENT_HISTORY_DICT
EVENT_HISTORY_DICT = {'NO_PRESSURE': 'No Pressure', 'PRESSURE_RISING': 'Pressure rising',
                      'PRESSURE_ALARM': 'Pressure Alarm', 'PRESSURE_FALLING': 'Pressure falling',
                      'PRESSURE_RECURRING': 'Pressure recurring after alarm',
                      'RECENT_PRESSURE': 'Pressure stopped rising', 'SENSOR_STOPPED': 'Sensor Stopped',
                      'MONITORING WAS PAUSED': 'Monitoring was paused',
                      'PATIENT WAS TURNED BY CAREGIVER': 'Caregiver Rotated Patient',
                      'MONITORING WAS RESUMED': 'Monitoring was resumed',
                      'SENSOR_REMOVED': 'Sensor Removed', 'DEVICE OFFLINE': 'Device went offline',
                      'DEVICE ONLINE': 'Device online',
                      'APP WAS STARTED': 'Application Started',
                      'DEVICE IS PLUGGED INTO POWER': 'Device is plugged into power',
                      'DEVICE IS UNPLUGGED FROM POWER': 'Device is unplugged from power',
                      'SENSOR CHANGED': 'Sensor Changed',
                      'SENSOR WENT OFFLINE': 'Sensor went offline', 'SENSOR CAME ONLINE': 'Sensor came online',
                      'INACTIVE_FOR_24H': 'Sensor stayed inactive for more than 24h'}

#strings
global INACTIVATED_STATUS
INACTIVATED_STATUS = 'Inactivated'

global INACTIVATED_REASON_DELETED
INACTIVATED_REASON_DELETED = 'Patient Deleted'

global ACTIVATED_STATUS
ACTIVATED_STATUS = 'Activated'

global ACTIVATED_REASON
ACTIVATED_REASON = 'New patient'

global REACTIVATED_STATUS
REACTIVATED_STATUS = 'Reactivated'

global REACTIVATED_REASON
REACTIVATED_REASON = 'Readmission'

global SENSOR_REMOVED
SENSOR_REMOVED = 'SENSOR_REMOVED'

global UNASSIGNED_DEVICE_ERROR
UNASSIGNED_DEVICE_ERROR = 'Patient not assigned to device'

global SENSOR_UNASSIGNED
SENSOR_UNASSIGNED = 'no sensor assigned'

global UNKNOWN
UNKNOWN = 'unknown'

global NA
NA = 'N/A'

#reports


#### reposition
global REPOSITION_PATIENT
REPOSITION_PATIENT = 'Patient Repos'

global REPOSITION_CAREGIVER
REPOSITION_CAREGIVER = 'Caregiver Repos'

global REPOSITION_TOTAL
REPOSITION_TOTAL = 'Total Repos'

global REPOSITION_PATIENT_CAREGIVER
REPOSITION_PATIENT_CAREGIVER = 'Patient/Caregiver Repos'

global ACTIVE_PATIENTS
ACTIVE_PATIENTS = 'Active Patients'

global ACTIVE_PATIENTS_HOURS
ACTIVE_PATIENTS_HOURS = 'Active Patient Hours'

global UNIQUE_ACTIVE_PATIENTS
UNIQUE_ACTIVE_PATIENTS = 'Unique Active Patients'

global REPOSITION_PATIENT_PER_PATIENT
REPOSITION_PATIENT_PER_PATIENT = 'Patient Repos/Patient'

global REPOSITION_CAREGIVER_PER_PATIENT
REPOSITION_CAREGIVER_PER_PATIENT = 'Caregiver Repos/Patient'

global REPOSITION_AVG
REPOSITION_AVG = 'Avg Repos'

global REPOSITION_MAX
REPOSITION_MAX = 'Max Repos'

global REPOSITION_MIN
REPOSITION_MIN = 'Min Repos'

global REPOSITION_AVG_TOP
REPOSITION_AVG_TOP = 'Avg Repos for Top 33%'

global REPOSITION_AVG_MID
REPOSITION_AVG_MID = 'Avg Repos for Mid 33%'

global REPOSITION_AVG_LOW
REPOSITION_AVG_LOW = 'Avg Repos for Low 33%'



#### alarm response
global ALARM_ALARMS
ALARM_ALARMS = 'Alarms'

global ALARM_MINUTES_ALARMING
ALARM_MINUTES_ALARMING = 'Minutes of Alarming'

global ALARM_MINUTES_ALARMS
ALARM_MINUTES_ALARMS = 'Minutes/Alarms'

#ACTIVE_PATIENTS

global ALARM_ALARMED_PATIENTS
ALARM_ALARMED_PATIENTS = 'Alarmed Patients'

global ALARM_ALARMED_PATIENTS_HOURS
ALARM_ALARMED_PATIENTS_HOURS = 'Alarmed Patient Hours'

global ALARM_UNIQUE_ALARMED_PATIENTS
ALARM_UNIQUE_ALARMED_PATIENTS = 'Unique Alarmed Patients'

global ALARM_ALARMED_ACTIVE
ALARM_ALARMED_ACTIVE = 'Alarmed Patients/Active Patients'

global ALARM_ALARMED_ACTIVE_HOURS
ALARM_ALARMED_ACTIVE_HOURS = 'Alarmed Patient Hours/Active Patient Hours'

global ALARM_UNIQUE_ALARMED_ACTIVE
ALARM_UNIQUE_ALARMED_ACTIVE = 'Unique Alarmed Patients/Unique Active Patients'

global ALARM_ALARMS_ALARMED
ALARM_ALARMS_ALARMED = 'Alarms/Alarmed Patients'

global ALARM_ALARMS_ALARMED_HOURS
ALARM_ALARMS_ALARMED_HOURS = 'Alarms/Alarmed Patient Hours'

global ALARM_ALARMS_UNIQUE_ALARMED
ALARM_ALARMS_UNIQUE_ALARMED = 'Alarms/Unique Alarmed Patients'

global ALARM_MAX_ALARMS
ALARM_MAX_ALARMS = 'Max Alarms'

global ALARM_MIN_ALARMS
ALARM_MIN_ALARMS = 'Min Alarms'

global ALARM_AVG_ALARMS_TOP
ALARM_AVG_ALARMS_TOP = 'Avg Alarms for Top 33%'

global ALARM_AVG_ALARMS_MID
ALARM_AVG_ALARMS_MID = 'Avg Alarms for Mid 33%'

global ALARM_AVG_ALARMS_LOW
ALARM_AVG_ALARMS_LOW = 'Avg Alarms for Low 33%'

global ALARM_MINUTES_ALARMED_PATIENTS
ALARM_MINUTES_ALARMED_PATIENTS = 'Minutes/Alarmed Patients'

global ALARM_MINUTES_ALARMED_PATIENTS_HOURS
ALARM_MINUTES_ALARMED_PATIENTS_HOURS = 'Minutes/Alarmed Patient Hours'

global ALARM_MINUTES_UNIQUE_ALARMED_PATIENTS
ALARM_MINUTES_UNIQUE_ALARMED_PATIENTS = 'Minutes/Unique Alarmed Patient'

global ALARM_MAX_MINUTES
ALARM_MAX_MINUTES = 'Max Minutes'

global ALARM_MIN_MINUTES
ALARM_MIN_MINUTES = 'Min Minutes'

global ALARM_AVG_MINUTES_TOP
ALARM_AVG_MINUTES_TOP = 'Avg Minutes for Top 33%'

global ALARM_AVG_MINUTES_MID
ALARM_AVG_MINUTES_MID = 'Avg Minutes for Mid 33%'

global ALARM_AVG_MINUTES_LOW
ALARM_AVG_MINUTES_LOW = 'Avg Minutes for Low 33%'

#sms
global SMS_ALERT_TEXT
SMS_ALERT_TEXT = 'PressureAlert: Patient %s needs to be repositioned right away.'

global SMS_CLEARED_TEXT
SMS_CLEARED_TEXT = 'PressureAlert: Patient %s has been repositioned.'

global SMS_RISING_ALARM
SMS_RISING_ALARM = 'PressureAlert: Patient %s needs to be moved off pressure'

global SMS_ALARM_FALLING
SMS_ALARM_FALLING = 'PressureAlert: Patient %s moved and is off pressure'

global SMS_FALLING_ALARM
SMS_FALLING_ALARM = 'PressureAlert: Patient %s needs to be moved off pressure'

global SMS_FALLING_NOPRESSURE
SMS_FALLING_NOPRESSURE = 'PressureAlert: Patient %s pressure point is resolved'



