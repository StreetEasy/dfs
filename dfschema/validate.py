import pandas as pd

from .core import DfSchema


def validate(df: pd.DataFrame, schema: dict, summary: bool = True) -> None:
    """validate dataframe against the schema

    validate dataframe agains the schema as a dictionary. will raise
    either DataFrameSummaryError (if summary=True) or DataFrameValidationError for specific
    problem (if summary=False)

    ### Example
    ```python
    import json
    import pandas as pd
    import dfschema
    from pathlib import Path

    path = '/schema.json'
    schema = json.loads(Path(path).read_text())

    df = pd.DataFrame({'a':[1,2], 'b':[3,4]})

    dfschema.validate(df, schema, summary=True)
    ```

    ### Alternative
    Equivalent to using `dfschema.DfSchema` class (which is recommended):

    Args:
        df (pd.DataFrame): A dataframe to validate
        schema (dict): schema as a dictionary to validate against
        summary (bool): if `False`, raise exception on first violation (faster), otherwise will collect all violations and raise summary exception (slower)

    """

    Schema = DfSchema.from_dict(schema)
    Schema.validate_df(df=df, summary=summary)
