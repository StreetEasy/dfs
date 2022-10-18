from typing import Optional
import pandas as pd
from pydantic import BaseModel, Field, PositiveInt, Extra

from .exceptions import DataFrameValidationError
from .collector import exception_collector


class ShapeSchema(BaseModel):
    rows: Optional[PositiveInt] = Field(None, description="exact number of rows")
    cols: Optional[PositiveInt] = Field(None, description="exact number of columns")
    max_cols: Optional[PositiveInt] = Field(
        None, description="maximum number of columns"
    )
    min_cols: Optional[PositiveInt] = Field(
        None, description="minimum number of columns"
    )
    max_rows: Optional[PositiveInt] = Field(None, description="maximum number of rows")
    min_rows: Optional[PositiveInt] = Field(None, description="minimum number of rows")

    class Config:
        extra = Extra.forbid

    @exception_collector
    def validate_df(self, df: pd.DataFrame) -> None:
        """validate shape of the dataframe"""
        for i, el in enumerate(("rows", "cols")):
            exact = getattr(self, el)
            if exact is not None:
                if not df.shape[i] == exact:
                    text = "{0}: {1} != {2}".format(el, df.shape[i], exact)
                    raise DataFrameValidationError(text)

            max_val = getattr(self, f"max_{el}")
            if max_val is not None:
                if not df.shape[i] <= max_val:
                    text = "{0}: {1} < {2}".format(el, df.shape[i], max_val)
                    raise DataFrameValidationError(text)

            min_val = getattr(self, f"min_{el}")
            if min_val is not None:
                if not df.shape[i] >= min_val:
                    text = "{0}: {1} < {2}".format(el, df.shape[i], min_val)
                    raise DataFrameValidationError(text)
