import sqlite3
import time
import json

class UserManager:
    def __init__(self, db_path, throttle):
        self.throttle_time = int(throttle)
        self.conn = sqlite3.connect(db_path)
        self._init_db()
        
    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (n INT PRIMARY KEY, address VARCHAR, token VARCHAR, last_interaction INTEGER)''')
        self.conn.commit()


    def check_interaction(self, address, token):
        current_time = int(time.time())
        c = self.conn.cursor()
        user = c.execute('''SELECT * FROM users WHERE address=? AND token=?''', (address, token)).fetchone()
        if user and current_time - user[2] < self.throttle_time:
            return False
        else:
            return True


    def update_interaction(self, address, token):
        current_time = int(time.time())
        c = self.conn.cursor()
        c.execute('''REPLACE INTO users (address, token, last_interaction) VALUES (?, ?, ?)''',
                      (address, token, current_time))
        self.conn.commit()


    def dump_db(self):
        c = self.conn.cursor()
        data = c.execute('''SELECT * FROM users''').fetchall()
        self.conn.commit()

        return data
