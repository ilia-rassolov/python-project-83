from validators.url import url
from urllib.parse import urlparse


def validate(url_data):
    errors = ""
    if not url(url_data):
        errors = "Некорректный URL"
    elif len(url_data) > 255:
        errors = "URL превышает 255 символов"
    return errors


def get_name(url):
    scheme = urlparse(url).scheme
    hostname = urlparse(url).hostname
    name = f"{scheme}://{hostname}"
    return name
