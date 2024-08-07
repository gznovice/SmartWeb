import sqlite3
import queue
import time

"""
import os 
don't need this, since connect function will create the file if it does not exist
"""

def db_write(db_file:str, create_sql:str, insert_sql:str, myqueue:queue.Queue):
    conn = sqlite3.connect(db_file, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(create_sql)
    #conn.commit()
    #don't need to commit since we shall write later
    
    batch_cnt = 0
    while True:        
        try:
            ip_address, access_time = myqueue.get(True, timeout=5)
            cursor.execute(insert_sql, (ip_address, access_time))
            batch_cnt += 1
        except queue.Empty:
            if batch_cnt > 0 :
                conn.commit()
                batch_cnt = 0
            time.sleep(1)            
        except Exception as e:
            pass
            ## should write to log
    #conn.Close()
    

