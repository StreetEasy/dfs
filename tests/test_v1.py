import pytest
from pydantic.error_wrappers import ValidationError


def test_validate_df_v1_invalid(bad_schema_v1):
    from dfschema.core.core import DfSchema

    with pytest.raises((ValidationError, TypeError)):
        DfSchema.from_dict(bad_schema_v1["schema"])


def test_schema_objects(good_schema_v1: dict):
    from dfschema.core.core import DfSchema

    S = DfSchema.from_dict(good_schema_v1["schema"])
    if good_schema_v1["name"] == "sales_certainty_inference":
        new = S.dict()
        model_col = [c for c in new["columns"] if c["name"] == "model"][0]
        assert model_col.get("categorical", {}).get("mode") == "exact_set"


def test_categorical_dtypes():
    from dfschema.core.core import DfSchema
    import json
    from pathlib import Path
    path = Path(__name__).parent / 'tests/test_schemas/v1/good/property_benchmarks.json'
    schema = json.loads(path.read_text())
    
    S = DfSchema.from_dict(schema)
    catcol = [el for el in S.columns if el.name == 'BOROUGH_ID'][0]
    assert catcol.categorical.value_set == frozenset((100, 200, 300, 400, 500))
