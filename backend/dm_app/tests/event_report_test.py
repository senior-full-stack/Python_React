import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from random import randint
import json
import jwt, base64
import requests
import time, datetime
from flask_api import status
import uuid
from rfc3339 import nowtostr, now, strtotimestamp, nowtimestamp, utcformysqlfromtimestamp

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

def test_event_report():
    start_time = time.time()
    #register user
    ID = str(uuid.uuid4())
    username = ID + '@dmsystems.com'
    admin_user = 'mtrapani@dmsystems.com'
    admin_pass = 'PASuccess1'
    name = ID
    password = str(uuid.uuid4())
    new_password = 'pass'
    device_id = str(uuid.uuid4())
    device_id2 = str(uuid.uuid4())
    device_secret = str(uuid.uuid4())
    device_secret2 = str(uuid.uuid4())
    patient_name = 'Patient'
    patient_id = str(uuid.uuid4())
    sync_id_1 = str(uuid.uuid4())
    sync_id_2 = str(uuid.uuid4())
    url_base = 'http://localhost:5666/'#'http://dm.nemik.net/api/v1/'#

    #log in user
    headers = {'Content-Type' : 'application/json'}
    data = {"email": admin_user ,"password": admin_pass}
    url = url_base + 'users/login'

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert status.HTTP_200_OK == r.status_code
    assert 'token' in r.json()

    admin_token = r.json()['token']

    print ("--- %s seconds ---" % (time.time() - start_time))

    #get event reports for patient
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + admin_token
        }
    url = url_base + 'eventreports/wallace'

    r = requests.get(url, headers=headers)

    assert status.HTTP_200_OK == r.status_code

    #get event reports
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + admin_token
        }
    url = url_base + 'eventreports'

    r = requests.get(url, headers=headers)

    assert status.HTTP_200_OK == r.status_code
