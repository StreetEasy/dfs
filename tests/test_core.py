import pytest
from pydantic.error_wrappers import ValidationError


def test_schema_objects(good_schema: dict):
    from dfs.core.core import DfSchema

    DfSchema.from_dict(good_schema["schema"])


def test_bad_schema_objects(bad_schema: dict):
    from dfs.core.core import DfSchema

    with pytest.raises((ValidationError, TypeError)):
        DfSchema.from_dict(bad_schema["schema"])
