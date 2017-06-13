from __future__ import print_function
from oauth2client.service_account import ServiceAccountCredentials 
from twilio_app import TESTING
import gspread
from gsheet import driver as GSD


SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SERVICE_SECRET_FILE = 'localfile/lumlife-gsheet-cred.json'

USER_ID = 'User ID (unique/fitbit)'
USER_PHONE = 'Phone Number'
USER_FN = 'First Name'
USER_SMS_SUB = 'SMS Subscribe'
USER_DEVICE = 'Device Type'
USER_EMAIL = 'Email Address'
USER_GROUP_NUM = 'Group Number'
USER_TZ = 'Timezone'

USER_FITBIT = 'fitbit'

USER_BOOL_TRUE = 'TRUE'
USER_BOOL_FALSE = 'FALSE'

if TESTING:
    SPREADSHEET_ID = '1XiNoDc2-hU8i8_GAEEUsqGmth2rF0mPVg1js_JySaAY'
else:
    SPREADSHEET_ID = '1H7uRrL0-K9pHq3NfJ4OmC3Qrck3AjTrigF33lKqMSuA'

USER_WORKSHEET = 'Users'

def get_users(filt=None, proj=None):
    """return a list of all users"""
    client = GSD.get_lumlife_client()
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(USER_WORKSHEET)
    users = sheet.get_all_records()
    users = GSD.record_filter(users, filt)
    users = GSD.record_project(users, proj)
    return users

def update_users(filt=None, updt=None):
    """update all users who meets the filter requirements with update values"""
    updt_count = 0
    if updt is None:
        return "nothing to update"
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_SECRET_FILE, SCOPES)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(USER_WORKSHEET)
    updt_keys = updt.keys()
    users = get_users(filt=filt, proj=None)
    user_keys = users[0].keys()

    for key in updt_keys:
        if key not in user_keys:
            raise Exception('Update Users: Key "%s" not found'%(key))

    for user in users:
        row = sheet.find(user[USER_ID]).row
        for key in updt_keys:
            if user[key] != updt[key]:
                try:
                    col = sheet.find(key).col
                    sheet.update_cell(row, col, updt[key])
                    updt_count += 1
                except Exception as e:
                    print(e)
                    continue
    return updt_count
