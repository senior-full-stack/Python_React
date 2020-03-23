from ..models import *
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from ..globs import *
from dm_app import struct_logger, LOGGING_INSTANCE
import copy
import boto3
from twilio.rest import TwilioRestClient

class Alert(Resource):
	def post(self):
		status_code = status.HTTP_400_BAD_REQUEST
		response = None
		try:
			data = copy.deepcopy(request.json)
			client = TwilioRestClient(TWILIO_SID, TWILIO_AUTH_TOKEN)

			message = client.messages.create(
					body="Turn Patient",
					to=data.get('phone_number'),
					from_=TWILIO_PHONE_NUMBER,
				)
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST

		return response, status_code

	def send_sms(self, text, number, medical_record_number):
		try:
			client = TwilioRestClient(TWILIO_SID, TWILIO_AUTH_TOKEN)

			message = client.messages.create(
					body=text % medical_record_number,
					to=number,
					from_=TWILIO_PHONE_NUMBER,
				)
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, path=request.path, method=request.method, exception=e.message)
			response = e.message

	def email_admins(self, message_type, message, subject):
		try:
			admins = DBUser.query.filter_by(role=ADMIN, email_notification=True).all()
			addresses = []
			for a in admins:
				addresses.append(a.email)

			ses = boto3.client('ses')
			from_address = ADMIN_FROM_ADDRESS
			return_address = 'klein1jonathan@gmail.com'

			if message_type == DEVICE_UNPLUGGED or message_type == DEVICE_PLUGGED_IN or message_type == DEVICE_OFFLINE or message_type == DEVICE_ONLINE:
				response = ses.send_email(Source=from_address, Destination={'ToAddresses': addresses }, Message={'Subject': {'Data': subject },
					'Body': { 'Text': { 'Data': message} } }, ReturnPath=return_address)
		except Exception as e:
			struct_logger.error(instance=LOGGING_INSTANCE, method='Alert.email_admins', exception=e.message)
			response = e.message
			status_code = status.HTTP_400_BAD_REQUEST



