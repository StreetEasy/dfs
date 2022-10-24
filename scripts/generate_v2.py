from pathlib import Path
from dfschema.core.core import DfSchema


def get_files(path: Path) -> list:
    return [f for f in path.glob("*.json")]


if __name__ == "__main__":
    v1files = get_files(Path("./tests/test_schemas/v1/bad/"))
    for file in v1files:
        schema = DfSchema.from_file(file)

        path = f"./tests/test_schemas/v2/bad/{file.stem}.json"
        with open(path, "w") as f:
            f.write(schema.json(indent=2))
