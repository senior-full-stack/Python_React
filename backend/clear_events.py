from dm_app.app import app, db
from dm_app.models import *
from pprint import pprint

BODY_LOCATIONS = ['SKULL', 'UPPER_SPINE', 'SACRUM', 'LEFT_HIP', 'RIGHT_HIP', 'LEFT_ISCHIA', 'RIGHT_ISCHIA', 'LEFT_ELBOW',
'RIGHT_ELBOW', 'LEFT_HEEL', 'RIGHT_HEEL']

ps = DBPatient.query.all()

for p in ps:
    for l in BODY_LOCATIONS:
        i = 0
        j = 1
        fix_count = 0
        es = DBEvent.query.filter_by(patient_id=p.id, range_end=None, location=l).order_by(DBEvent.range_start).all()
        if len(es) > 1:
            print len(es)
            for e in es:
                if j < len(es):
                    es[i].range_end = es[j].range_start
                    fix_count = fix_count + 1
                    print fix_count
                    my_logger.warning(str(p.name) + ' ' + l)
                i = i + 1
                j = j + 1
db.session.commit()