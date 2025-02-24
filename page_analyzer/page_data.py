import requests
from requests import HTTPError
from requests.exceptions import RequestException
from bs4 import BeautifulSoup


def get_page_data(url):
    name = url['name']
    try:
        page = requests.get(name, timeout=1)
        page.raise_for_status()
    except (RequestException, HTTPError):
        return None
    status_code = page.status_code
    html_doc = page.text
    soup = BeautifulSoup(html_doc, 'lxml')
    title = soup.title.string if soup.title else ""
    h1 = soup.h1.string if soup.h1 else ""
    description = ""
    tags = soup.find_all('meta')
    for tag in tags:
        if tag.get("name") == "description":
            description = tag.get("content", "")
            break
    return {"url_id": url['id'], "status_code": status_code, "h1": h1[:254],
            "title": title[:254], "description": description}
