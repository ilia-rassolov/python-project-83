import psycopg2
from psycopg2.extras import DictCursor


class CRUD:
    def __init__(self, db_url):
        self.conn = psycopg2.connect(db_url)

    def open_connection(self):
        self.curs = self.conn.cursor(cursor_factory=DictCursor)
        return self.curs

    def commit_db(self):
        return self.conn.commit()

    def close_connection(self):
        self.curs.close()
        self.conn.close()
