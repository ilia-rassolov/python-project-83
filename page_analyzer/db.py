from psycopg2.extras import DictCursor
import psycopg2


def get_db(app):
    return psycopg2.connect(app.config['DATABASE_URL'])

class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls")
            return [dict(row) for row in cur]

    def find(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_entities(self):
        with self.conn.cursor(row_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls")
            return [dict(row) for row in cur]

    def save(self, url):
        if 'id' not in url or not url['id']:
            with self.conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO url (name) VALUES
                    (%s) RETURNING id""",
                    (url['name'])
                )
                id = cur.fetchone()[0]
                url['id'] = id
            self.conn.commit()

