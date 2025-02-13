from validators.url import url
from validators import ValidationError


def validate(url_data):
    errors = ""
    try:
        url(url_data)
    except ValidationError:
        errors = "Некорректный URL"
    if len(url_data) > 255:
        errors = "URL превышает 255 символов"
    return errors
