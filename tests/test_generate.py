# import pytest


def test_generate_df1(df1):
    from dfschema.core import DfSchema
    from dfschema import __version__

    print(df1.dtypes)

    try:
        S = DfSchema.from_df(df1)
    except Exception as e:  # for debugging
        sd = DfSchema.from_df(df1, return_dict=True)
        raise Exception(sd, e)

    S.validate_df(df1)  # type: ignore
    assert S.metadata.get('generated_with',{}).get('dfschema') == __version__


def test_generate_df4(df4):
    from dfschema.core import DfSchema

    print(df4.dtypes)

    try:
        S = DfSchema.from_df(df4)
    except Exception as e:  # for debugging
        sd = DfSchema.from_df(df4, return_dict=True)
        raise Exception(sd, e)

    S.validate_df(df4)  # type: ignore
