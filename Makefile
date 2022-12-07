RUN = poetry run

schema/monarch-py.yaml:
	poetry run monarch schema > $@

src/monarch_api/model.py: schema/monarch-api.yaml schema/monarch-py.yaml
	poetry run gen-pydantic $< > $@

#todo: remove the pipe grep cleaning bits after the next linkml update
frontend/src/api/interfaces.ts: schema/monarch-api.yaml schema/monarch-py.yaml
	poetry run gen-typescript $< | grep -v "\*" | grep -v -e '^[[:space:]]*$$' > $@

.PHONY: clobber
clobber:
	rm schema/monarch-py.yaml
	rm monarch_api/model.py
	rm frontend/src/api/interfaces.ts

.PHONY: dev-backend
dev-backend: monarch_api/main.py
	poetry run uvicorn src.monarch_api.main:app --reload

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
