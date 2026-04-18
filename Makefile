DOCKER_ENV_FILE ?= .env.docker.local
COMPOSE = docker compose --env-file $(DOCKER_ENV_FILE)

.PHONY: docker-env docker-build docker-up docker-down docker-logs docker-ps

docker-env:
	@if [ -f "$(DOCKER_ENV_FILE)" ]; then \
		echo "$(DOCKER_ENV_FILE) already exists"; \
	else \
		cp .env.docker.example $(DOCKER_ENV_FILE); \
		echo "Created $(DOCKER_ENV_FILE) from .env.docker.example"; \
	fi

docker-build: docker-env
	$(COMPOSE) build

docker-up: docker-env
	$(COMPOSE) up --build

docker-down: docker-env
	$(COMPOSE) down

docker-logs: docker-env
	$(COMPOSE) logs -f

docker-ps: docker-env
	$(COMPOSE) ps

