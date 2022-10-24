"""
Support Dtypes and Aliases.
mostly based on pandas.core.dtypes.dtypes.
https://pandas.pydata.org/docs/user_guide/basics.html#basics-dtypes
"""
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


DtypeAliasPool = {
    # logic
    "bool_": "bool",
    "bool": "bool",
    # String
    "object": "object",
    "str": "string",
    "character": "string",
    "string": "string",
    # Numeric
    "number": "numeric",
    "numeric": "numeric",
    "float": "float",
    "floating": "float",
    "integer": "int",
    "int": "int",
    "int64": "int",
    "int32": "int",
    "int16": "int",
    # time
    "datetime64[ns]": "datetime64[ns]",
    "datetime": "datetime64[ns]",
    "date": "datetime64[ns]",
    "timedelta": "timedelta64[ns]",
    # other
    "category": "category",
    "float64": "float",
    "float32": "float",
    "float16": "float",
}

DtypeLiteral = Literal[tuple(DtypeAliasPool.keys())]  # type: ignore
