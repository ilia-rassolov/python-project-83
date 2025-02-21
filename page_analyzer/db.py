import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import OperationalError, DatabaseError
import logging


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("SELECT id, name FROM urls ORDER BY id DESC")
            all_urls = [dict(row) for row in curs]
        content = []
        for url in all_urls:
            row = dict()
            with self.conn.cursor(cursor_factory=DictCursor) as curs:
                curs.execute(f"""SELECT
                                  MAX(id) FROM url_checks
                                  WHERE url_id = {url['id']};""")
                check_id = curs.fetchone()[0]
            if check_id:
                with self.conn.cursor(cursor_factory=DictCursor) as curs:
                    curs.execute(f"""SELECT
                                     id AS id_check,
                                     created_at AS last_created_at,
                                     status_code AS last_status_code
                                     FROM url_checks WHERE id = {check_id};""")
                    row = dict(curs.fetchone())
            row['id_url'] = url['id']
            row['name_url'] = url['name']
            content.append(row)
        return content

    def find_url(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("SELECT * FROM urls WHERE id = %s", (id,))
            row = curs.fetchone()
        return dict(row) if row else None

    def save_url(self, name):
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("""INSERT INTO urls (name) VALUES
            (%s) RETURNING id""", (name,))
            id = curs.fetchone()['id']
        return id

    def find_id(self, name):
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("SELECT id FROM urls WHERE name = %s", (name,))
            id = curs.fetchone()['id']
        return id


class CheckRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_checks(self, url_id):
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("""SELECT
                             * FROM url_checks
                             WHERE url_id = %s ORDER BY id DESC""", (url_id,))
            return [dict(row) for row in curs]

    def save_check(self, new_check):
        placeholders = ', '.join(f'%({k})s' for k in new_check)
        query = (f"""INSERT INTO url_checks
                  ({', '.join(new_check)}) VALUES ({placeholders})""")
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute(query, new_check)


class DBClient:
    def __init__(self, db_url):
        self.db_url = db_url

    def open_connection(self):
        try:
            self.conn = psycopg2.connect(self.db_url)
        except OperationalError:
            logging.error('Unable to establish connection to database!')
        except DatabaseError:
            logging.error('The database is not working correctly!')
        return self.conn

    def commit_db(self):
        return self.conn.commit()

    def close_connection(self):
        return self.conn.close()
