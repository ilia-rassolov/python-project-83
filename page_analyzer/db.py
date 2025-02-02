from psycopg2.extras import DictCursor
from urllib.parse import urlparse


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls ORDER BY id DESC")
            return [dict(row) for row in cur]

    def find_url(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def save(self, url_data):
        hostname = urlparse(url_data).hostname
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO urls (name) VALUES
                (%s) RETURNING id""",
                (hostname,)
            )
            id = cur.fetchone()[0]
        self.conn.commit()
        return id

    def find_id(self, url_data):
        hostname = urlparse(url_data).hostname
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name FROM urls")
            urls = cur.fetchall()
            for id, name in urls:
                if name == hostname:
                    return id
