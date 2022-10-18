from datetime import date
from typing import Callable, Optional, Union, List
import json
from pathlib import Path


import pandas as pd
from pydantic import BaseModel, Extra, Field, PrivateAttr
import sys

from .column import ColSchema, _validate_column_presence
from .exceptions import DataFrameSchemaError, DataFrameSummaryError, SubsetSummaryError
from .shape import ShapeSchema
from .legacy import infer_protocol_version, LegacySchemaRegistry
from .generate import generate_schema_dict_from_df

# from .base_config import BaseConfig


if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

CURRENT_PROTOCOL_VERSION: Final = 2.0


class MetaData(BaseModel):
    protocol_version: float = Field(
        CURRENT_PROTOCOL_VERSION, description="protocol version of the schema"
    )
    version: Optional[str] = Field(
        date.today().strftime("%Y-%m-%d"),
        description="version of the schema",
        example="2022-06-12",
    )

    custom_settings: Optional[dict] = Field(
        None, description="custom settings. does not affect any logic"
    )


class DfSchema(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):  # type: ignore

    metadata: Optional[MetaData] = Field(
        MetaData(),
        description="optional metadata, including version and protocol version",
    )

    shape: Optional[ShapeSchema] = Field(None, description="shape expectations")
    columns: Optional[List[ColSchema]] = Field([], description="columns expectations")
    additionalColumns: bool = Field(
        True,
        description="if true, Will allow any additional columns not defined in the schema",
    )

    exactColumnOrder: bool = Field(
        False,
        description="if true, will require order of columns to exactly match column order in schema",
    )

    subsets: Optional[List["SubsetSchema"]] = Field(
        None, description="dataframe subset expectations"
    )

    _exception_pool: List[Exception] = PrivateAttr([])
    _summary: bool = PrivateAttr()

    def _summary_error(self) -> DataFrameSummaryError:
        error_list = "\n".join(
            [
                f"- {e.args[0]}"
                for e in self._exception_pool
                if not isinstance(e, SubsetSummaryError)
            ]
        )
        subset_summaries = "\n".join(
            [
                e.args[0]
                for e in self._exception_pool
                if isinstance(e, SubsetSummaryError)
            ]
        )

        txt = "Dataframe validation failed:"
        if error_list:
            txt += f"\n{error_list}"

        # NOTE: subset errors as a subsection
        if subset_summaries:
            txt += f"\n{subset_summaries}"

        return DataFrameSummaryError(txt)

    def validate_column_presence(self, df: pd.DataFrame) -> None:
        schema_col_names = {col.name for col in self.columns}  # type: ignore
        _validate_column_presence(
            df, schema_col_names, additionalColumns=self.additionalColumns, root=self
        )

    def validate_df(self, df: pd.DataFrame, summary: bool = True) -> None:
        """validate dataframe"""
        self._exception_pool = []
        self._summary = summary

        if not isinstance(df, pd.DataFrame):
            raise DataFrameSchemaError(
                f"Data should be `pd.DataFrame`, got `{type(df)}`"
            )

        if self.shape:
            self.shape.validate_df(df, root=self)

        if self.columns:
            self.validate_column_presence(df)

            for col in (col for col in self.columns if col.name in df.columns):
                col.validate_column(df[col.name], root=self)

        if self.subsets:
            for subset in self.subsets:
                subset.validate_df(df=df, root=self)

        if len(self._exception_pool) > 0:
            error = self._summary_error()
            raise error

    def validate_sql(
        self,
        sql: str,
        con,
        read_sql_kwargs: Optional[dict] = None,
        summary: bool = True,
    ) -> None:
        """validate SQL table. Function complately based on `pandas.read_sql`

        Right now does not support sampling, but could be added in the future
        """
        df = pd.read_sql(sql, con, **(read_sql_kwargs or {}))
        self.validate_df(df, summary=summary)

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "DfSchema":
        """create DfSchema from json file"""

        if isinstance(path, str):
            path = Path(path)

        try:
            if path.suffix == ".json":
                with path.open("r") as f:
                    schema = json.load(f)
            elif path.suffix == ".yaml":
                try:
                    import yaml

                    with path.open("r") as f:
                        schema = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYaml is required to load yaml files")
            else:
                raise ValueError(
                    f"Unsupported file extension: {path.suffix}, should be one of .json or .yaml"
                )
            return cls.from_dict(schema)
        except Exception as e:
            raise DataFrameSchemaError(f"Error loading schema from file {path}") from e

    @classmethod
    def from_dict(
        cls,
        dict_: dict,
    ) -> "DfSchema":
        """create DfSchema from dict, same as `DfSchema(**dict_)`\n
        except this will migrate old schemas if necessary
        """

        pv = infer_protocol_version(dict_)
        if pv == CURRENT_PROTOCOL_VERSION:
            return cls(**dict_)
        else:
            while pv < CURRENT_PROTOCOL_VERSION:
                dict_, pv = LegacySchemaRegistry[pv](**dict_).migrate()
            return cls(**dict_)

    @classmethod
    def from_df(
        cls,
        df: pd.DataFrame,
        subset_predicates: Optional[List[dict]] = None,
        return_dict: bool = False,
    ) -> Union["DfSchema", dict]:
        """
        generate Schema object from given dataframe.
        by default will generate strict schema that given dataframe should match.
        """

        schema = generate_schema_dict_from_df(df)
        subset_schemas = []
        if subset_predicates:
            for predicate in subset_predicates:
                filtered = SubsetSchema.filter_df(df, predicate)

                subset_schema = generate_schema_dict_from_df(filtered)
                subset_schema["predicate"] = predicate
                subset_schemas.append(subset_schema)

            schema["subsets"] = [subset_schemas]

        if return_dict:
            return schema

        return cls(**schema)


class SubsetSchema(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):  # type: ignore
    """
    Subset is essentially same as DfSchema,
    except it is assumed to run validation on a SUBSET of the dataframe.
    """

    _predicate_description = """
    predicate to select subset.
    - If string, will be interpreted as query for `df.query()`.
    - If dict, keys should be column names, values should be values to exactly match"""
    predicate: Union[
        dict,
        str,
    ] = Field(..., description=_predicate_description)

    shape: Optional[ShapeSchema] = Field(None, description="shape expectations")
    columns: Optional[List[ColSchema]] = Field([], description="columns expectations")

    additionalColumns: bool = Field(
        True,
        description="if true, Will allow any additional columns not defined in the schema",
    )

    exactColumnOrder: bool = Field(
        False,
        description="if true, will require order of columns to exactly match column order in schema",
    )

    _exception_pool: List[Exception] = PrivateAttr([])
    _summary: bool = PrivateAttr()

    def _summary_error(self, df_shape: tuple) -> SubsetSummaryError:
        error_list = "\n".join([f"- {e.args[0]}" for e in self._exception_pool])

        return SubsetSummaryError(
            f"Subset({self.predicate}, shape:{df_shape}) validation failed:\n{error_list}"
        )

    @staticmethod
    def _filter(df: pd.DataFrame, predicate) -> pd.DataFrame:
        """filter dataframe by predicate"""

        if isinstance(predicate, str):
            return df.query(predicate)

        elif isinstance(predicate, dict):
            mask = pd.Series(True, index=df.index)

            for k, v in predicate.items():
                mask &= df[k] == v
            return df[mask]
        else:
            raise ValueError(f"Unsupported predicate type: {type(predicate)}")

    def validate_column_presence_and_order(self, df: pd.DataFrame) -> None:
        schema_col_names = tuple(col.name for col in self.columns)  # type: ignore

        _validate_column_presence(
            df,
            schema_col_names,
            additionalColumns=self.additionalColumns,
            exactColumnOrder=self.exactColumnOrder,
            root=self,
        )

    def validate_df(self, df: pd.DataFrame, root: DfSchema) -> None:
        """validate dataframe"""
        self._exception_pool = []
        self._summary = root._summary

        filtered_df = self._filter(df, self.predicate)

        if self.shape:
            self.shape.validate_df(filtered_df, root=self)

        if self.columns:
            self.validate_column_presence_and_order(filtered_df)

            for col in (col for col in self.columns if col.name in df.columns):
                col.validate_column(filtered_df[col.name], root=self)

        if self._exception_pool:
            summary_ = self._summary_error(filtered_df.shape)
            root._exception_pool.append(summary_)

    @classmethod
    def from_df(
        cls,
        df: pd.DataFrame,
        predicate: Union[dict, str, Callable],
        return_dict: bool = False,
    ) -> Union["SubsetSchema", dict]:
        filtered_df = cls._filter(df, predicate=predicate)

        schema = generate_schema_dict_from_df(filtered_df)
        schema["predicate"] = predicate

        if return_dict:
            return schema

        return cls(**schema)


DfSchema.update_forward_refs()  # Note: required because of self-referencing
