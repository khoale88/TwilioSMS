from __future__ import print_function
from datetime import datetime
import json
from twilio.rest import Client
from pytz import timezone

from repository import userRepository as USRR
from repository import groupRepository as GRPR
from repository import smsRuleRepository as SMSRR

from gsheet import driver as GSD

twilio_cred = json.load(open("localfile/twilioCred.json", 'r'))
twilio_client = Client(twilio_cred['account'], twilio_cred['token'])
twilio_number = twilio_cred['number']

def send_sms_by_users(users, msg):
    if not isinstance(users, list):
        users = [users]
    send_list = []
    unsend_list = []
    for user in users:
        try:
            if not user[USRR.USER_PHONE]:
                unsend_list.append(user[USRR.USER_FN])
                continue
            user_msg = msg.replace("_user_", user[USRR.USER_FN])
            twilio_client.messages.create(to=user[USRR.USER_PHONE],
                                          from_=twilio_number,
                                          body=user_msg)
            send_list.append(user[USRR.USER_FN])
        except Exception as e:
            print(e)
            unsend_list.append(user[USRR.USER_FN])
    return send_list, unsend_list

def shoud_remind_send_data(user, rule):
    """return if a user should be reminded to send data to lumlife"""
    local_time = datetime.now(timezone(user[USRR.USER_TZ]))
    weekday = local_time.weekday()
    hour = int(local_time.strftime("%H"))
    return(rule and
           weekday in rule[SMSRR.SMS_RULE_DOW] and
           hour == rule[SMSRR.SMS_RULE_TOD] and
           USRR.USER_FITBIT not in user[USRR.USER_ID])

def remind_send_data(user, rule):
    msg = rule[SMSRR.SMS_RULE_MSG]
    return send_sms_by_users(user, msg)

def should_notify_login(user, rule):
    """return if a user should be notified to login"""
    local_time = datetime.now(timezone(user[USRR.USER_TZ]))
    weekday = local_time.weekday()
    hour = int(local_time.strftime("%H"))
    return(rule and
           weekday in rule[SMSRR.SMS_RULE_DOW] and
           hour == rule[SMSRR.SMS_RULE_TOD])

def notify_login(user, rule, groups):
    lumlifehost = 'http://lumlife.com/'
    user_groups = [gr.strip() for gr in user[USRR.USER_GROUP_NUM].split(',')]
    links = [lumlifehost + groups[gkey] for gkey in user_groups if gkey in groups.keys()]
    links = ", ".join(links)
    msg = rule[SMSRR.SMS_RULE_MSG]
    msg = msg.replace("_URL_", links)
    return send_sms_by_users(user, msg)

def handle_hourly_events():
    """batch processing every hour on all users in database"""
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

    success = []
    failure = []
    for user in users:
        if should_notify_login(user, login_rule):
            succ, fail = notify_login(user, login_rule, groups)
            success.extend(succ)
            failure.extend(fail)
        if shoud_remind_send_data(user, rmd_rule):
            succ, fail = remind_send_data(user, rmd_rule)
            success.extend(succ)
            failure.extend(fail)
    return success, failure

if __name__ == "__main__":
    pass
