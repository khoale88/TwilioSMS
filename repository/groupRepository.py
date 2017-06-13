from __future__ import print_function
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gsheet import driver as GSD
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SERVICE_SECRET_FILE = 'localfile/lumlife-gsheet-cred.json'

GROUP_NUM = 'Group Number'
GROUP_ID = 'Group ID'
GROUP_URL = 'Google URL'

SPREADSHEET_ID = '1XiNoDc2-hU8i8_GAEEUsqGmth2rF0mPVg1js_JySaAY'
# SPREADSHEET_ID ='1H7uRrL0-K9pHq3NfJ4OmC3Qrck3AjTrigF33lKqMSuA'

def get_groups(filt=None, proj=None):
    client = GSD.get_lumlife_client()
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet('Groups')
    groups = sheet.get_all_records()
    groups = GSD.record_filter(groups, filt)
    groups = GSD.record_project(groups, proj)
    return groups

if __name__ == "__main__":
    pass