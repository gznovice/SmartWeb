from flask import request, jsonify, make_response, render_template
from dns import dns_lookup
import requests
import json
from functools import wraps
import os
import google.generativeai as genai
import sqlite3
#from config import Config
from datetime import datetime
import token_man
import queue

CLOUDAPI_KEY=os.getenv("CLOUDFLARE_KEY")
DNS_ZONE_ID=os.getenv("DNS_ZONE_ID")
HOME_ID=os.getenv("HOME_ID")
HOME_DNS=os.getenv("HOME_DNS")

RECORDS_URL=f"https://api.cloudflare.com/client/v4/zones/{DNS_ZONE_ID}/dns_records/"
UPDATE_URL=f"{RECORDS_URL}{HOME_ID}"

SUCCESS_RECORDS_DATA_TEMPLATE = '''{{
    "STATUS"=true,
    "DATA"={}
}}'''

ERROR_RECORDS_DATA_TEMPLATE = '''{{
    "STATUS"=false,
    "DATA"=[]
}}'''

headers = {
    'Authorization':f'Bearer {CLOUDAPI_KEY}',
    'Content-type':'application/json'
}

def   run_db_sql(dbUrl, dbSql, datas = ()):
    conn = sqlite3.connect(dbUrl)
    cursor = conn.cursor()
    cursor.execute(dbSql, datas)
    conn.commit()
    conn.close()

#return json of records
def dns_record_list(dns_name:str)->str:    
    response=requests.get(RECORDS_URL, headers=headers)
    try:
        response.raise_for_status()
        data=response.json()
        records=[]
        if data['result']:
            for record in data['result']:
                if dns_name=='' or dns_name == record['name']:
                    records.append(record)
            
        else:
            print("error from cloudflare server")
            return ERROR_RECORDS_DATA_TEMPLATE    
        records_str=json.dumps(records)
        
        return SUCCESS_RECORDS_DATA_TEMPLATE.format(records_str)

    except requests.exceptions.RequestException as e:
       # print("error found when connect to cloudflare server:"+str(e)+"_"+str(headers))
        print("error found when connect to cloudflare server:"+"_"+str(headers))
        return ERROR_RECORDS_DATA_TEMPLATE


def update_cloudflare_dns(ip:str):
    LAST_UPDATE_IP = "LAST_UPDATE_IP"
    if(os.getenv(LAST_UPDATE_IP, '') == ip):
        return ip + " updated"
    data_to_patch=f"""{{
        "content":"{ip}",
        "name":"{HOME_DNS}",
        "proxied":false,
        "type":"A",
        "ttl":200
    }}"""
    
    response = requests.patch(UPDATE_URL, headers=headers, data=data_to_patch)
    if response.status_code==200:
        os.putenv(LAST_UPDATE_IP, ip)
        return ip + " updated"
    else:       
        return "ip update failed"

# Authentication decorator, verify the simple authentication
def __authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):   
        auth = request.authorization       
        if(auth and token_man.get_authenticate(auth.username, auth.password)):
            return f(*args, **kwargs)
        return make_response('Could not verify your identification', 401, 
                             {'WWW-Authenticate': 'Basic realm="Login Requred"'})
    return decorated

# Authentication decorator, verify the token in the header
def __authenticate1(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("token")
        if(token and token_man.verify_token(token)["result"]):
            return f(*args, **kwargs)
        return make_response('Unauthorized', 401)
    return decorated

def init_routes(app, my_queue:queue.Queue):
    @app.route('/')
    def hello():
        return 'Hello World!'
    
    @app.route('/dns', methods=['GET', 'POST'])
    def dnslookup():
        if(request.method == 'POST'):
            if(request.form):
                domain = request.form.get('domain')
                method = request.form.get('method')
                return dns_lookup(domain, method)
        else:
            return render_template('dnsform.html')
    
    @app.route('/joke')
    def joke():
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=[])        
        prompt = "Tell me a everyday joke."
        response = chat.send_message(prompt)        
        return response.text
    
    @app.route('/verifytoken/<token>')
    def verify_token(token):
        return token_man.verify_token(token)


    # protected
    @app.route('/gettoken')
    @__authenticate
    def get_token():        
        auth = request.authorization        
        return token_man.get_token(auth.username)
    

    # protected
    @app.route('/updatedns')
    @__authenticate1
    def updatedns():
        client_ip = request.headers.get('X-Real-IP')
        if not client_ip:
            client_ip = request.remote_addr     
        return update_cloudflare_dns(client_ip)

    # protected
    @app.route('/cfdns')
    @app.route('/cfdns/')
    @app.route('/cfdns/<dns_name>')
    @__authenticate1
    def listdns(dns_name=''):
        client_ip = request.remote_addr     
        return dns_record_list(dns_name)
    
    @app.route('/log')
    def log():
        client_ip = request.remote_addr     
        my_queue.put((client_ip, datetime.now()), block=True)  
        
#if not os.path.exists(Config.LOG_FILE):
            #run_db_sql(Config.LOG_FILE, Config.LOG_DB_TABLE_CREATE_SQL)
###        run_db_sql(Config.LOG_FILE, Config.LOG_INSERT_SQL, (client_ip, datetime.now()))

        return "ip logged"     
    
    @app.route('/route_name')
    def method_name():
        pass