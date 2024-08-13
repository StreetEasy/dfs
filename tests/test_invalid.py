import pytest


def test_df_validate_invalid_schema(df1, bad_schema: dict):
    from dfschema import validate
    from pydantic.v1.error_wrappers import ValidationError

    with pytest.raises(ValidationError):
        validate(df1, bad_schema["schema"])
