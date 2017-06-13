from twilio_app import app
from flask import request, json
from twilio import twiml
from repository import userRepository as USRR

UNSUB_MSGS = ['_STOP', '_UNSUBCRIBE']
SUB_MSGS = ['_START', '_SUBCRIBE']

@app.route("/twilio/receiveSMS", methods=['GET', 'POST'])
def handle_coming_sms():
    """Respond to incoming message with a simple text message."""
    number = request.form['From']
    msg_body = request.form['Body']

    # type cast to int to match with data type in google sheet
    if number[0] == "+":
        number = number[1:]
    number = int(number)
    twilio_resp = twiml.Response()

    if msg_body in UNSUB_MSGS:
        updt = USRR.update_users(filt={USRR.USER_PHONE:number},
                                 updt={USRR.USER_SMS_SUB:USRR.USER_BOOL_FALSE})
        if updt != 0:
            twilio_resp.message("You have been unsubscribed from Lumlife. "
                                "Text _START to resubscribe. Data might apply")
    elif msg_body in SUB_MSGS:
        updt = USRR.update_users(filt={USRR.USER_PHONE:number},
                                 updt={USRR.USER_SMS_SUB:USRR.USER_BOOL_TRUE})
        if updt != 0:
            twilio_resp.message("You have been subscribed to Lumlife. "
                                "Text _STOP to unsubscribe. Data might apply")
    else:
        pass
    return str(twilio_resp)
