def validate(url_data):
    errors = {}
    if not url_data.get('name'):
        errors['title'] = "Can't be blank"
    if int(url_data.get('price')) < 0:
        errors['price'] = "Can't be negative"
    return errors