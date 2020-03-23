from dm_app import *
from functools import wraps
from flask.globals import current_app, request
from flask_api import status
from flask_restful import reqparse
from models import db, DBDevice, DBUser, DBPatientActivation, DBPatientsActive, DBPatient, DBLargeRequest, DBEvent, DBEventHistory
import bcrypt
import datetime
from datetime import tzinfo
import hashlib, hmac
import jwt, base64
import urllib
from rfc3339 import strtotimestamp, nowtimestamp, utcfromtimestamp, utcformysqlfromtimestamp, now
import cProfile
import StringIO
import pstats
import contextlib
import time as _time
from dateutil import rrule, tz
from datetime import datetime, time
from globs import *
from actions.alert import Alert
import inspect

SECRET = app.secret_key #'moosheep'
TOKEN_EXPIRED_MINUTES = 86400 #60 seconds
SALT = app.salt

ZERO = timedelta(0)
HOUR = timedelta(hours=1)
STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0


@contextlib.contextmanager
def profiled():
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = StringIO.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    # uncomment this to see who's calling what
    # ps.print_callers()
    print(s.getvalue())

def log(ip, path, action, request, result, user=None, device=None, device_header=None, version_header=None):
    try:
        if user:
            if request and 'password' in request:
                request.pop('password')
            if request and 'old_password' in request:
                request.pop('old_password')
            if request and 'new_password' in request:
                request.pop('new_password')
            struct_logger.info(instance=LOGGING_INSTANCE, ip=ip, user=user, action=action, path=path, request=json.dumps(request), result=result)
        if device:
            struct_logger.info(instance=LOGGING_INSTANCE, ip=ip, device=device, action=action, path=path, request=json.dumps(request), result=result,
                device_id_header=device_header, android_version_header=version_header)
    except Exception as e:
            struct_logger.error(instance=LOGGING_INSTANCE, event='logging exception', message=e.message)

def hash_pass(password):
        return bcrypt.hashpw(str(password), SALT)

def offload_request(device_id, patient_id, request, request_class, request_action):
    struct_logger.msg(instance=LOGGING_INSTANCE, message='offloading request %s %s %s %s' % ( device_id, patient_id, request_class, request_action))
    offload = DBLargeRequest(device_id, patient_id, request, request_class, request_action, utcformysqlfromtimestamp(nowtimestamp()))
    db.session.add(offload)
    db.session.commit()

def authenticate_user_token_and_return_payload(token):
    payload = None
    if 'iat' in token:
        token_time = token['iat']
	difference = nowtimestamp() - token_time
        #print 'time difference' + str(difference)
        if difference < TOKEN_EXPIRED_MINUTES:
            if 'user' in token:
                user = DBUser.query.filter_by(email=token['user']).first()
                if user and user.deleted == False:
		    token2 = token.copy()
                    if 'org' in token and token['org'] == 'TEST':
                        token2.pop('org')
                        token2.pop('iat')
#                        token.pop('user')
#                        token2.pop('sub')
                        payload = token2
                    else:
                        payload = { 'error' : 'unauthorized'}
                else:
                    payload = { 'error' : 'user deleted'}
            else:
                payload = { 'error' : 'unauthorized'}
        else:
            payload = { 'error' : 'token expired'}
            log(request.remote_addr, request.path, request.method, request.json, 401, user=None, device=request.headers.get('Authorization'))
    return payload

def parse_user_token():
    if 'Authorization' not in request.headers:
        return None
    else:
        payload = None
        try:
            header = request.headers.get('Authorization')
            if header.split()[0].lower() == 'bearer':
                token = header.split()[1]
                token_decoded = jwt.decode(token, SECRET, algorithms=['HS256','HS512'])
                payload = authenticate_user_token_and_return_payload(token_decoded)
        except Exception as e:
            struct_logger.error(instance=LOGGING_INSTANCE, event='parse user token', message=e.message)
            log(request.remote_addr, request.path, request.method, request.json, 401, user=None, device=request.headers.get('Authorization'))
            payload = {'error' : 'error parsing token ' + str(e)}
    return payload

def validate_jwt_user_token(f):
    @wraps(f)
    def f1(*args, **kwargs):
        class_ = inspect.getcallargs(f, *args)['self'].__class__.__name__
        function_ = f.__name__

        if (class_ == 'Event' and function_ == 'post') or (class_ in ['Sync']): # and function_ == 'get'):
            token = parse_device_token()
        else:
            token = parse_user_token()

        if not token:
            log(request.remote_addr, request.path, request.method, request.json, 401, user=None, device=request.headers.get('Authorization'))
            return {'error': 'Forbidden - request requires a valid client token'}, status.HTTP_401_UNAUTHORIZED
        else:
            if 'error' in token:
                #parsing failed
                return token, status.HTTP_401_UNAUTHORIZED
            else:
                kwargs = dict(kwargs.items() + token.items())
                return f(*args, **kwargs)
    return f1

def validate_jwt_user_token_reports(f):
    @wraps(f)
    def f1(*args, **kwargs):
        if 'format' in request.args and request.args.get('format').lower() == 'csv':
            validation = parse_report_token()
            if not 'error' in validation:
                kwargs = dict(kwargs.items() + validation.items())
                return f(*args, **kwargs)
            else:
                log(request.remote_addr, request.path, request.method, request.json, 401, user=request.headers.get('email'), 
                    device=request.headers.get('token'))
                return validation, status.HTTP_401_UNAUTHORIZED
        else:
            token = parse_user_token()
            if not token:
                log(request.remote_addr, request.path, request.method, request.json, 401, user=None, device=request.headers.get('Authorization'))
                return {'error': 'Forbidden - request requires a valid client token'}, status.HTTP_401_UNAUTHORIZED
            else:
                if 'error' in token:
                    #parsing failed
                    return token, status.HTTP_401_UNAUTHORIZED
                else:
                    kwargs = dict(kwargs.items() + token.items())
                    return f(*args, **kwargs)
    return f1

def parse_report_token():
    response = None
    email = request.args.get('email')
    expiration = request.args.get('expiration')
    token = request.args.get('token')

    if email and expiration and token:
        now = nowtimestamp()
        if int(expiration) >= now:
            compare_token = hmac.new(SECRET, email + '_' + expiration, hashlib.sha256).hexdigest()
            if compare_token == token:
                response = {'user': email}
            else:
                response = {'error': 'Forbidden - request requires a valid token, token mismatch'}
        else:
            response = {'error': 'Forbidden - request requires a valid token, expired'}
    return response



def authenticate_device_token_and_return_payload(token):
    payload = None
    if 'iat' in token:
        token_time = token['iat']
        difference = nowtimestamp() - token_time
        #print 'time difference' + str(difference)
        if difference < TOKEN_EXPIRED_MINUTES:
            if 'sub' in token:
                device = DBDevice.query.filter_by(serial=token['sub']).first()
                if device and device.deleted == False:
                    #authenticate = jwt.decode(header_token, device.secret, algorithms=['HS256','HS512'], leeway=20)
                    payload = {'device_id' : device.id, 'patient_id' : device.patient_id, 'medical_record_number' : device.medical_record_number, 
                    'device_serial' : device.serial }
                    record_device_online(device)
                    device.last_seen = utcformysqlfromtimestamp(nowtimestamp())
                    db.session.commit()
        else:
            #log(request.remote_addr, request.path, request.method, request.json, 401, user=None, device=request.headers.get('Authorization'))
            payload = { 'error' : 'token expired'}
    return payload


def record_device_online(device):
    if device.last_seen and device.last_seen < (datetime.utcnow() - timedelta(seconds=ALERT_INTERVAL_SECONDS * 3)):
        p = DBPatient.query.filter_by(id=device.patient_id).first()
        if p:
            instance = utcformysqlfromtimestamp(nowtimestamp())

            subject = '%s: Room %s, device online' % (FACILITY, p.room)
            message = 'Device %s online at %s' % (device.serial, str(convert_date_to_tz(instance)))
            Alert().email_admins(DEVICE_ONLINE, message, subject)

            
            event = {}
            event['medical_record_number'] = p.medical_record_number
            event['unit_floor'] = p.unit_floor
            event['patient_id'] = p.id
            event['device_id'] = device.id
            event['instance'] = instance
            event['message'] = 'DEVICE ONLINE'
            e = DBEvent(**event)
            db.session.add(e)

            event_history = {}
            event_history['medical_record_number'] = p.medical_record_number
            event_history['unit_floor'] = p.unit_floor
            event_history['event_type'] = EVENT_HISTORY_DICT['DEVICE ONLINE']
            event_history['occurred'] = instance
            eh = DBEventHistory(**event_history)
            db.session.add(eh)


def parse_device_token():
    if 'Authorization' not in request.headers:
        return None
    else:
        payload = None
        try:
            header = request.headers.get('Authorization')
            if header.split()[0].lower() == 'bearer':
                token = header.split()[1]
                token_decoded = jwt.decode(token, SECRET, algorithms=['HS256','HS512'])
                payload = authenticate_device_token_and_return_payload(token_decoded)
        except Exception as e:
            struct_logger.error(instance=LOGGING_INSTANCE, event='parse device token', message=e.message)
            #log(request.remote_addr, request.path, request.method, request.json, 401, user=None, device=request.headers.get('Authorization'))
            payload = {'error' : 'error parsing token ' + str(e)}
    return payload

def validate_jwt_device_token(f):
    @wraps(f)
    def f1(*args, **kwargs):
        token = parse_device_token()
        if not token:
            log(request.remote_addr, request.path, request.method, request.json, 401, user=None, device=request.headers.get('Authorization'),
                device_header=request.headers.get(DEVICE_ID_HEADER), version_header=request.headers.get(ANDROID_VERSION_HEADER))
            return {'error': 'Forbidden - request requires a valid client token'}, status.HTTP_401_UNAUTHORIZED
        else:
            if 'error' in token:
                #parsing failed
                return token, status.HTTP_401_UNAUTHORIZED
            else:
                kwargs = dict(kwargs.items() + token.items())
                return f(*args, **kwargs)
    return f1

def validate_jwt_device_or_user_token(f):
    @wraps(f)
    def f1(*args, **kwargs):
        token = parse_either_token()
        if not token:
            log(request.remote_addr, request.path, request.method, request.json, 401, user=None, device=request.headers.get('Authorization'))
            return {'error': 'Forbidden - request requires a valid client token'}, status.HTTP_401_UNAUTHORIZED
        else:
            if 'error' in token:
                #parsing failed
                return token, status.HTTP_401_UNAUTHORIZED
            else:
                kwargs = dict(kwargs.items() + token.items())
                return f(*args, **kwargs)
    return f1

def parse_either_token():
    if 'Authorization' not in request.headers:
        return None
    else:
        payload = None
        try:
            header = request.headers.get('Authorization')

            if header.split()[0].lower() == 'bearer':
                token = header.split()[1]
                token_decoded = jwt.decode(token, None, algorithms=['HS256','HS512'], verify=False)
                payload = authenticate_device_token_and_return_payload(token_decoded, token)
                if not payload or 'error' in token_decoded:
                    #could be a user token
                    token_decoded = jwt.decode(token, SECRET, algorithms=['HS256','HS512'])
                    payload = authenticate_user_token_and_return_payload(token_decoded)
                elif token_decoded:
                    #device decode worked
                    payload = authenticate_device_token_and_return_payload(token_decoded, token)
        except Exception as e:
            struct_logger.error(instance=LOGGING_INSTANCE, event='parse either token', message=e.message)
            log(request.remote_addr, request.path, request.method, request.json, 401, user=None, device=request.headers.get('Authorization'),
                device_header=request.headers.get(DEVICE_ID_HEADER), version_header=request.headers.get(ANDROID_VERSION_HEADER))
            payload = {'error' : 'error parsing token ' + str(e)}
    return payload

def convert_date_to_tz(date):
    if USE_TIMEZONE:
        to_zone = tz.gettz(TIMEZONE)
        from_zone = tz.gettz('UTC')
        utc = date.replace(tzinfo=from_zone)
        converted_date = utc.astimezone(to_zone).replace(tzinfo=None)
    else:
        converted_date = date
    return converted_date

def convert_date_to_utc(date):
    if USE_TIMEZONE:
        to_zone = tz.gettz('UTC')
        from_zone = tz.gettz(TIMEZONE)
        utc = date.replace(tzinfo=from_zone)
        converted_date = utc.astimezone(to_zone).replace(tzinfo=None)
    else:
        converted_date = date
    return converted_date

def set_tz(date):
    if USE_TIMEZONE:
        to_zone = tz.gettz(TIMEZONE)
        converted_date = date.replace(tzinfo=to_zone)
    else:
        converted_date = date
    return converted_date

def populate_active_patients():
    l = DBPatientsActive.query.order_by(DBPatientsActive.date.desc(), DBPatientsActive.hour.desc()).first()
    if l:
        start_date = datetime.combine(l.date, time(hour=l.hour)) + timedelta(hours=1)
        start_date_utc = convert_date_to_utc(start_date)
        until = convert_date_to_tz(now())
        if start_date_utc <= now().replace(tzinfo=None, minute=0, second=0, microsecond=0):
            ps = DBPatient.query.filter_by(deleted=False).all()
            c = 0
            for p in ps:
                c += 1
                print c
                stop = False
                search_date = None
                a = DBPatientActivation.query.filter(DBPatientActivation.patient_id == p.id, DBPatientActivation.occurred < start_date_utc, 
                    DBPatientActivation.status.in_(['Activated', 'Reactivated'])).order_by(DBPatientActivation.occurred.desc()).first()
                if a:
                    d = DBPatientActivation.query.filter(DBPatientActivation.patient_id == p.id, DBPatientActivation.status == 'Inactivated', 
                        DBPatientActivation.occurred > a.occurred).first()
                    if d:
                        search_date = d.occurred
                        a_occurred_converted = convert_date_to_tz(a.occurred)
                        end_date = convert_date_to_tz(d.occurred)
                        for dt in rrule.rrule(rrule.HOURLY, dtstart=a_occurred_converted.replace(minute=0, second=0, microsecond=0), until=end_date):
                            po = DBPatientsActive.query.filter_by(date=dt.date(), hour=dt.hour, unit_floor=p.unit_floor).first()
                            if po:
                                po.number_active += 1
                                db.session.merge(po)
                            else:
                                po = DBPatientsActive(dt.date(), dt.hour, p.unit_floor, 1)
                                db.session.add(po)
                    else:
                        stop = True
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
                            a_occurred_converted = convert_date_to_tz(a.occurred)
                            end_date = convert_date_to_tz(d.occurred)
                            for dt in rrule.rrule(rrule.HOURLY, dtstart=a_occurred_converted.replace(minute=0, second=0, microsecond=0), until=end_date):
                                pa = DBPatientsActive.query.filter_by(date=dt.date(), hour=dt.hour, unit_floor=p.unit_floor).first()
                                if pa:
                                    pa.number_active += 1
                                    db.session.merge(po)
                                else:
                                    pa = DBPatientsActive(dt.date(), dt.hour, p.unit_floor, 1)
                                    db.session.add(po)
                        else:
                            stop = True
                            a_occurred_converted = convert_date_to_tz(a.occurred)
                            for dt in rrule.rrule(rrule.HOURLY, dtstart=a_occurred_converted.replace(minute=0, second=0, microsecond=0), until=until):
                                pa = DBPatientsActive.query.filter_by(date=dt.date(), hour=dt.hour, unit_floor=p.unit_floor).first()
                                if po:
                                    pa.number_active += 1
                                    db.session.merge(po)
                                else:
                                    pa = DBPatientsActive(dt.date(), dt.hour, p.unit_floor, 1)
                                    db.session.add(po)
                    else:
                        stop = True
        db.session.commit()
