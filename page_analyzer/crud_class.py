import psycopg2


class CRUD:
    def __init__(self, db_url):
        self.db_url = db_url

    def open_connection(self):
        try:
            self.conn = psycopg2.connect(self.db_url)
        except Exception:
            print('Can`t establish connection to database')
        return self.conn

    def commit_db(self):
        return self.conn.commit()

    def close_connection(self):
        self.conn.close()
