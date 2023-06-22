RUN = poetry -C backend/ run
VERSION = $(shell cd backend && poetry version -s)
ROOTDIR = $(shell pwd)

### Help ###
.PHONY: help
help:
	@echo "╭───────────────────────────────────────────────────────────╮"
	@echo "│ Makefile for Monarch API                                  │"
	@echo "│ ────────────────────────                                  │"
	@echo "│ Usage:                                                    │"
	@echo "│     make <target>                                         │"
	@echo "│                                                           │"
	@echo "│ Targets:                                                  │"
	@echo "│     help                Print this help message           │"
	@echo "│     all                 Install everything                │"
	@echo "│     fresh               Clean and install everything      │"
	@echo "│     clean               Clean up build artifacts          │"
	@echo "│     clobber             Clean up generated files          │"
	@echo "│                                                           │"
	@echo "│     docs                Generate documentation            │"
	@echo "│     model               Generate model files              │"
	@echo "|     fixtures            Generate data fixtures            │" 
	@echo "│                                                           │"
	@echo "│     install             Install backend and frontend      │"
	@echo "│     install-backend     Install backend                   │"
	@echo "│     install-frontend    Install frontend                  │"
	@echo "│                                                           │"
	@echo "│     test                Run all tests                     │"
	@echo "│     test-backend        Run backend tests                 │"
	@echo "│     test-frontend       Run frontend tests                │"
	@echo "│                                                           │"
	@echo "│     dev-frontend        Run frontend in development mode  │"
	@echo "│     dev-backend         Run backend in development mode   │"
	@echo "│                                                           │"
	@echo "│     docker-build        Build docker image                │"
	@echo "│     docker-push         Push docker image                 │"
	@echo "│                                                           │"
	@echo "│     lint                Lint all code                     │"
	@echo "│     lint-backend        Lint backend code                 │"
	@echo "│     lint-frontend       Lint frontend code                │"
	@echo "│                                                           │"
	@echo "│     format              Format all code                   │"
	@echo "│     format-backend      Format backend code               │"
	@echo "│     format-frontend     Format frontend code              │"
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
		yarn install && \
		npx playwright install


.PHONY: model
model: schema/
	$(RUN) monarch schema > schema/model.yaml
	$(RUN) gen-pydantic schema/model.yaml > backend/src/monarch_api/model.py
	$(RUN) gen-typescript schema/model.yaml > frontend/src/api/model.ts
	$(RUN) black backend/src/monarch_api/model.py


.PHONY: fixtures
fixtures: install-backend
	@echo "Generating fixtures..."
	@echo "This requires a running instance of Monarch Solr."
	$(RUN) python scripts/generate_fixtures.py
	# $(RUN) black backend/src/monarch_api/fixtures.py

# Documentation
.PHONY: docs
docs: install-backend model
	$(RUN) gen-doc -d $(ROOTDIR)/docs/Data-Model/ $(ROOTDIR)/schema/monarch-api.yaml
	$(RUN) mkdocs build


### Testing ###

.PHONY: test
test: test-backend test-frontend


.PHONY: test-backend
test-backend: install-backend model
	$(RUN) pytest backend/tests


.PHONY: test-frontend
test-frontend: install-frontend model
	cd frontend && \
		yarn test


### Development ###

.PHONY: dev-frontend
dev-frontend: frontend/src/api/model.ts
	cd frontend && \
		yarn dev


.PHONY: dev-backend
dev-backend: backend/src/monarch_api/model.py
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
	rm -rf backend/.venv


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
		yarn test:lint


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
		yarn lint
