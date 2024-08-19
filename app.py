from flask import Flask
from routes import init_routes
from db_writer import db_write
import queue
import threading
from config import Config

my_queue = queue.Queue()

def start_working_thread():
    work_thread = threading.Thread(target=db_write, args=(Config.LOG_FILE, Config.LOG_DB_TABLE_CREATE_SQL, Config.LOG_INSERT_SQL, my_queue, ))
    work_thread.start()

app = Flask(__name__)

init_routes(app, my_queue)

if __name__ == '__main__':
    start_working_thread()
    app.run(debug=True) 