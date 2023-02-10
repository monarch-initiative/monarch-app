RUN = poetry -C backend/ run
VERSION = $(shell cd backend && poetry version -s)
ROOTDIR = $(shell pwd)


### Help ###

.PHONY: help
help:
	@echo "╭───────────────────────────────────────────────────────────╮"
	@echo "│ Makefile for Monarch API                                  │"
	@echo "│ Usage:                                                    │"
	@echo "│     make <target>                                         │"
	@echo "│                                                           │"
	@echo "│ Targets:                                                  │"
	@echo "│     fresh               Clean and install everything      │"
	@echo "│     all                 Install everything                │"
	@echo "│     install             Install backend and frontend      │"
	@echo "│     install-backend     Install backend                   │"
	@echo "│     install-frontend    Install frontend                  │"
	@echo "│     model               Generate model files              │"
	@echo "│     docs                Generate documentation            │"
	@echo "│     dev-frontend        Run frontend in development mode  │"
	@echo "│     dev-backend         Run backend in development mode   │"
	@echo "│     docker-build        Build docker image                │"
	@echo "│     docker-push         Push docker image                 │"
	@echo "│     clean               Clean up build artifacts          │"
	@echo "│     clobber             Clean up generated files          │"
	@echo "│     lint                Lint all code                     │"
	@echo "│     lint-backend        Lint backend code                 │"
	@echo "│     lint-frontend       Lint frontend code                │"
	@echo "│     format              Format all code                   │"
	@echo "│     format-backend      Format backend code               │"
	@echo "│     format-frontend     Format frontend code              │"
	@echo "│     help                Print this help message           │"
	@echo "╰───────────────────────────────────────────────────────────╯"

### Installation and Setup ###

.PHONY: fresh
fresh: clean clobber all


.PHONY: all
all: install model docs


.PHONY: install
install: install-backend install-frontend


.PHONY: install-backend
install-backend:
	cd backend && \
		poetry install


.PHONY: install-frontend
install-frontend:
	cd frontend && \
		yarn install


.PHONY: model
model: install-frontend
	mkdir -p schema
	$(RUN) monarch schema > schema/monarch-py.yaml
	$(RUN) gen-pydantic schema/monarch-api.yaml > backend/src/monarch_api/model.py
	$(RUN) gen-typescript schema/monarch-api.yaml > frontend/src/api/model.ts
	$(RUN) black backend/src/monarch_api/model.py
	cd frontend && \
		npx prettier -w src/api/model.ts


# Documentation
.PHONY: docs
docs: install-backend model
	$(RUN) gen-doc -d $(ROOTDIR)/docs/Data-Model/ $(ROOTDIR)/schema/monarch-api.yaml


### Development ###

.PHONY: dev-frontend
dev-frontend: frontend/src/api/model.ts
	cd frontend && \
		yarn serve


.PHONY: dev-backend
dev-backend: backend/src/monarch_api/main.py
	cd backend && \
		poetry run uvicorn src.monarch_api.main:app --reload


### Docker ###

.PHONY: docker-build
docker-build:
	cd backend && \
		docker build --rm --tag us-central1-docker.pkg.dev/monarch-initiative/monarch-api/monarch-api:$(VERSION) .

.PHONY: docker-push
docker-push:
	docker push us-central1-docker.pkg.dev/monarch-initiative/monarch-api/monarch-api:$(VERSION)

### Linting, Formatting, and Cleaning ###

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .pytest_cache
	rm -rf dist


.PHONY: clobber
clobber:
	rm -f schema/monarch-py.yaml \
		backend/src/monarch_api/model.py \
		frontend/src/api/model.ts


.PHONY: lint
lint: install lint-frontend lint-backend


.PHONY: lint-frontend
lint-frontend: install-frontend
	cd frontend && \
		npx prettier --check src tests


.PHONY: lint-backend
lint-backend: install-backend
	$(RUN) flake8 --exit-zero --max-line-length 120 backend/src backend/tests
	$(RUN) isort --check-only --diff backend/src backend/tests
	$(RUN) black --check --diff backend/src backend/tests


.PHONY: format
format: format-frontend format-backend


.PHONY: format-backend
format-backend: install-backend
	$(RUN) autoflake \
		--recursive \
		--remove-all-unused-imports \
		--remove-unused-variables \
		--ignore-init-module-imports \
		--in-place \
		backend/src backend/tests
	$(RUN) isort backend/src backend/tests
	$(RUN) black backend/src backend/tests


.PHONY: format-frontend
format-frontend: install-frontend
	cd frontend && \
		npx prettier -w src tests

