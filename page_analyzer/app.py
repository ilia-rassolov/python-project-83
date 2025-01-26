from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
import os
from dotenv import load_dotenv
import psycopg2
from db import get_db, UrlRepository
from validator_db import validate


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
    url_data = request.form.to_dict()
    errors = validate(url_data)
    if errors:
        return render_template('index.html', errors=errors, url=url_data), 422
    repo.save(url_data)
    render_template('show.html', url=url_data, errors=errors), 422
    return redirect(url_for('/urls/<id>'))

@app.route('/urls/<id>')
def find_url(id):
    url = repo.find(id)
    return render_template('show.html', url=url)

@app.route('/urls')
def urls():
    urls = repo.get_entities()
    return render_template('urls.html', urls=urls)


if __name__ == '__main__':
    app.run()
