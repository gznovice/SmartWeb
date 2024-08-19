class Config:
    DEBUG = False
    LOG_FILE = "access.db"
    LOG_DB_TABLE_CREATE_SQL = '''CREATE TABLE IF NOT EXISTS IPACCESS(
        id INTEGER PRIMARY KEY,
        ip TEXT NOT NULL,
        access_timestamp INTEGER NOT NULL
    )'''

    LOG_INSERT_SQL = '''INSERT INTO IPACCESS(ip, access_timestamp) VALUES(?, ?)
'''
    DNS_UPDATE_LOG = "dns.log"
     