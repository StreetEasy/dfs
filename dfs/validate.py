import pandas as pd

from .core import DfSchema


def validate_df(df: pd.DataFrame, schema: dict, summary: bool = True) -> None:
    """validate dataframe over the scheme

    validate dataframe columns, shape, dtypes
    over the schema

    Arguments:
        df -- dataframe to validate
        schema -- dict -- dictionary to validate against,
            check wiki for more detaims NOTE: add wiki documentation!
        summary -- bool -- if False, raise exception as soon as possible, otherwise wait for all checks to be done
        validate_schema -- bool -- if True, validate schema vs jsonschema standart, otherwise skip it
    """

    Schema = DfSchema.from_dict(schema)
    Schema.validate_df(df=df, summary=summary)
