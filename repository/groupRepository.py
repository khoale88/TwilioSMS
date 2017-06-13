from __future__ import print_function
from twilio_app import TESTING
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gsheet import driver as GSD
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SERVICE_SECRET_FILE = 'localfile/lumlife-gsheet-cred.json'

GROUP_NUM = 'Group Number'
GROUP_ID = 'Group ID'
GROUP_URL = 'Google URL'

if TESTING:
    SPREADSHEET_ID = '1XiNoDc2-hU8i8_GAEEUsqGmth2rF0mPVg1js_JySaAY'
else:
    SPREADSHEET_ID = '1H7uRrL0-K9pHq3NfJ4OmC3Qrck3AjTrigF33lKqMSuA'
GROUP_WORKSHEET = 'Groups'

def get_groups(filt=None, proj=None):
    client = GSD.get_lumlife_client()
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(GROUP_WORKSHEET)
    groups = sheet.get_all_records()
    groups = GSD.record_filter(groups, filt)
    groups = GSD.record_project(groups, proj)
    return groups
