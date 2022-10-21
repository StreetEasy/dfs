from pydantic import BaseModel, Extra, Field, PositiveInt

# import json

from typing import Optional, Union, Dict, List, Tuple
from ..logger import logger
from ..dtype import DtypeLiteral


class V1_ShapeSchema(BaseModel):
    class Config:
        extra = Extra.forbid

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


class V1_ColObj(BaseModel):
    class Config:
        extra = Extra.forbid

    dtype: Optional[DtypeLiteral]  # type: ignore

    min_value: Optional[float]
    max_value: Optional[float]

    na_limit: Union[None, bool, float] = Field(None, gt=0, le=1.0)

    include: Optional[List[str]] = None
    oneof: Optional[List[str]] = None
    unique: Optional[bool] = None


class V1_ColumnsSchema(BaseModel):
    __root__: Dict[str, V1_ColObj]

    class Config:
        extra = Extra.forbid


class V1_DfSchema(BaseModel):
    class Config:
        extra = Extra.forbid
        arbitrary_types_allowed = True

    version: Optional[str] = Field(
        None,
        description="version of the schema",
        example="2022-06-12",
    )

    protocol_version: float = Field(1.0, description="version of the protocol")

    metadata: Optional[dict] = None
    custom_settings: Optional[dict] = None

    strict_cols: Optional[bool] = Field(
        False, description="if true, won't support additional columns"
    )
    shape: Optional[V1_ShapeSchema] = Field(None, description="shape expectations")
    columns: Union[List[str], V1_ColumnsSchema, None] = Field(
        None, description="columns expectations"
    )

    def migrate(self) -> Tuple[dict, float]:
        logger.info("Migrating schema v1 to v2")
        schema = self.dict(exclude_none=True)

        if "protocol_version" in schema:
            schema.pop("protocol_version")

        schema["metadata"] = {"protocol_version": 2.0}
        schema["additionalColumns"] = schema.pop("strict_cols", False)

        if "columns" in schema:

            if isinstance(schema["columns"], dict):
                schema["columns"] = [
                    dict(name=k, **v) for k, v in schema["columns"].items()
                ]
            elif isinstance(schema["columns"], list):
                schema["columns"] = [dict(name=name) for name in schema["columns"]]

            for col in schema["columns"]:  # type: ignore
                # na_limits:
                if "na_limit" in col and isinstance(col["na_limit"], bool):
                    """convert old na_limit to na_limits"""
                    col["na_limit"] = 0.99

                # value_limits
                for vl in {"max_value", "min_value"}:
                    if vl in col:
                        value_limits = col.get("value_limits", {})
                        value_limits[vl[:3]] = col.pop(vl)
                        col["value_limits"] = value_limits

                # categorical
                for k in ("oneof", "include", "exact_set"):
                    if col.get(k) is not None:
                        categorical = col.get("categorical", dict())
                        try:
                            categorical["value_set"] = set(col.pop(k, {}))
                        except TypeError as e:
                            raise TypeError(k, col, e)
                        categorical["mode"] = k
                        col["categorical"] = categorical
                        break

                if "unique" in col:
                    categorical = col.get("categorical", {})
                    categorical["unique"] = col.pop("unique")
                    col["categorical"] = categorical

        return (schema, 2.0)
