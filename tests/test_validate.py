import pytest
from pathlib import Path

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



prediction_good_schemas = [
    Path(__file__).parent / "test_schemas/v2/good/v2_predictions.json",
    Path(__file__).parent / "test_schemas/v2/good/v2_predictions2.json"
]


@pytest.fixture
def df4():
    import pandas as pd
    df = pd.DataFrame({
        "value": [100000, 200000, 300000, 500000],
        "inferred_at": ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-03"],
        "trained_at": ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-03"],
        "model": ["main", "certainty_low", "certainty_hight", "certainty_median"],
        "version": ["1.0.0", "1.0.1", "1.0.2", "1.0.3"],
    })
    for col in ["inferred_at", "trained_at"]:
        df[col] = pd.to_datetime(df[col])
    return df


@pytest.mark.parametrize("schema", prediction_good_schemas)
def test_validate_df4(df4, schema):
    from dfschema import DfSchema
    schema = DfSchema.from_file(schema)
    schema.validate_df(df4)