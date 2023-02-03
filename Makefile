RUN = poetry run
VERSION=$(shell poetry version -s)

.PHONY: install
install:
	poetry install


.PHONY: generate-model
generate-model:
	poetry run monarch schema > schema/monarch-py.yaml
	poetry run gen-pydantic schema/monarch-api.yaml > src/monarch_api/model.py
	poetry run gen-typescript schema/monarch-api.yaml > frontend/src/api/interfaces.ts

.PHONY: clobber
clobber:
	rm -f schema/monarch-py.yaml
	rm -f src/monarch_api/model.py
	rm -f frontend/src/api/interfaces.ts


.PHONY: dev-backend
dev-backend: monarch_api/main.py
	poetry run uvicorn src.monarch_api.main:app --reload

.PHONY: generate-docs
generate-docs: install generate-model
	$(RUN) gen-doc -d docs/Data-Model/ schema/monarch-api.yaml


.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .pytest_cache
	rm -rf dist

.PHONY: lint
lint:
	$(RUN) flake8 --exit-zero --max-line-length 120 src tests/
	$(RUN) black --check --diff src tests
	$(RUN) isort --check-only --diff src tests

.PHONY: format
format:
	$(RUN) autoflake \
		--recursive \
		--remove-all-unused-imports \
		--remove-unused-variables \
		--ignore-init-module-imports \
		--in-place src tests
	$(RUN) isort src tests
	$(RUN) black src tests

.PHONY: docker-build
docker-build:
	docker build --rm --tag us-central1-docker.pkg.dev/monarch-initiative/monarch-api/monarch-api:$(VERSION) .

.PHONY: docker-push
docker-push:
	docker push us-central1-docker.pkg.dev/monarch-initiative/monarch-api/monarch-api:$(VERSION)