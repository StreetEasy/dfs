import pytest
import pandas as pd
import numpy as np


@pytest.fixture()
def df_subset():
    return pd.DataFrame({"x": [1, 2, 3, 4], "y": ["foo", "foo", "baz", np.nan]})


def test_subset_dict(df_subset):
    from dfschema.core.core import DfSchema

    D = {
        "metadata": {"protocol_version": 2.0},
        "subsets": [
            {
                "predicate": {"y": "foo"},
                "columns": [{"name": "x", "dtype": "int", "value_limits": {"max": 2}}],
            },
            {
                "predicate": {"y": "baz"},
                "columns": [
                    {
                        "name": "x",
                        "dtype": "int",
                        "value_limits": {"min": 3, "max": 3},
                    }
                ],
            },
        ],
    }

    S = DfSchema.from_dict(D)
    S.validate_df(df_subset)


def test_subset_query(df_subset):
    from dfschema.core.core import DfSchema

    D = {
        "metadata": {"protocol_version": 2.0},
        "subsets": [
            {
                "predicate": "y == 'foo'",
                "columns": [{"name": "x", "dtype": "int", "value_limits": {"max": 2}}],
            },
            {
                "predicate": "x >= 3",
                "shape": {"rows": 2},
                "columns": [
                    {
                        "name": "x",
                        "dtype": "int",
                        "value_limits": {"max": 4, "min": 3},
                    }
                ],
            },
        ],
    }

    S = DfSchema.from_dict(D)
    S.validate_df(df_subset)


def test_subset_query_raises(df_subset):
    from dfschema.core.core import DfSchema
    from dfschema.core.exceptions import DataFrameSummaryError

    D = {
        "metadata": {"protocol_version": 2.0},
        "subsets": [{"predicate": "x >= 3", "shape": {"rows": 5}}],
    }

    S = DfSchema.from_dict(D)

    with pytest.raises(DataFrameSummaryError):
        S.validate_df(df_subset)
