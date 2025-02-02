from flask import Flask, redirect, render_template, request, url_for
import os
from dotenv import load_dotenv
import psycopg2
from db import UrlRepository
from validator import validate


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = True
DATABASE_URL = os.getenv('DATABASE_URL')


conn = psycopg2.connect(DATABASE_URL)
repo = UrlRepository(conn)


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/')
def add_url():
    url_data = request.form.get("url")
    errors = validate(url_data)
    if errors:
        return render_template('index.html', errors=errors), 422
    id = repo.find_id(url_data)
    if id:
        render_template('show.html', repeat=True), 422
        return redirect(url_for(f'/urls/<{id}>'), code=302)
    id = repo.save(url_data)
    url = repo.find_url(id)
    render_template('show.html', url=url, add_new=True), 422
    return redirect(url_for(f'/urls/{id}'), code=302)


@app.route('/urls/<id>')
def find(id):
    url = repo.find_url(id)
    return render_template('show.html', url=url)


@app.route('/urls')
def urls():
    urls = repo.get_content()
    return render_template('urls.html', urls=urls)


if __name__ == '__main__':
    app.run()
