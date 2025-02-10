from urllib.parse import urlparse
from requests import HTTPError
import requests
from bs4 import BeautifulSoup


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
        tag = soup.meta
        description = tag.get("content", '') if tag.get("name") == "description" else ''
        title = soup.title.string if soup.title else ''
        h1 = soup.h1.string if soup.h1 else ''
        new_check = {"url_id": url['id'], "status_code": status_code, "h1": h1,
                     "title": title, "description": description}
        return new_check


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
