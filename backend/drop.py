from dm_app.app import app, db
from dm_app.models import *
from dm_app.rfc3339 import nowtostr, now, strtotimestamp, nowtimestamp, utcformysqlfromtimestamp
from dm_app.utils import hash_pass
db.drop_all()