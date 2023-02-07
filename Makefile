RUN = poetry run
VERSION = $(shell cd backend && poetry version -s)
ROOTDIR = $(shell pwd)


### Help ###

.PHONY: help
help:
	@echo "╭───────────────────────────────────────────────────────────╮"
	@echo "│ Makefile for monarch─api                                  │"
	@echo "│                                                           │"
	@echo "│ Usage:                                                    │"
	@echo "│     make <target>                                         │"
	@echo "│                                                           │"
	@echo "│ Targets:                                                  │"
	@echo "│     install:             install dependencies             │"
	@echo "│     install─backend:     install backend dependencies     │"
	@echo "│     install─frontend:    install frontend dependencies    │"
	@echo "│     model:               generate model files             │"
	@echo "│     clobber:             remove generated model files     │"
	@echo "│     docs:                generate documentation           │"
	@echo "│     dev─frontend:        run frontend in development mode │"
	@echo "│     dev─backend:         run backend in development mode  │"
	@echo "│     docker─build:        build docker image               │"
	@echo "│     docker─push:         push docker image                │"
	@echo "│     clean:               remove temporary files           │"
	@echo "│     lint:                lint code                        │"
	@echo "│     format:              format code                      │"
	@echo "╰───────────────────────────────────────────────────────────╯"


### Installation and Setup ###

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
	cd backend && \
		$(RUN) monarch schema > $(ROOTDIR)/schema/monarch-py.yaml && \
		$(RUN) gen-pydantic $(ROOTDIR)/schema/monarch-py.yaml > src/monarch_api/model.py && \
		$(RUN) gen-typescript $(ROOTDIR)/schema/monarch-py.yaml > $(ROOTDIR)/frontend/src/api/model.ts
	cd frontend && \
		npx prettier -w src/api/model.ts


.PHONY: clobber
clobber:
	rm -f schema/monarch-py.yaml
	rm -f backend/src/monarch_api/model.py
	rm -f frontend/src/api/model.ts


# Documentation
.PHONY: docs
docs: install generate-model
	cd backend && \
		$(RUN) gen-doc -d $(ROOTDIR)/docs/Data-Model/ $(ROOTDIR)/schema/monarch-py.yaml


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
	docker build --rm --tag us-central1-docker.pkg.dev/monarch-initiative/monarch-api/monarch-api:$(VERSION) backend/Dockerfile

.PHONY: docker-push
docker-push:
	docker push us-central1-docker.pkg.dev/monarch-initiative/monarch-api/monarch-api:$(VERSION)

### Linting, Formatting, and Cleaning ###

# TODO: add linting and formatting for frontend?
.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .pytest_cache
	rm -rf dist


.PHONY: lint
lint: install
	cd backend && \
		$(RUN) flake8 --exit-zero --max-line-length 120 src tests/
		$(RUN) black --check --diff src tests
		$(RUN) isort --check-only --diff src tests
	cd frontend && \
		npx prettier --check src/api/model.ts


.PHONY: format
format: 
	$(RUN) autoflake \
		--recursive \
		--remove-all-unused-imports \
		--remove-unused-variables \
		--ignore-init-module-imports \
		--in-place backend/src backend/tests
	$(RUN) isort backend/src backend/tests
	$(RUN) black backend/src backend/tests

