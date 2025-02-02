from validators.url import url


def validate(url_data):
    errors = None
    if not url(url_data):
        errors = "Некорректный URL"
    elif len(url_data) > 255:
        errors = "URL превышает 255 символов"
    return errors
