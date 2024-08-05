from flask import request
import os
import google.generativeai as genai
import sqlite3
from config import Config
from datetime import datetime


def run_db_sql(dbUrl, dbSql, datas = ()):
    conn = sqlite3.connect(dbUrl)
    cursor = conn.cursor()
    cursor.execute(dbSql, datas)
    conn.commit()
    conn.close()




def init_routes(app):
    @app.route('/')
    def hello():
        return 'Hello World!'
    
    @app.route('/joke')
    def joke():
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=[])        
        prompt = "Tell me a everyday joke."
        response = chat.send_message(prompt)        
        return response.text


    
    @app.route('/log')
    def log():
        client_ip = request.remote_addr        
        if not os.path.exists(Config.LOG_FILE):
            run_db_sql(Config.LOG_FILE, Config.LOG_DB_TABLE_CREATE_SQL)
        run_db_sql(Config.LOG_FILE, Config.LOG_INSERT_SQL, (client_ip, datetime.now()))
        return "ip logged"
    
    @app.route('/route_name')
    def method_name():
        pass