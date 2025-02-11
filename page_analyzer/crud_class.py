import psycopg2
from psycopg2.extras import DictCursor


class CRUD:
    def __init__(self, DB_URL):
        self.db = DB_URL

    def open_connection(self):
        try:
            self.conn = psycopg2.connect(self.db)
        except Exception:
            print('Can`t establish connection to database')
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        return self.cursor

    def close_connection(self):
        return self.cursor.close()

    def commit_db(self):
        return self.conn.commit()
