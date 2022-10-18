import pytest

# import pandas as pd


max_min_correct = {
    "df1": [  # protocol 1.0
        {
            "columns": {
                "x": {"max_value": 5, "min_value": 0},
                "y": {"dtype": "string"},
            },
            "strict_cols": True,
        },
        {
            "columns": {
                "x": {"max_value": 4, "min_value": 1},
                "y": {"dtype": "string"},
            },
            "strict_cols": True,
        },
        {
            "metadata": {"protocol_version": 2.0},
            "additionalColumns": True,
            "columns": [
                {
                    "name": "x",
                    "distribution": {
                        "metrics": [
                            {"name": "median", "range": [2, 3]},
                            {"name": "mean", "range": [2, 3]},
                            {"name": "std", "range": [1, 2]},
                            {
                                "name": "quantile",
                                "range": [1, 1.2],
                                "kwargs": {"q": 0.05},
                            },
                        ]
                    },
                },
                {"name": "y", "dtype": "string"},
            ],
        },
    ],
    "df2": [  # protocol 1.0
        {
            "columns": {
                "x": {"min_value": 1},
                "y": {"dtype": "string"},
            },
            "strict_cols": True,
        },
        {
            "columns": {
                "x": {"min_value": 1, "max_value": 4},
                "y": {"dtype": "string"},
            },
            "strict_cols": True,
        },
    ],
}


@pytest.mark.parametrize("schema", max_min_correct["df1"])
def test_validate_df1_max_min(df1, schema):
    from dataframe_schema import validate_df

    validate_df(df1, schema)


@pytest.mark.parametrize("schema", max_min_correct["df2"])
def test_validate_df2_max_min(df2, schema):
    from dataframe_schema import validate_df

    validate_df(df2, schema)


wrong_schemas_max_min_df2 = [
    {
        "columns": {
            "x": {"max_value": 2, "min_value": 1},
            "y": {"max_value": 0.99, "min_value": 0.5},
        }
    }
]


@pytest.mark.parametrize("schema", wrong_schemas_max_min_df2)
def test_validate_df2_max_min_raises(df2, schema):
    from dataframe_schema import validate_df, DataFrameValidationError

    with pytest.raises(DataFrameValidationError):
        validate_df(df2, schema)
