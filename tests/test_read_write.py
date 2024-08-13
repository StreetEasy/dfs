import pytest
import pandas as pd
from pathlib import Path

test_dir = Path(__file__).parent / "test_schemas"


paths = [str(test_dir / "v2/good/v2_raw.json"), str(test_dir / "v2/good/v2_raw.yml")]


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        [
            {"pid": 1, "price": 2400, "bedrooms": 2, "bathrooms": 1, "size": 600},
            {"pid": 1, "price": 2400, "bedrooms": 2, "bathrooms": 1, "size": 600},
        ]
    )


@pytest.mark.parametrize("path", paths)
def test_read_schema_file(path, sample_df):
    from dfschema import DfSchema

    schema = DfSchema.from_file(path)
    schema.validate_df(sample_df)


@pytest.mark.parametrize("format", ["json", "yml"])
def test_write_schema_file(format, sample_df):
    from dfschema import DfSchema
    from tempfile import TemporaryDirectory

    schema: DfSchema = DfSchema.from_df(sample_df)  # type: ignore

    # create a temporary directory using the context manager
    with TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / f"test_schema.{format}"
        schema.to_file(path)

        assert path.exists()

        txt = path.read_text()
        if format == "yml":
            import yaml

            try:
                schema_structure = yaml.safe_load(txt)
            except Exception as e:
                raise Exception(txt) from e
        elif format == "json":
            import json

            schema_structure = json.loads(txt)

        assert "additionalColumns" in schema_structure
