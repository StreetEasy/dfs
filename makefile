
tests:
	poetry run python -m pytest

jshema:
	poetry run python scripts/generate_jsonschema.py

docs:
	poetry run jsonschema2md jsonschemas/schema.json docs/docs.md

changelog:
	poetry run auto-changelog
