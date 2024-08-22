'''
I would like to implement such logic
1. check user/password, return token if ok
2. multiple tokens can exist, but only valid only within 1 min
3. check token valid/expire/not exists
4. use jsonify in flask package
'''

from flask import jsonify
import os
#import secrets

#import itsdangerous
from itsdangerous import URLSafeTimedSerializer  as Serializer, BadSignature, SignatureExpired

USERNAME=os.getenv("SMARTWEB_USER")
PASSWORD=os.getenv("SMARTWEB_PASSWORD")

#secret_key=secrets.token_hex(16), will cause problem when production web server create 3 instances
secret_key=os.getenv("SMARTWEB_KEY")

token_expire_in_sec=60

s=Serializer(secret_key)

def __gen_token(data)->str:
    return s.dumps(data)

"""
Return: {"result":True, "msg":""}
{"result":False, "msg":"unknown error"}
{"result":False, "msg":"bad signature"}
{"result":False, "msg":"token expired"}
"""

def verify_token(token:str)->dict:
    try:
        data = s.loads(token,  max_age=token_expire_in_sec)        
        if(data["user"] == USERNAME):
            return {"result":True, "msg":""}
        return {"result":False, "msg":"unknown error"}
    except BadSignature:
        return {"result":False, "msg":"bad signature"}
    except SignatureExpired:
        return {"result":False, "msg":"bad signature"}

def get_authenticate(user:str, password:str):
    if(USERNAME == user and PASSWORD == password):
        return True
    return False
    

def get_token (user:str)->str:
    return __gen_token({"user":user })