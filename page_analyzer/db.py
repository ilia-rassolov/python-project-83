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
            WITH get_last_check_by_url AS (
            SELECT
                urls.id AS id_url,
                urls.name AS name_url,
                MAX(url_checks.id) AS last_check
            FROM urls
            LEFT JOIN url_checks
                ON
                    urls.id = url_checks.url_id
            GROUP BY urls.id , urls.name
            )

            SELECT
                glsbu.name_url,
                glsbu.id_url,
                glsbu.last_check,
                url_checks.status_code AS last_status_code,
                url_checks.description,
                url_checks.h1,
                url_checks.title,
                url_checks.created_at AS last_created_at
            FROM get_last_check_by_url AS glsbu
            LEFT JOIN url_checks
                ON
                    glsbu.id_url = url_checks.url_id
            WHERE glsbu.last_check = url_checks.id OR glsbu.last_check IS NULL
            ORDER BY glsbu.id_url DESC;""")
            content = [dict(row) for row in curs]
            for row in content:
                for k, v in row.items():
                    if v is None:
                        row[k] = ""
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
