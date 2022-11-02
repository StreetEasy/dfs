import pandas as pd

from .core import DfSchema


def validate_df(df: pd.DataFrame, schema: dict, summary: bool = True) -> None:
    """validate dataframe against the schema

    validate dataframe agains the schema as a dictionary. will raise
    either DataFrameSummaryError (if summary=True) or DataFrameValidationError for specific
    problem (if summary=False)

    Same as using DfSchema object:
    ```python
    Schema = DfSchema.from_dict(schema)
    Schema.validate_df(df=df, summary=summary)
    ```

    Args:
        df (pd.DataFrame): A dataframe to validate
        schema (dict): schema as a dictionary to validate against
        summary (bool): if `False`, raise exception on first violation (faster), otherwise will collect all violations and raise summary exception (slower)

    Returns:
        None
    """

    Schema = DfSchema.from_dict(schema)
    Schema.validate_df(df=df, summary=summary)
