from flask import Flask
import os
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return '<a href="/">Page analyzer</a>'


if __name__ == '__main__':
    app.run()
