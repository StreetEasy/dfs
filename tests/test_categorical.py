import pandas as pd
import pytest

# from hypothesis.extra.pandas import column, data_frames
# from hypothesis import given, strategies as st


def test_df_oneof():
    from dataframe_schema import validate_df, DataFrameSummaryError

    df = pd.DataFrame({"x": [1, 2, 3], "y": [0.2, 0.5, 0.99], "z": ["A", "A", "Q"]})
    schema = {
        "metadata": {"protocol_version": 1.0},
        "columns": {
            "x": {"max_value": 5, "min_value": 0},
            "y": {"max_value": 1, "min_value": 0},
            "z": {"oneof": ["A", "Q"]},
        },
        "strict_cols": True,
    }

    validate_df(df, schema)

    df.loc[1, "z"] = "B"
    with pytest.raises(DataFrameSummaryError):
        validate_df(df, schema)


# @given(df=cat_df_include())
def test_df_include():
    from dataframe_schema import validate_df, DataFrameSummaryError

    df = pd.DataFrame({"x": [1, 2, 3], "y": [0.2, 0.5, 0.99], "z": ["A", "Q", "Q"]})

    schema = {
        "columns": {
            "x": {"dtype": "int"},
            "y": {"dtype": "float"},
            "z": {"include": ["A", "Q"]},
        },
        "strict_cols": True,
    }

    validate_df(df, schema)

    schema["columns"]["z"]["include"].append("B")
    with pytest.raises(DataFrameSummaryError):
        validate_df(df, schema)


def test_df_unique():
    from dataframe_schema import validate_df, DataFrameSummaryError

    df = pd.DataFrame({"x": [1, 2, 3], "y": [0.2, 0.5, 0.99], "z": ["A", "B", "C"]})
    schema = {
        "columns": {
            "x": {"max_value": 5, "min_value": 0},
            "y": {"max_value": 1, "min_value": 0},
            "z": {"unique": True},
        },
        "strict_cols": True,
    }

    validate_df(df, schema)

    df["z"] = "A"

    with pytest.raises(DataFrameSummaryError):
        validate_df(df, schema)
