dev-backend: monarch_api/main.py
	poetry run uvicorn monarch_api.main:app --reload

monarch_api/model.py: schema/monarch-api.yaml
	poetry run gen-pydantic ../$< > ../$@

#todo: remove the pipe grep cleaning bits after the next linkml update
frontend/src/api/interfaces.ts: schema/monarch-api.yaml
	cd backend && poetry run gen-typescript ../$< | grep -v "\*" | grep -v -e '^[[:space:]]*$$' > ../$@

clobber:
	rm monarch_api/model.py
	rm frontend/src/api/interfaces.ts

test:
	poetry run pytest
