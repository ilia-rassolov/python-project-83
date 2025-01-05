from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return '<a href="/">Page analyzer/</a>'

__all__ = ('app',)

if __name__ == '__main__':
    app.run()
