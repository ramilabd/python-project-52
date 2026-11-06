install:
	uv sync

dev:
	uv run python manage.py runserver

collectstatic:
	uv run python manage.py collectstatic --noinput

migrate:
	uv run python manage.py migrate

setup: install build-css collectstatic migrate

lint:
	uv run ruff check

build:
	./build.sh

render-start:
	gunicorn task_manager.wsgi

build-css:
	uv run python manage.py tailwind build --force

messages:
	uv run python manage.py makemessages -l ru

compile-messages:
	uv run python manage.py compilemessages