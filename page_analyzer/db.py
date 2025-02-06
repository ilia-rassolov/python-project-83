from urllib.parse import urlparse
import psycopg2
import os


DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


class UrlRepository:
    def __init__(self, cur):
        self.cur = cur

    def get_content(self):
        self.cur.execute("SELECT * FROM urls ORDER BY id DESC")
        return [dict(row) for row in self.cur]

    def find_url(self, id):
        self.cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
        row = self.cur.fetchone()
        return dict(row) if row else None

    def save(self, url_data):
        hostname = urlparse(url_data).hostname
        self.cur.execute(
            """INSERT INTO urls (name) VALUES
            (%s) RETURNING id""",
            (hostname,)
            )
        id = self.cur.fetchone()[0]
        return id

    def find_id(self, url_data):
        hostname = urlparse(url_data).hostname
        self.cur.execute("SELECT id, name FROM urls")
        urls = self.cur.fetchall()
        for row in urls:
            url = dict(row)
            if url["name"] == hostname:
                return url["id"]
