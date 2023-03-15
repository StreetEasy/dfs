import pytest
from pydantic.error_wrappers import ValidationError


def test_validate_df_v1_invalid(bad_schema_v1):
    from dfschema.core.core import DfSchema

    with pytest.raises((ValidationError, TypeError)):
        DfSchema.from_dict(bad_schema_v1["schema"])


def test_schema_objects(good_schema_v1: dict):
    from dfschema.core.core import DfSchema
    
    S = DfSchema.from_dict(good_schema_v1["schema"])
    if good_schema_v1['name'] == 'sales_certainty_inference':
        new = S.dict()
        model_col = [c for c in new['columns'] if c['name'] == 'model'][0]
        assert model_col.get('categorical', {}).get('mode') == 'exact_set'
