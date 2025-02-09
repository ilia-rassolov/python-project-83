from flask import (Flask, redirect, render_template, request,
                   url_for, flash, get_flashed_messages)
import os
from dotenv import load_dotenv

from .db import UrlRepository, CRUD, CheckRepository
from .validator import validate


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = True
DATABASE_URL = os.getenv('DATABASE_URL')

conn = CRUD(DATABASE_URL)


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages,)


@app.route('/urls')
def urls():
    cursor = conn.open_connection()
    repo_urls = UrlRepository(cursor)
    content = repo_urls.get_content()
    conn.close_connection()
    return render_template('urls.html', content=content,)


@app.route('/urls/<id>')
def url_show(id):
    cursor = conn.open_connection()
    repo_urls = UrlRepository(cursor)
    url = repo_urls.find_url(id)

    repo_checks = CheckRepository(cursor)
    checks = repo_checks.get_checks(id)
    conn.close_connection()
    messages = get_flashed_messages(with_categories=True)
    return render_template('show.html',
                           url=url, checks=checks, messages=messages,)


@app.post('/')
def add_url():
    url_data = request.form.get("url")
    errors = validate(url_data)
    if errors:
        flash(f"{errors}", 'error')
        return redirect(url_for('index'), code=302)
    cursor = conn.open_connection()
    repo_urls = UrlRepository(cursor)
    id_existing = repo_urls.find_id(url_data)
    if id_existing:
        id = id_existing
        flash('Страница уже существует', 'repeat')
    else:
        id = repo_urls.save_url(url_data)
        conn.commit_db()
        flash('Страница успешно добавлена', 'success')
    url = repo_urls.find_url(id)
    conn.close_connection()
    render_template('show.html', url=url,), 422
    return redirect(url_for('url_show', id=id), code=302)


@app.post('/urls/<id>/checks')
def add_check(id):
    new_check = {"url_id": id, "status_code": "777", "h1": "заголовок сайта",
                 "title": "заголовок документа", "description": "описание"}
    cursor = conn.open_connection()
    repo_checks = CheckRepository(cursor)
    repo_checks.save_check(new_check)
    conn.commit_db()
    conn.close_connection()
    flash('Страница успешно проверена', 'success_check')
    return redirect(url_for('url_show', id=id), code=302)


if __name__ == '__main__':
    app.run()
