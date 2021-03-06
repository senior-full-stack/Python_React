from functools import wraps
import json, time, hmac, requests, string, random, flask_wtf, uuid, logging, logging.handlers
from datetime import datetime, timedelta
from hashlib import sha1
from flask import Flask, redirect, url_for, session, request, make_response, render_template, app, Response
from flask_api import status
from flask_restful import Resource, Api
from flask_restful_swagger import swagger
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
import structlog
from structlog import get_logger
from structlog.processors import JSONRenderer

app = Flask(__name__, instance_relative_config=False)
api = swagger.docs(Api(app), apiVersion='0.1')

#Load the file specified by the APP_CONFIG_FILE environment variable
#Variables defined here will override those in the default configuration
app.config.from_envvar('APP_CONFIG_FILE')
app.secret_key = app.config['SECRET_KEY']
app.salt = app.config['SALT']

#app.debug = app.config["DEBUG"]
#app.config['SQLALCHEMY_RECORD_QUERIES'] = True
#app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
LOGGING_INSTANCE = app.config["LOGGING_INSTANCE"]
struct_logger = structlog.wrap_logger(structlog.PrintLogger(), processors=[JSONRenderer()])

ALERT_INTERVAL_SECONDS = 120

app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

#timezone
TIMEZONE = 'America/Chicago'
USE_TIMEZONE = True

#facility
FACILITY = 'DEV'

ADMIN_FROM_ADDRESS = 'jflores@digitalhealths.com'