import pytest


def test_df_validate_invalid_schema(df1, bad_schema: dict):
    from dataframe_schema import validate_df
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        validate_df(df1, bad_schema["schema"])
