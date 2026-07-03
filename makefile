
tests:
	uv run python -m pytest

jshema:
	uv run python scripts/generate_jsonschema.py

serve_docs:
	uv run mkdocs serve

docs:
	uv run mkdocs build -f .config/mkdocs/mkdocs.yml

changelog:
	uv run gitchangelog
