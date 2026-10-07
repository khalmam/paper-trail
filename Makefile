export DJANGO_SETTINGS_MODULE ?= config.settings.dev

db:
	docker compose up -d

migrate:
	python manage.py migrate

run:
	uvicorn config.asgi:application --reload --port 8000

test:
	pytest -q
