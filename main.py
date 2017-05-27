from flask import Flask,redirect, make_response, abort, Response, json, request, url_for
from twilio.rest import TwilioRestClient
from twilio import twiml
import requests

twilio_cred = json.load(open("twilioCred.json", 'r'))
twilio_client = TwilioRestClient(twilio_cred['account'],twilio_cred['token'])

app = Flask(__name__)
app.config['twilioNumber'] = twilio_cred['number']
app.config.from_object('config')

def send_sms(to_numbers, msg):
    for number in to_numbers:
        twilio_client.sms.messages.create(to=number,
                                          from_=app.config['twilioNumber'],
                                          body=msg)

def send_sms_bycontact(contacts, msg):
    if type(contacts) is not dict:
        raise Exception("contacts must be a dictionary/map")
    send_list = []
    unsend_list = []
    for user in contacts:
        try:
            user_contact = contacts[user]
            user_msg = msg.replace("_user_", user_contact['name'])
            user_phoneNumber = user_contact['phoneNumber']
            twilio_client.sms.messages.create(to=user_phoneNumber,
                                              from_=app.config['twilioNumber'],
                                              body=user_msg)
            send_list.append(user_contact['name'])
            print send_list
        except Exception as e:
            unsend_list.append({user_contact['name']: str(e)})
    return send_list, unsend_list

@app.route("/twilio/receiveSMS", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    number = request.form['From']
    msg_body = request.form['Body']

    twilio_resp = twiml.Response()

    contacts = json.load(open("phoneNumbers.json", 'r'))
    if number == contacts["Cong"]["phoneNumber"]:
        resp = app.test_client().put('http://locahost:5000/twilio/sendSMS-toAll',
                                     headers={'Content-Type':'application/json'},
                                     data=json.dumps({"message":msg_body}))
        twilio_resp.message(str(resp.data))
    else:
        twilio_resp.message("Thank you for the text: " + msg_body)

    return str(twilio_resp)


@app.route('/twilio/sendSMS', methods=['PUT'])
def send_twilio_sms():
    json_request = request.json
    if len(json_request['numbers']) != 0:
        send_sms(to_numbers=json_request['numbers'],
                 msg=json_request['message'])
    return Response(status=200)

@app.route('/twilio/sendSMS-toAll', methods=['PUT'])
def send_twilio_sms_toall():
    json_request = request.json
    if 'message' not in json_request:
        abort(response='need "message" field', status=400)
    msg = json_request['message']
    contacts = json.load(open("phoneNumbers.json", 'r'))
    print contacts
    success, failure = send_sms_bycontact(contacts, msg)

    body = {}
    body['success'] = "message has been send to " + ", ".join(success)
    body['error']= ", ".join(failure)
    return Response(headers={"content-type":"application/json"},
                    response=json.dumps(body),
                    status=200)

@app.route('/twilio/sendSMS-byNames', methods=['PUT'])
def send_twilio_sms_byname():
    json_request = request.json
    if 'message' not in json_request:
        abort(response='need "message" field', status=400)
    msg = json_request['message']

    names = []
    if 'names' in json_request:
        names = json_request['names']

    if type(names) is not list:
        abort(response='"names" field must be a list', status=400)

    contacts = json.load(open("phoneNumbers.json", 'r'))
    if len(names) == 0:
        names = contacts.keys()

    to_contacts = {key:contacts[key] for key in contacts if key in names}
    success, failure = send_sms_bycontact(to_contacts, msg)

    body = {}
    body['success'] = "message has been send to " + ", ".join(success)
    body['error']= ", ".join(failure)
    return Response(headers={"content-type":"application/json"},
                    response=json.dumps(body),
                    status=200)

@app.route('/twilio/addNumber', methods=['POST'])
def add_twilio_number():
    json_request = request.json
    if 'name' not in json_request or \
       'phoneNumber' not in json_request:
        return Response(response="need name and phoneNumber fields",status=403)

    name = json_request['name']
    contacts = json.load(open("phoneNumbers.json", 'r'))
    if name in contacts:
        err_msg = "name already exist! Use updateNumber instead"
        return Response(err_msg, status=400)

    phoneNumber = json_request['phoneNumber']
    phoneNumber = str(phoneNumber)
    phoneNumber = phoneNumber.replace("-", "")
    if phoneNumber[:2] != "+1":
        phoneNumber = "+1" + phoneNumber
    contacts[name] = {"name":name,
                        "phoneNumber":phoneNumber}
    json.dump(contacts, open("phoneNumbers.json", 'w'))
    return Response(headers={"content-type":"application/json"},
                    response=json.dumps(contacts),
                    status=200)

@app.route('/twilio/updateNumber', methods=['PUT'])
def update_twilio_number():
    json_request = request.json
    if 'name' not in json_request or \
       'phoneNumber' not in json_request:
        return Response(response="need name and phoneNumber fields",status=403)

    name = json_request['name']
    contacts = json.load(open("phoneNumbers.json", 'r'))
    if name not in contacts:
        return Response(response="name not found! Use addNumber instead",
                        status=403)
    phoneNumber = json_request['phoneNumber']
    phoneNumber = phoneNumber.replace("-", "")
    if phoneNumber[:2] != "+1":
        phoneNumber = "+1" + phoneNumber
    contacts[name]['phoneNumber'] = phoneNumber
    json.dump(contacts, open("phoneNumbers.json", 'w'))
    return Response(headers={"content-type":"application/json"},
                    response=json.dumps(contacts),
                    status=200)

@app.route('/twilio/phoneNumbers', methods=['GET'])
def get_twilio_numbers():
    contacts = json.load(open("phoneNumbers.json", 'r'))
    return Response(headers={"content-type":"application/json"},
                    response=json.dumps(contacts),
                    status=200)

@app.route('/twilio/removeNumbers', methods=['DELETE'])
def del_twilio_numbers():
    json_request = request.json
    names = json_request['names']
    contacts = json.load(open("phoneNumbers.json", 'r'))
    least = False
    for name in names:
        if name in contacts.keys():
            least = True
            del contacts[name]
    if least is True:
        json.dump(contacts, open("phoneNumbers.json", 'w'))
    return Response(headers={"content-type":"application/json"},
                    response=json.dumps(contacts),
                    status=200)

if __name__ == '__main__':
    app.run(host=app.config["HOST"],
            port=app.config["PORT"])

