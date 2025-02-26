import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import OperationalError, DatabaseError
import logging


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("""
            SELECT
                urls.id AS url_id,
                urls.name AS url_name
            FROM urls
            ORDER BY urls.id DESC;""")
            content = [dict(row) for row in curs]
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("""
            SELECT
                DISTINCT  ON(url_id)
                url_id,
                status_code,
                created_at
            FROM  url_checks
            ORDER BY url_id, status_code, created_at DESC;""")
            checks = [dict(row) for row in curs]
        for url in content:
            for check in checks:
                if url["url_id"] == check["url_id"]:
                    url["last_created_at"] = check["created_at"]
                    url["last_status_code"] = check["status_code"]
                    break
        return content

    def get_url_by_id(self, id):
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

    def get_id_by_name(self, name):
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("SELECT id FROM urls WHERE name = %s", (name,))
            try:
                id = curs.fetchone()['id']
            except TypeError:
                id = None
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
        self.conn = None

    def open_connection(self):
        try:
            self.conn = psycopg2.connect(self.db_url)
        except (OperationalError, DatabaseError) as err:
            logging.error(err)
        return self.conn

    def commit_db(self):
        return self.conn.commit()

    def close_connection(self):
        return self.conn.close()
