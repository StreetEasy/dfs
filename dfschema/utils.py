import pandas as pd
from datetime import date

from .core.exceptions import DataFrameValidationError

__all__ = ["sort_by_scheme", "generate_scheme", "schema_to_dtypes"]


DTYPE_DICT = {
    "object": "str",
    "float64": "float",
    "int64": "int",
    "datetime64[ns]": "datetime",
}


def sort_by_scheme(df: pd.DataFrame, scheme: dict) -> pd.DataFrame:
    """sort dataframe columns bu the scheme order

    uses either index, if columns is list, or `index` value if columns is dict

    Args:
        df -- pd.DataFrame - dataframe to sort
        scheme -- dict - scheme dict
    """
    if "columns" not in scheme:
        raise DataFrameValidationError(
            "No columns in the scheme: {}".format(scheme.keys())
        )

    scheme_columns = scheme["columns"]

    if isinstance(scheme_columns, list):
        return df[scheme_columns]

    elif isinstance(scheme_columns, dict):
        sorted_cols = [k for k in scheme_columns if "index" in scheme_columns[k]]
        sorted_cols.sort(key=lambda x: scheme_columns[x].get("index", None))

        other_cols = []
        if len(sorted_cols) < len(df.columns):
            other_cols = [col for col in df.columns if col not in sorted_cols]

        cols = sorted_cols + other_cols
        return df[cols]


def generate_scheme(
    df: pd.DataFrame,
    additionalColumns: bool = True,
    exactColumnOrder: bool = False,
    na_thlds: bool = True,
    minmax: bool = True,
    version: str = f"{date.today():%Y-%m-%d}",
) -> dict:
    """generates dummy scheme over given dataframe"""
    schema: dict = {
        "additionalColumns": additionalColumns,
        "exactColumnOrder": exactColumnOrder,
        "version": version,
    }

    cols: dict = {"dtype": df.dtypes.astype(str).to_dict()}

    if na_thlds:
        cols["na_limit"] = df.notnull().all().astype(int)  # type: ignore

    cols_df = pd.DataFrame(cols)
    cols_df["dtype"] = cols_df["dtype"].replace(DTYPE_DICT)

    schema["columns"] = cols_df.to_dict(orient="index")  # type: ignore

    minmax_cols = ("float", "int")

    for name, props in schema["columns"].items():
        if minmax and props["dtype"] in minmax_cols:
            s: pd.Series = df[name]
            schema["columns"][name]["min"] = s.min()
            schema["columns"][name]["max"] = s.max()

        if props["na_limit"] == 0:
            schema["columns"][name]["na_limit"] = True

        if props["dtype"] == "category":
            schema["columns"][name]["one_of"] = df[name].unique().tolist()

    return schema


def schema_to_dtypes(schema: dict) -> dict:
    """generate a dict of dtypes for pandas to_sql
    out of the schema.
    """
    try:
        from sqlalchemy import BIGINT, BOOLEAN, DATE, DATETIME, FLOAT, SMALLINT, VARCHAR
    except ImportError:
        raise ImportError(
            "`sqlalchemy` is required to use this function. You can install it as extra for this package"
        )

    sql_dtypes = {
        "object": VARCHAR,
        "str": VARCHAR,
        "date": DATE,
        "bool": BOOLEAN,
        "datetime": DATETIME,
        "small_int": SMALLINT,
        "int": BIGINT,
        "float": FLOAT,
    }

    dtypes = {
        col: sql_dtypes.get(v["dtype"], None)
        for col, v in schema["columns"].items()
        if "dtype" in v
    }
    return dtypes
