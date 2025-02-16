from flask import (Flask, redirect, render_template, request,
                   url_for, flash, get_flashed_messages)
import os
from dotenv import load_dotenv

from .db import UrlRepository, CheckRepository
from .validator import validate
from .crud import CRUD


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = os.getenv('DEBUG')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages,)


@app.route('/urls')
def urls():
    db = CRUD(DATABASE_URL)
    conn = db.open_connection()
    repo_urls = UrlRepository(conn)
    content = repo_urls.get_content()
    db.close_connection()
    return render_template('urls.html', content=content,)


@app.post('/urls')
def add_url():
    url_data = request.form.get("url")
    errors = validate(url_data)
    if errors:
        flash(f"{errors}", 'error')
        render_template('index.html'), 422
        return redirect(url_for('index'), code=302)
    db = CRUD(DATABASE_URL)
    conn = db.open_connection()
    repo_urls = UrlRepository(conn)
    id_existing = repo_urls.find_id(url_data)
    if id_existing:
        id = id_existing
        flash('Страница уже существует', 'repeat')
    else:
        id = repo_urls.save_url(url_data)
        db.commit_db()
        flash('Страница успешно добавлена', 'success')
    url = repo_urls.find_url(id)
    db.close_connection()
    return redirect(url_for('url_show', url=url, id=id), code=302)


@app.route('/urls/<id>')
def url_show(id):
    db = CRUD(DATABASE_URL)
    conn = db.open_connection()
    repo_urls = UrlRepository(conn)
    url = repo_urls.find_url(id)

    repo_checks = CheckRepository(conn)
    checks = repo_checks.get_checks(id)
    db.close_connection()
    messages = get_flashed_messages(with_categories=True)
    return render_template('show.html',
                           url=url, checks=checks, messages=messages,)


@app.post('/urls/<id>/checks')
def add_check(id):
    db = CRUD(DATABASE_URL)
    conn = db.open_connection()
    repo_urls = UrlRepository(conn)
    url = repo_urls.find_url(id)
    new_check = repo_urls.make_check(url)
    if new_check is None:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_show', id=id), code=302)
    repo_checks = CheckRepository(conn)
    repo_checks.save_check(new_check)
    db.commit_db()
    db.close_connection()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_show', id=id), code=302)


if __name__ == '__main__':
    app.run()
