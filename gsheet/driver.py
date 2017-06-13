from __future__ import print_function
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SERVICE_SECRET_FILE = 'localfile/lumlife-gsheet-cred.json'
SPREADSHEET_ID = '1XiNoDc2-hU8i8_GAEEUsqGmth2rF0mPVg1js_JySaAY'


BOOL_TRUE = 'TRUE'
BOOL_FALSE = 'FALSE'

_credentials = None
_client = None

def get_lumlife_client():
    global _client, _credentials
    if not _client:
        _credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_SECRET_FILE, SCOPES)
        _client = Client(_credentials)

    _client.login()
    return _client

class Client(gspread.Client):
    def login(self):
        """override gspread Client to check the 10 minutes."""
        if not self.auth.access_token or \
                (hasattr(self.auth, 'access_token_expired') and self.auth.access_token_expired) or\
                (self.auth.get_access_token().expires_in < 600):
            import httplib2

            http = httplib2.Http()
            self.auth.refresh(http)

        self.session.add_header('Authorization', "Bearer " + self.auth.access_token)

def record_filter(records, filt):
    if len(records) == 0 or filt is None or not isinstance(filt, dict):
        return records

    rec_keys = records[0].keys()
    filt_keys = filt.keys()

    for key in filt_keys:
        if key not in rec_keys:
            raise Exception('Filter: Key "%s" not found'%(key))

    results = []
    for record in records:
        results.append(record)
        for key in filt_keys:
            opt_code, parm = opt_parm(filt[key])
            if not opt_filt[opt_code](record[key], parm):
                del results[-1]
                break
    return results

def record_project(records, proj):
    if len(records) == 0 or proj is None or not isinstance(proj, dict):
        return records

    rec_keys = records[0].keys()
    proj_keys = proj.keys()

    for key in proj_keys:
        if key not in rec_keys:
            raise Exception('Project: Key "%s" not found'%(key))
        if proj[key] not in [0, 1]:
            raise Exception('Project: invalid value "$%s" for key "%s"'
                            %(str(proj[key]), key))

    for record in records:
        for k in rec_keys:
            if k not in proj_keys or proj[k] == 0:
                del record[k]
    return records

EQ = '$EQ'
NE = '$NE'
NOT = '$NOT'
ISIN = '$ISIN'
NOTIN = '$NOTIN'
HAS = '$HAS'
NOTHAS = '$NOTHAS'

def eq_filt(records, parm):
    return records == parm

def ne_filt(records, parm):
    return records != parm

def isin_filt(records, parm):
    return records in parm

def notin_filt(records, parm):
    return records not in parm

def has_filt(records, parm):
    return parm in records

def nothas_filt(records, parm):
    return parm not in records

def opt_parm(filt):
    if not isinstance(filt, dict):
        parm = filt
        return EQ, parm
    key = list(filt)[0]
    nestedkey, parm = opt_parm(filt[key])
    if nestedkey == EQ and key == ISIN:
        pass
    elif nestedkey == EQ and key == NE:
        pass
    elif nestedkey == EQ and key == NOT:
        key = NE
    elif nestedkey == ISIN and key == NOT:
        key = NOTIN
    elif nestedkey == EQ and key == HAS:
        pass
    elif nestedkey == HAS and key == NOT:
        key = NOTHAS
    elif nestedkey == EQ and key == NOTHAS:
        pass
    elif nestedkey == EQ and key == NOTIN:
        pass
    else:
        raise Exception("%s and %s cannot combined"%(key, nestedkey))
    return key, parm

opt_filt = {EQ:eq_filt,
            NE:ne_filt,
            ISIN:isin_filt,
            NOTIN:notin_filt,
            HAS:has_filt,
            NOTHAS:nothas_filt}


if __name__ == "__main__":
    pass
#     # print(opt_parm({NOT:{ISIN:['a','b','c']}}))
#     print(get_records({USER_FN:{NOT:{ISIN:["Khoa", "Ilya"]}}},{USER_FN:1, USER_ID:0}))