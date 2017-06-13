import functools
from flask import request, Response

from repository import pwdRepository as PWDR

def body_field_validation(*key_names):
    def validate(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwds):
            for key_name in key_names:
                if key_name not in request.json:
                    return Response(response='"%s" key needed in json body'%(key_name), status=400)
            return f(*args, **kwds)
        return decorated_function
    return validate

def header_field_validation(*field_names):
    def validate(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwds):
            for field_name in field_names:
                if field_name not in request.headers:
                    return Response(response='"%s" key needed in header'%(field_name), status=400)
            return f(*args, **kwds)
        return decorated_function
    return validate

def lumlife_key_validation(serv_name):
    def validate(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwds):
            if 'lumlife_key' not in request.headers:
                return Response(response='"lumlife_key" key needed in header', status=400)
            pwd = PWDR.get_pwds(filt={PWDR.PWD_SV_NAME:serv_name})[0]
            lumlife_key = pwd[PWDR.PWD_SV_KEY]
            if request.headers['lumlife_key'] != lumlife_key:
                return Response(response='invalid lumlife key', status=403)
            return f(*args, **kwds)
        return decorated_function
    return validate