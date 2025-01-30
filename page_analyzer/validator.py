from validators import url


def validate(url_data):
    errors = None
    if not url(url_data.get('name')):
        errors = "Некорректный URL"
    elif len(url_data.get('name')) > 255:
        errors = "URL превышает 255 символов"
    return errors

print(validate({'name': ""}))