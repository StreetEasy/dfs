import pytest
import pandas as pd


@pytest.fixture
def str_df() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "x": ["A-1", "A-10", "Z-12", None],
            "y": ["A-1 APT", "A-10 PH", "Z-12 THS", None],
            "z": ["A-1", "A-10", "A-12", None],
        }
    )
    
    for col in df.columns:
        df[col] = df[col].astype("string")
    return df


def test_string_matching(str_df):
    from dfschema.core.core import DfSchema

    D = {
        "metadata": {"protocol_version": 2.0},
        "columns": [
            {"name": "x", "dtype": "string", "str_pattern": r"^[A-Z]-\d+$"},
            {"name": "y", "dtype": "string", "str_pattern": r"^[A-Z]-\d+"},
            {"name": "z", "dtype": "string", "str_pattern": "A-"},  # not regex
        ],
    }

    S = DfSchema.from_dict(D)
    S.validate_df(str_df)


def test_string_matching_raises(str_df):
    from dfschema import DfSchema
    from dfschema.core.exceptions import DataFrameSummaryError

    D = {
        "metadata": {"protocol_version": 2.0},
        "columns": [
            {"name": "x", "dtype": "string", "str_pattern": r"^[A-Z]-\d+"},
            {"name": "y", "dtype": "string", "str_pattern": r"^[A-Z]-\d+$"},
        ],
    }

    S = DfSchema.from_dict(D)
    with pytest.raises(DataFrameSummaryError):
        S.validate_df(str_df)
