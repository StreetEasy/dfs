import pytest


good_schemas = [
    {"shape": {"rows": 4, "cols": 2}},
    {"shape": {"max_rows": 4}},
    {"shape": {"max_cols": 2}},
    {"shape": {"min_rows": 2}},
    {"shape": {"min_cols": 2}},
    {"columns": ["x", "y"]},
    {"columns": {"x": {"dtype": "number"}, "y": {"dtype": "character"}}},
    {
        "columns": {
            "x": {"dtype": "number"},
            "y": {"dtype": "character", "na_limit": 0.5},
        }
    },
    {
        "columns": {
            "x": {"dtype": "number"},
            "y": {"dtype": "character", "na_limit": 0.25},
        }
    },
]


@pytest.mark.parametrize("schema", good_schemas)
def test_validate_df(df1, schema):
    from dfschema import validate

    validate(df1, schema)


wrong_schemas = [
    {"shape": {"rows": 3, "cols": 3}},
    {"shape": {"rows": 2, "cols": 2}},
    {"shape": {"max_rows": 2}},
    {"shape": {"max_cols": 1}},
    {"shape": {"min_rows": 5}},
    {"shape": {"min_cols": 3}},
    {"columns": ["x", "y", "z"]},
    {"columns": {"x": {"dtype": "floating"}, "y": {"dtype": "floating"}}},
    {
        "columns": {
            "x": {"dtype": "int"},
            "y": {"dtype": "character", "na_limit": 0.2},
        }
    },
]


@pytest.mark.parametrize("summary", [False, True])
@pytest.mark.parametrize("schema", wrong_schemas)
def test_validate_df_raises(df1, summary, schema):
    from dfschema import (
        validate,
        DataFrameValidationError,
        DataFrameSummaryError,
    )

    e = [DataFrameValidationError, DataFrameSummaryError][summary]

    with pytest.raises(e):
        validate(df1, schema, summary=summary)


good_schemas2 = [
    {
        "columns": {
            "x": {"dtype": "floating", "na_limit": 0.4},
            "y": {"dtype": "character"},
        }
    },
    {
        "columns": {
            "x": {"dtype": "floating", "na_limit": True},
            "y": {"dtype": "character"},
        }
    },
]

wrong_schemas2 = [
    {
        "columns": {
            "x": {"dtype": "floating", "na_limit": 0.2},
            "y": {"dtype": "character"},
        }
    }
]


@pytest.mark.parametrize("schema", good_schemas2)
def test_validate_df2(df2, schema):
    from dfschema import validate

    validate(df2, schema)


@pytest.mark.parametrize("summary", [False, True])
@pytest.mark.parametrize("schema", wrong_schemas2)
def test_validate_df2_raises(df2, summary, schema):
    from dfschema import (
        validate,
        DataFrameValidationError,
        DataFrameSummaryError,
    )

    e = [DataFrameValidationError, DataFrameSummaryError][summary]

    with pytest.raises(e):
        validate(df2, schema, summary=summary)


good_schemas3 = [
    {"columns": {"x": {"dtype": "string"}, "y": {"dtype": "string"}}},
]

wrong_schemas3 = [
    {
        "columns": {
            "x": {"dtype": "floating", "na_limit": True},
            "y": {"dtype": "character"},
        }
    },
    {
        "columns": {
            "x": {"dtype": "floating", "na_limit": 0.5},
            "y": {"dtype": "character"},
        }
    },
]


@pytest.mark.parametrize("schema", good_schemas3)
def test_validate_nan_str(df3, schema):
    from dfschema import validate

    validate(df3, schema)


@pytest.mark.parametrize("schema", wrong_schemas3)
def test_validate_df3_raises(df3, schema):
    from dfschema import validate, DataFrameValidationError

    with pytest.raises(DataFrameValidationError):
        validate(df3, schema)
