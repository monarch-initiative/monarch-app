RUN = poetry -C backend run
VERSION = $(shell poetry -C backend version -s)
ROOTDIR = $(shell pwd)
SCHEMADIR = $(ROOTDIR)/backend/src/monarch_py/datamodels

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
	@echo "│     dev-api             Run api in development mode       │"
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
		poetry install -E api --with dev


.PHONY: install-frontend
install-frontend:
	cd frontend && \
		yarn install && \
		npx playwright install


.PHONY: model
model: install-backend	
	$(RUN) gen-pydantic $(SCHEMADIR)/model.yaml > $(SCHEMADIR)/model.py
	$(RUN) gen-typescript $(SCHEMADIR)/model.yaml > frontend/src/api/model.ts
	$(RUN) black $(SCHEMADIR)/model.py


### Documentation ###

docs/Data-Model:
	mkdir -p $@

.PHONY: docs
docs: install-backend docs/Data-Model
	$(RUN) gen-doc -d $(ROOTDIR)/docs/Data-Model/ $(SCHEMADIR)/model.yaml
	$(RUN) typer backend/src/monarch_py/cli.py utils docs --name monarch --output docs/Usage/CLI.md
	$(RUN) mkdocs build


### Testing ###

.PHONY: test
test: test-backend test-frontend


.PHONY: test-backend
test-backend: 
	$(RUN) pytest backend/tests


.PHONY: test-frontend
test-frontend: 
	cd frontend && \
		yarn test


.PHONY: fixtures
fixtures: 
	@echo "Generating fixtures..."
	$(RUN) python scripts/generate_fixtures.py --all-fixtures
	$(RUN) black backend/tests/fixtures/
	cd frontend && \
		yarn lint 

### Development ###

.PHONY: dev-frontend
dev-frontend: frontend/src/api/model.ts
	cd frontend && \
		yarn dev


.PHONY: dev-api
dev-api: 
	cd backend && \
		poetry run uvicorn src.monarch_py.api.main:app --reload


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
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf `find . -name __pycache__` \
		.ruff_cache .pytest_cache **/.ipynb_checkpoints \
		frontend/dist \
		backend/.venv \



.PHONY: clobber
clobber:
	rm -f schema/model.yaml \
		backend/src/monarch_py/datamodels/model.py \
		frontend/src/api/model.ts


.PHONY: lint
lint: lint-frontend lint-backend


.PHONY: lint-frontend
lint-frontend: 
	cd frontend && \
		yarn test:lint


.PHONY: lint-backend
lint-backend: 
	$(RUN) ruff check --diff --exit-zero backend
	$(RUN) black --check --diff -l 120 backend/src backend/tests


.PHONY: format
format: format-frontend format-backend


.PHONY: format-backend
format-backend: 
	$(RUN) ruff check --fix --exit-zero backend
	$(RUN) black -l 120 backend/src backend/tests


.PHONY: format-frontend
format-frontend:
	cd frontend && \
		yarn lint
