# import pytest


def test_generate(df1):
    from dfs.core import DfSchema

    print(df1.dtypes)

    try:
        S = DfSchema.from_df(df1)
    except Exception as e:  # for debugging
        sd = DfSchema.from_df(df1, return_dict=True)
        raise Exception(sd, e)

    S.validate_df(df1)  # type: ignore
