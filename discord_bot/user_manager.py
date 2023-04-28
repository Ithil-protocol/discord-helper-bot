import sqlite3
import time

class UserManager:
    def __init__(self, db_path, throttle):
        self.throttle_time = int(throttle)
        self.conn = sqlite3.connect(db_path)
        self._init_db()
        
    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (address TEXT PRIMARY KEY, token VARCHAR, last_interaction INTEGER)''')
        self.conn.commit()


    def check_interaction(self, address, token):
        c = self.conn.cursor()
        current_time = int(time.time())
        user = c.execute('''SELECT * FROM users WHERE address=? AND token=?''', (address, token)).fetchone()
        if user and current_time - user[2] < self.throttle_time:
            return False
        else:
            #c.execute('''REPLACE INTO users (address, token, last_interaction) VALUES (?, ?, ?)''',
            #          (address, token, current_time))
            #self.conn.commit()
            return True
