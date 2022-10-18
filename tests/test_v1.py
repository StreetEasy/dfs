import pytest
from pydantic.error_wrappers import ValidationError


def test_validate_df_v1_invalid(bad_schema_v1):
    from dfs.core.core import DfSchema

    with pytest.raises((ValidationError, TypeError)):
        DfSchema.from_dict(bad_schema_v1["schema"])


def test_schema_objects(good_schema_v1: dict):
    from dfs.core.core import DfSchema

    DfSchema.from_dict(good_schema_v1["schema"])
