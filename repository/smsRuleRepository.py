from __future__ import print_function
from oauth2client.service_account import ServiceAccountCredentials
from twilio_app import TESTING
import gspread
from gsheet import driver as GSD
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SERVICE_SECRET_FILE = 'localfile/lumlife-gsheet-cred.json'

if TESTING:
    SPREADSHEET_ID = '1XiNoDc2-hU8i8_GAEEUsqGmth2rF0mPVg1js_JySaAY'
else:
    SPREADSHEET_ID = '1H7uRrL0-K9pHq3NfJ4OmC3Qrck3AjTrigF33lKqMSuA'

SMS_RULE_WORKSHEET = 'SMS Rules'

SMS_RULE_NAME = 'Name'
SMS_RULE_DOW = 'Days of Week'
SMS_RULE_TOD = 'Time of Day'
SMS_RULE_MSG = 'Message'
SMS_RULE_ACTIVE = 'Active'

def get_sms_rules(filt=None, proj=None):
    client = GSD.get_lumlife_client()
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SMS_RULE_WORKSHEET)
    rules = sheet.get_all_records()
    rules = GSD.record_filter(rules, filt)
    rules = GSD.record_project(rules, proj)
    return rules
