from twilio_app import app
from flask import request, json, abort, Response
from helper_func.validation import body_field_validation as BodyFieldValidation
from helper_func.validation import lumlife_key_validation as LumKeyValidation
from helper_func.twilioSMSHandler import send_sms_bycontact, handle_hourly_events
from gsheet import driver as GSD

from repository import userRepository as USRR
from repository import pwdRepository as PWDR

@app.route('/twilio/hourly', methods=['PUT'])
@LumKeyValidation(PWDR.PWD_TWSMS_SV)
def hourly_trigger():
    success, failure = handle_hourly_events()
    body = {}
    body['success'] = ", ".join(success)
    body['failure'] = ", ".join(failure)
    return Response(response=json.dumps(body), status=200,
                    headers={"content-type":"application/json"})

@app.route('/twilio/sendSMS-toSubscribe', methods=['PUT'])
@LumKeyValidation(PWDR.PWD_TWSMS_SV)
@BodyFieldValidation('message')
def send_twilio_sms_toSubscribe():
    msg = request.json['message']
    users = USRR.get_users(filt={USRR.USER_SMS_SUB:USRR.USER_BOOL_TRUE})
    success, failure = send_sms_bycontact(users, msg)
    body = {}
    body['success'] = ", ".join(success)
    body['failure'] = ", ".join(failure)
    return Response(response=json.dumps(body), status=200,
                    headers={"content-type":"application/json"})

@app.route('/twilio/sendSMS-byNames', methods=['PUT'])
@LumKeyValidation(PWDR.PWD_TWSMS_SV)
@BodyFieldValidation('message', 'names')
def send_twilio_sms_byname():
    msg = request.json['message']
    names = request.json['names']
    users = USRR.get_users(filt={USRR.USER_FN:{GSD.ISIN:names},
                                 USRR.USER_SMS_SUB:USRR.USER_BOOL_TRUE})
    success, failure = send_sms_bycontact(users, msg)
    body = {}
    body['success'] = ", ".join(success)
    body['failure'] = ", ".join(failure)
    return Response(response=json.dumps(body), status=200,
                    headers={"content-type":"application/json"})
