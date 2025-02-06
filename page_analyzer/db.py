from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import DictCursor


class UrlRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_content(self):
        self.cursor.execute("SELECT * FROM urls ORDER BY id DESC")
        return [dict(row) for row in self.cursor]

    def find_url(self, id):
        self.cursor.execute("SELECT * FROM urls WHERE id = %s", (id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def save(self, url_data):
        hostname = urlparse(url_data).hostname
        self.cursor.execute(
            """INSERT INTO urls (name) VALUES
            (%s) RETURNING id""",
            (hostname,)
            )
        id = self.cursor.fetchone()[0]
        return id

    def find_id(self, url_data):
        hostname = urlparse(url_data).hostname
        self.cursor.execute("SELECT id, name FROM urls")
        urls = self.cursor.fetchall()
        for row in urls:
            url = dict(row)
            if url["name"] == hostname:
                return url["id"]


class UrlCRUD:
    def __init__(self, DB_URL):
        self.db = DB_URL

    def open_connection(self):
        try:
            self.conn = psycopg2.connect(self.db)
        except:
            print('Can`t establish connection to database')
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        return self.cursor

    def close_connection(self):
        return self.cursor.close()

    def commit_db(self):
        return self.conn.commit()
