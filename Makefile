# AIMOS — convenience targets (requires Docker Compose + make)

.PHONY: up down logs seed validate e2e openapi

up:
	@chmod +x setup.sh 2>/dev/null || true
	./setup.sh

down:
	docker compose down

logs:
	docker compose logs -f api worker

seed:
	docker compose exec -T api python /app/scripts/db_init.py

validate:
	python3 scripts/validate_env.py

e2e:
	python3 scripts/test_full_campaign.py

openapi:
	python3 scripts/export_openapi.py
