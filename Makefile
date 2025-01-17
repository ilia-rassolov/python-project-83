PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app

install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer.app:app run

lint:
	uv run flake8 page_analyzer

test:
	uv run pytest

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app


