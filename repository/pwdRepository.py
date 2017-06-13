from __future__ import print_function
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gsheet import driver as GSD
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SERVICE_SECRET_FILE = 'localfile/lumlife-gsheet-cred.json'

SPREADSHEET_ID = '1XiNoDc2-hU8i8_GAEEUsqGmth2rF0mPVg1js_JySaAY'

PWD_SV_NAME = "Service Name"
PWD_SV_KEY = "Service Key"
PWD_TWSMS_SV = "Twilio SMS"

def get_pwds(filt=None, proj=None):
    client = GSD.get_lumlife_client()
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet('Keys')
    pwds = sheet.get_all_records()
    pwds = GSD.record_filter(pwds, filt)
    pwds = GSD.record_project(pwds, proj)
    return pwds
