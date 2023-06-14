import sys
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from .config import CURRENT_PROTOCOL_VERSION


class Generated_With(BaseModel):
    @property
    def dfschema(self) -> str:
        if sys.version_info >= (3, 8):
            from importlib.metadata import version
        else:
            from importlib_metadata import version

        return version("dfschema")

    @property
    def pandas(self) -> str:
        import pandas as pd

        return pd.__version__


class MetaData(BaseModel):
    protocol_version: float = Field(
        CURRENT_PROTOCOL_VERSION, description="protocol version of the schema"
    )
    version: Optional[str] = Field(
        date.today().strftime("%Y-%m-%d"),
        description="version of the schema",
        example="2022-06-12",
    )

    generated_with: Generated_With = Field(
        Generated_With(), description="version of packages schema was generated with"
    )
    custom_settings: Optional[dict] = Field(
        None, description="custom settings. does not affect any logic"
    )
