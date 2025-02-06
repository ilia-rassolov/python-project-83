from flask import (Flask, redirect, render_template, request,
                   url_for, flash, get_flashed_messages)
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import DictCursor

from .db import UrlRepository
from .validator import validate


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = True
DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages,)


@app.route('/urls')
def urls():
    with conn.cursor(cursor_factory=DictCursor) as cur:
        repo = UrlRepository(cur)
        urls = repo.get_content()
        cur.close()
    return render_template('urls.html', urls=urls,)


@app.route('/urls/<id>')
def url_show(id):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        repo = UrlRepository(cur)
        url = repo.find_url(id)
        cur.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template('show.html', url=url, messages=messages,)


@app.post('/')
def add_url():
    url_data = request.form.get("url")
    errors = validate(url_data)
    if errors:
        flash(f"{errors}", 'error')
        return redirect(url_for('index'), code=302)
    with conn.cursor(cursor_factory=DictCursor) as cur:
        repo = UrlRepository(cur)
        id_existing = repo.find_id(url_data)
        if id_existing:
            id = id_existing
            flash('Страница уже существует', 'warning')
        else:
            id = repo.save(url_data)
            conn.commit()
            flash('Страница успешно добавлена', 'success')
        url = repo.find_url(id)

    render_template('show.html', url=url,), 422
    return redirect(url_for('url_show', id=id), code=302)


if __name__ == '__main__':
    app.run()
