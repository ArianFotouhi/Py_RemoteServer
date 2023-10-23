import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('data/mobile_db.db')
        self.cursor = self.conn.cursor()

    def create_table(self):

        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS mobile_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    lounge TEXT)
        ''')
    def commit_table(self, name, email, lounge):
        self.cursor.execute('INSERT INTO mobile_table (name, email, lounge) VALUES (?,?,?)', 
        (name, email, lounge,))
        
        self.conn.commit()

    def fetch_table(self, query = 'SELECT * FROM mobile_table'):
        self.cursor.execute(query)
        history = self.cursor.fetchall()
        return history

    def close_db(self):
        self.conn.close()

