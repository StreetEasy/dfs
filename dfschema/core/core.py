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

# from .utils import SchemaEncoder
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


class DfSchema(BaseModel):  # type: ignore
    """Main class of the package

    Represents a Schema to check (validate) dataframe against. Schema
    is flavor-agnostic (does not specify what kind of dataframe it is)
    """

    class Config:
        extra = Extra.forbid
        arbitrary_types_allowed = True

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
        """validate Dataframe aganist this schema

        validate dataframe agains the schema as a dictionary. will raise
        either DataFrameSummaryError (if summary=True) or DataFrameValidationError for specific
        problem (if summary=False)

        ### Example
        ```python
        import pandas as pd
        from dfschema import DfSchema

        path = '/schema.json'

        df = pd.DataFrame({'a':[1,2], 'b':[3,4]})
        dfs.DfSchema.from_file(path).validate_df(df)
        ```

        Args:
            df (pd.DataFrame): A dataframe to validate
            summary (bool): if `False`, raise exception on first violation (faster), otherwise will collect all violations and raise summary exception (slower)


        """
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
        """validate SQL table. Relies on `pandas.read_sql` to infer datatypes

        Right now does not support sampling, but this could be added in the future

        Args:
            sql (str): SQL statement (query) to run
            con (sqlalchemy.connection): connection to the database
            read_sql_kwargs (dict): Optional set of params to pass to `pd.read_sql_kwargs`
            summary (bool): if `False`, raise exception on first violation (faster), otherwise will collect all violations and raise summary exception (slower)
        Returns:
            None
        """
        df = pd.read_sql(sql, con, **(read_sql_kwargs or {}))
        self.validate_df(df, summary=summary)

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "DfSchema":
        """create DfSchema from file

        Method supports json and yaml formats
        Note: this is a class method, not instance method.
        PyYaml package is required to read yaml.

        Args:
            path (str or Path): path to the file, either json or yaml"
        Returns:
            DfSchema: DfSchema object instance
        """

        if isinstance(path, str):
            path = Path(path)

        try:
            if path.suffix == ".json":
                with path.open("r") as f:
                    schema = json.load(f)
            elif path.suffix in (".yml", ".yaml"):
                try:
                    import yaml

                    with path.open("r") as f:
                        schema = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYaml is required to load yaml files")
            else:
                raise ValueError(
                    f"Unsupported file extension: {path.suffix}, should be one of .json or .yml"
                )
            return cls.from_dict(schema)
        except Exception as e:
            raise DataFrameSchemaError(f"Error loading schema from file {path}") from e

    def to_file(self, path: Union[str, Path]) -> None:
        """write chema to file

        Supports json and yaml.

        Args:
            path (str, Path): path to write file to.
        Returns:
            None
        """
        if isinstance(path, str):
            path = Path(path)

        try:

            if path.suffix == ".json":
                schema_json = self.json(exclude_none=True, indent=4)
                with path.open("w") as f:
                    f.write(schema_json)
            elif path.suffix in (".yml", ".yaml"):
                schema_dict = self.dict(exclude_none=True)

                try:
                    import yaml

                    with path.open("w") as f:
                        yaml.dump(schema_dict, f)
                except ImportError:
                    raise ImportError("PyYaml is required to load yaml files")
            else:
                raise ValueError(
                    f"Unsupported file extension: {path.suffix}, should be one of .json or .yml"
                )

        except Exception as e:
            raise DataFrameSchemaError(f"Error wriging schema to file {path}") from e

    @classmethod
    def from_dict(cls, dict_: dict,) -> "DfSchema":
        """create DfSchema from dict.

        same as `DfSchema(**dict_)`, but will also migrate old protocol schemas if necessary.

        Args:
            dict_ (dict): dictionary to generate DfSchema from
        Returns:
            DfSchema: instance of DfSchema
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
        """generate DfSchema object from given dataframe.

        By default will generate strict schema that given dataframe should match.
        Do not expect it to generate good schema, rather a scaffolding to build
        one manually from.

        Note: this is a class method, not an instance method.

        Args:
            df (pd.DataFrame): dataframe to generate from
            subset_predicates (List[dict]): Optional list of dictionary predicates to generate subsets from
            return_dict (bool): wether return a dictionary instead of DfSchema instance (mostly for debugging purposes)
        Return:
            Union[DfSchema, dict]: either an instance of a class, or a dictionary
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
    Subset is almost identical to DfSchema,
    except it is assumed to run validation on a SUBSET of the dataframe.
    It also has a `predicate` attribute that defines way to retrieve this subset from
    the root dataframe.

    Also it raises `SubsetSummaryError` instead of `DataFrameSummaryError`

    """

    _predicate_description = """
    predicate to select subset.
    - If string, will be interpreted as query for `df.query()`.
    - If dict, keys should be column names, values should be values to exactly match"""
    predicate: Union[dict, str,] = Field(..., description=_predicate_description)

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
        """validate Dataframe aganist this schema

        validate dataframe agains the schema as a dictionary. will raise
        either SubsetSummaryError or DataFrameValidationError for specific
        problem

        Args:
            df (pd.DataFrame): A dataframe to validate
        Returns:
            None
        """
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
        """generate SubsetSchema object from given dataframe and a predicate

        By default will generate strict schema that given dataframe should match.
        Do not expect it to generate good schema, rather a scaffolding to build
        one manually from.

        Note: this is a class method, not an instance method.

        Args:
            df (pd.DataFrame): dataframe to generate from
            predicate (dict, str, Callable): Predicate to filter by. If string, will use it as an argument to `df.query`.\nIf callable, assumes it to be a function that returns a subset if given a dataframe.\nIf dictionary, will assume keys to be columns and values - sets of possible values.
            return_dict (bool): wether return a dictionary instead of SubsetSchema instance (mostly for debugging purposes)
        Return:
            Union[SubsetSchema, dict]: either an instance of a class, or a dictionary
        """
        filtered_df = cls._filter(df, predicate=predicate)

        schema = generate_schema_dict_from_df(filtered_df)
        schema["predicate"] = predicate

        if return_dict:
            return schema

        return cls(**schema)


DfSchema.update_forward_refs()  # Note: required because of self-referencing
