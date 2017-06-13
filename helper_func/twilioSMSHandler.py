from __future__ import print_function
from twilio.rest import TwilioRestClient
import json
from datetime import datetime
from pytz import timezone

from repository import userRepository as USRR
from repository import groupRepository as GRPR
from repository import smsRuleRepository as SMSRR

from gsheet import driver as GSD

twilio_cred = json.load(open("localfile/twilioCred.json", 'r'))
twilio_client = TwilioRestClient(twilio_cred['account'], twilio_cred['token'])
twilio_number = twilio_cred['number']

def send_sms_bycontact(contacts, msg):
    if not isinstance(contacts, list):
        contacts = [contacts]
    send_list = []
    unsend_list = []
    for user in contacts:
        try:
            if not user[USRR.USER_PHONE]:
                unsend_list.append(user[USRR.USER_FN])
                continue

            user_msg = msg.replace("_user_", user[USRR.USER_FN])
            twilio_client.sms.messages.create(to=user[USRR.USER_PHONE],
                                              from_=twilio_number,
                                              body=user_msg)
            send_list.append(user[USRR.USER_FN])
        except Exception as e:
            print(e)
            unsend_list.append(user[USRR.USER_FN])
    return send_list, unsend_list

def handle_hourly_events():
    users = USRR.get_users(filt={USRR.USER_SMS_SUB:USRR.USER_BOOL_TRUE,
                                 USRR.USER_PHONE:{GSD.NE:""},
                                 USRR.USER_TZ:{GSD.NE:""},
                                 USRR.USER_GROUP_NUM:{GSD.NE:""}})
    groups = GRPR.get_groups(filt={GRPR.GROUP_ID:{GSD.NE:""}})
    groups = {group[GRPR.GROUP_NUM]:group[GRPR.GROUP_ID] for group in groups}
    rules = SMSRR.get_sms_rules(filt={SMSRR.SMS_RULE_ACTIVE:GSD.BOOL_TRUE})
    rmd_rule = {}
    login_rule = {}
    for rule in rules:
        rule[SMSRR.SMS_RULE_DOW] = [int(ele) for ele in rule[SMSRR.SMS_RULE_DOW].split(',')]
        if rule[SMSRR.SMS_RULE_NAME] == 'Send Data Reminder':
            rmd_rule = rule
        elif rule[SMSRR.SMS_RULE_NAME] == 'Login Push Notification':
            login_rule = rule

    lumlifehost = 'http://lumlife.com/'
    success = []
    failure = []
    for user in users:
        local_time = datetime.now(timezone(user[USRR.USER_TZ]))
        weekday = local_time.weekday()
        hour = int(local_time.strftime("%H"))
        if(login_rule and
           weekday in login_rule[SMSRR.SMS_RULE_DOW] and
           hour == login_rule[SMSRR.SMS_RULE_TOD]):
            user_groups = [gr.strip() for gr in user[USRR.USER_GROUP_NUM].split(',')]
            links = [lumlifehost + groups[gkey] for gkey in user_groups if gkey in groups.keys()]
            links = ", ".join(links)
            msg = login_rule[SMSRR.SMS_RULE_MSG]
            msg = msg.replace("_URL_", links)
            succ, fail = send_sms_bycontact(user, msg)
            success.extend(succ)
            failure.extend(fail)
        if(rmd_rule and
           weekday in rmd_rule[SMSRR.SMS_RULE_DOW] and
           hour == rmd_rule[SMSRR.SMS_RULE_TOD]):
            if USRR.USER_FITBIT not in user[USRR.USER_ID]:
                msg = rmd_rule[SMSRR.SMS_RULE_MSG]
                succ, fail = send_sms_bycontact(user, msg)
                success.extend(succ)
                failure.extend(fail)
    return success, failure

if __name__ == "__main__":
    pass
