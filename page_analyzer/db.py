from urllib.parse import urlparse
from requests import HTTPError
import requests
from bs4 import BeautifulSoup
from psycopg2.extras import DictCursor


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

    def save_url(self, url_data):
        scheme = urlparse(url_data).scheme
        hostname = urlparse(url_data).hostname
        name = f"{scheme}://{hostname}"

        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("""INSERT INTO urls (name) VALUES
            (%s) RETURNING id""",
                         (name,)
                         )
            id = curs.fetchone()[0]
        return id

    def find_id(self, url_data):
        scheme = urlparse(url_data).scheme
        hostname = urlparse(url_data).hostname
        name = f"{scheme}://{hostname}"

        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("SELECT id, name FROM urls")
            urls = curs.fetchall()
        for row in urls:
            url = dict(row)
            if url["name"] == name:
                return url["id"]

    def make_check(self, url):
        name = url['name']
        resp = requests.get(name)
        try:
            resp.raise_for_status()
        except HTTPError:
            return None
        status_code = resp.status_code
        html_doc = resp.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        title = soup.title.string if soup.title else ""
        h1 = soup.h1.string if soup.h1 else ""
        description = ""
        tags = soup.find_all('meta')
        for tag in tags:
            if tag.get("name") == "description":
                description = tag.get("content", "")
                break
        new_check = {"url_id": url['id'], "status_code": status_code, "h1": h1,
                     "title": title, "description": description}
        return new_check


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
