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

doctor:
	@docker info >/dev/null 2>&1 && echo 'docker: ok' || echo 'docker: DOWN (open Docker Desktop)'
	@docker compose exec -T db pg_isready -U papertrail >/dev/null 2>&1 && echo 'postgres: ok' || echo 'postgres: DOWN (run: docker compose up -d)'
	@python manage.py migrate --check >/dev/null 2>&1 && echo 'migrations: up to date' || echo 'migrations: PENDING or database unreachable'

packet:
	python manage.py export_packet
