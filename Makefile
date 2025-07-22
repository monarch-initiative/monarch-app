RUN = cd backend && uv run
VERSION = $(shell uv --directory backend version -s)
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
	@echo "|     data                Generate data files               │"
	@echo "|     category-enums      Generate category enums           │"
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
		uv sync && \
		uv pip install -e .[dev]


.PHONY: install-frontend
install-frontend:
	cd frontend && \
		bun install && \
		bunx playwright install


.PHONY: model
model: install-backend	
	$(RUN) gen-pydantic --meta NONE --extra-fields allow $(SCHEMADIR)/model.yaml > $(SCHEMADIR)/model.py
	$(RUN) gen-typescript $(SCHEMADIR)/model.yaml > $(ROOTDIR)/frontend/src/api/model.ts
	make format


### Documentation ###

docs/Data-Model:
	mkdir -p $@

.PHONY: docs
docs: install-backend docs/Data-Model
	$(RUN) gen-doc -d $(ROOTDIR)/docs/Data-Model/ $(SCHEMADIR)/model.yaml
	$(RUN) typer $(ROOTDIR)/backend/src/monarch_py/cli.py utils docs --name monarch --output $(ROOTDIR)/docs/Usage/CLI.md
	$(RUN) mkdocs build -f ../mkdocs.yaml


### Data/Fixtures ###

.PHONY: fixtures
fixtures: 
	@echo "Generating fixtures and data..."
	$(RUN) python ../scripts/generate_fixtures.py --all-fixtures
	make format


.PHONY: data
data:
	@echo "Generating frontpage metadata..."
	$(RUN) python ../scripts/generate_fixtures.py --metadata
	@echo "Generating resources data..."
	wget https://raw.githubusercontent.com/monarch-initiative/monarch-documentation/main/src/docs/resources/monarch-app-resources.json -O frontend/src/pages/resources/resources.json
	make format-frontend

.PHONY: update_publications
update_publications:
	@echo "Generating publications data..."
	$(RUN) python ../scripts/get_publications.py update --update-data

.PHONY: category-enums
category-enums:
	@echo "Generating category enums..."
	$(RUN) python ../scripts/generate_category_enums.py
	make format-backend
	

### Testing ###

.PHONY: test
test: test-backend test-frontend


.PHONY: test-backend
test-backend: 
	$(RUN) pytest tests


.PHONY: test-frontend
test-frontend: 
	cd frontend && \
		bun run test


### Development ###

.PHONY: dev-frontend
dev-frontend: frontend/src/api/model.ts
	cd frontend && \
		VITE_API=local bun run dev


.PHONY: dev-api
dev-api: 
	$(RUN) uvicorn src.monarch_py.api.main:app --reload


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
		bun run test:lint


.PHONY: lint-backend
lint-backend: 
	$(RUN) ruff check --diff --exit-zero .
	$(RUN) black --check --diff -l 120 src tests


.PHONY: format
format: format-frontend format-backend


.PHONY: format-backend
format-backend: 
	$(RUN) ruff check --fix --exit-zero .
	$(RUN) black -l 120 src tests


.PHONY: format-frontend
format-frontend:
	cd frontend && \
		bun run lint
