import pytest
from pydantic.v1.error_wrappers import ValidationError


def test_schema_objects(good_schema: dict):
    from dfschema.core.core import DfSchema

    DfSchema.from_dict(good_schema["schema"])


def test_bad_schema_objects(bad_schema: dict):
    from dfschema.core.core import DfSchema

    with pytest.raises((ValidationError, TypeError)):
        DfSchema.from_dict(bad_schema["schema"])


@pytest.fixture(scope="function")
def test_dataframe():
    import pandas as pd

    return pd.DataFrame({"foo": [1, 2, 3], "bar": [3, 2, 1]})


def test_optional_columns(test_dataframe):
    from dfschema import DfSchema, DataFrameValidationError

    S = DfSchema.from_df(test_dataframe)

    second_df = test_dataframe.drop(columns=["bar"])

    with pytest.raises(DataFrameValidationError):
        S.validate_df(second_df)

    S.columns[1].optional = True
    S.validate_df(second_df)
