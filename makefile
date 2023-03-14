
tests:
	poetry run python -m pytest

jshema:
	poetry run python scripts/generate_jsonschema.py

serve_docs:
	poetry run mkdocs serve

docs:
	poetry run mkdocs build -f .config/mkdocs/mkdocs.yml

changelog:
	poetry run gitchangelog
