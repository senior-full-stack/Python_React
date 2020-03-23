from dm_app.app import app, db
from dm_app.models import DBBodyLocation, DBDevice, DBEvent, DBEventHistory, DBGlobalDeviceSettings, DBGlobalLocationSettings, \
    DBPatient, DBPatientHistory, DBPatientHistory, DBUser
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand



migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()