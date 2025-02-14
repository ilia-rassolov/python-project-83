from validators.url import url


def validate(url_data):
    errors = ""
    if not url(url_data, public=True):
        errors = "Некорректный URL"
    elif len(url_data) > 255:
        errors = "URL превышает 255 символов"
    return errors
