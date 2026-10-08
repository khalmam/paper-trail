export DJANGO_SETTINGS_MODULE ?= config.settings.dev

db:
	docker compose up -d

migrate:
	python manage.py migrate

run:
	uvicorn config.asgi:application --reload --port 8000

test:
	pytest -q

seed:
	python manage.py seed_demo

tamper:
	python manage.py tamper_demo --seq 1

verify:
	python manage.py verify_ledger
