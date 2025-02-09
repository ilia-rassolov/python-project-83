from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import DictCursor


class UrlRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_content(self):
        self.cursor.execute("SELECT id, name FROM urls ORDER BY id DESC")
        all_urls = [dict(row) for row in self.cursor]
        content = []
        for url in all_urls:
            row = dict()
            self.cursor.execute(f"""SELECT
                                 MAX(id) FROM url_checks
                                 WHERE url_id = {url['id']};""")
            check_id = self.cursor.fetchone()[0]
            if check_id:
                self.cursor.execute(f"""SELECT
                                     id AS id_check,
                                     created_at AS last_created_at,
                                     status_code AS last_status_code
                                     FROM url_checks WHERE id = {check_id};""")
                row = dict(self.cursor.fetchone())
            row['id_url'] = url['id']
            row['name_url'] = url['name']
            content.append(row)
        return content

    def find_url(self, id):
        self.cursor.execute("SELECT * FROM urls WHERE id = %s", (id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def save_url(self, url_data):
        scheme = urlparse(url_data).scheme
        hostname = urlparse(url_data).hostname
        name = f"{scheme}://{hostname}"
        self.cursor.execute(
            """INSERT INTO urls (name) VALUES
            (%s) RETURNING id""",
            (name,)
            )
        id = self.cursor.fetchone()[0]
        return id

    def find_id(self, url_data):
        scheme = urlparse(url_data).scheme
        hostname = urlparse(url_data).hostname
        name = f"{scheme}://{hostname}"
        self.cursor.execute("SELECT id, name FROM urls")
        urls = self.cursor.fetchall()
        for row in urls:
            url = dict(row)
            if url["name"] == name:
                return url["id"]


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


class CheckRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_checks(self, url_id):
        self.cursor.execute("""SELECT
                             * FROM url_checks
                             WHERE url_id = %s ORDER BY id DESC""", (url_id,))
        return [dict(row) for row in self.cursor]

    def save_check(self, new_check):
        placeholders = ', '.join(f'%({k})s' for k in new_check)
        query = (f"""INSERT INTO url_checks
                  ({', '.join(new_check)}) VALUES ({placeholders})""")
        self.cursor.execute(query, new_check)
