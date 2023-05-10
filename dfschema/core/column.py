import sys
from datetime import date, datetime
from typing import List, Optional, FrozenSet, Union, Tuple  # , Pattern
from warnings import warn

import pandas as pd
from pydantic import BaseModel, Extra, Field  # , validator

from .dtype import DtypeAliasPool, DtypeLiteral
from .exceptions import DataFrameSchemaError, DataFrameValidationError
from .logger import logger
from .collector import exception_collector

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


@exception_collector
def _validate_column_presence(
    df: pd.DataFrame,
    column_names: Tuple[str],
    additionalColumns: bool = True,
    exactColumnOrder: bool = False,
) -> None:
    """Validate that columnns defined in schma are present in dataframe.
    If `additionalColumns` is False, raise an error if any extra column is present"""
    if not additionalColumns:
        other_cols = tuple(col for col in df.columns if col not in column_names)

        if len(other_cols) != 0:
            text = f"Some columns should not be in dataframe: {other_cols}"
            raise DataFrameValidationError(text)

    lac_cols = [col for col in column_names if col not in df.columns]
    if len(lac_cols) != 0:
        text = f"Some columns are not in dataframe: {lac_cols}"
        raise DataFrameValidationError(text)

    if exactColumnOrder:
        dfcols = list(df.columns)[: len(column_names)]
        if dfcols != column_names:
            text = (
                f"Order of columns is not exact, should be {column_names}, got {dfcols}"
            )
            raise DataFrameValidationError(text)


class ValueLimits(BaseModel):  # type: ignore
    min: Union[float, date, datetime, str, None] = None
    max: Union[float, date, datetime, str, None] = None

    class Config:
        extra = Extra.forbid
        use_enum_values = True

    @exception_collector
    def validate_column(self, series: pd.Series, col_name: Optional[str] = None) -> None:  # type: ignore
        _text: str = "Column `{name}` violates value limits: {detail}"
        col_name: str = col_name or str(series.name)  # type: ignore

        if (self.min is not None) and (self.max is not None):
            mask = series.between(self.min, self.max) | series.isna()
            logger.debug(
                f"Testing column {col_name} for value limits: {self.min} <= `{col_name}` <= {self.max}"
            )

            if not mask.all():
                series_min, series_max = series.min(), series.max()
                txt = _text.format(
                    name=col_name,
                    detail=f"values go beyound boundaries: {self.min} <= ({series_min}-{series_max}) <= {self.max} ",
                )
                raise DataFrameValidationError(txt)

        elif self.min is not None:
            logger.debug(
                f"Testing column {col_name} for value limits: `{col_name}` >= {self.min}"
            )
            series_min = series.min()

            if series_min < self.min:
                txt = _text.format(
                    name=col_name,
                    detail=f"values go below minimum: {series_min} < {self.min}",
                )
                raise DataFrameValidationError(txt)

        elif self.max is not None:
            logger.debug(
                f"Testing column {col_name} for value limits: `{col_name}` <= {self.max}"
            )
            series_max = series.max()
            if series_max > self.max:
                txt = _text.format(
                    name=col_name,
                    detail=f"values go below maximum: {series_max} > {self.max}",
                )
                raise DataFrameValidationError(txt)
        else:
            raise DataFrameSchemaError(f"Broken Value Limit: {self.to_dict()}")


class DistributionMetric(BaseModel):  # type: ignore
    class Config:
        extra = Extra.forbid
        use_enum_values = True

    name: Literal["mean", "std", "median", "quantile"]
    range: Tuple[float, float]
    kwargs: dict = Field(
        {}, description="Additional arguments for the metric to be passed via **kwargs"
    )

    @exception_collector
    def validate_column(self, series: pd.Series, col_name: Optional[str] = None) -> None:  # type: ignore
        if self.name == "quantile" and "q" not in self.kwargs:
            raise DataFrameSchemaError(
                "Quantile metric requires `q` argument in kwargs within [0,1]"
            )

        value = getattr(series, self.name)(**self.kwargs)

        if not self.range[0] <= value <= self.range[1]:
            txt = f"Metric {self.name} for column `{col_name}` is outside the range [{self.range[0]}, {self.range[1]}]"
            raise DataFrameValidationError(txt)


class Distribution(BaseModel):  # type: ignore
    class Config:
        extra = Extra.forbid
        use_enum_values = True

    metrics: List[DistributionMetric] = []

    def validate_column(self, series: pd.Series, root, col_name: Optional[str] = None) -> None:  # type: ignore
        for metric in self.metrics:
            metric.validate_column(series, col_name, root=root)


class Categorical(BaseModel):  # type: ignore
    value_set: Optional[Union[FrozenSet[int], FrozenSet[float], FrozenSet[str],]] = None
    mode: Optional[Literal["oneof", "exact_set", "include"]] = None
    unique: bool = Field(
        False, description="if true, the column must contain only unique values"
    )

    class Config:
        extra = Extra.forbid

    @exception_collector
    def _validate_unique(self, vc: pd.Series, col_name: str) -> None:
        if vc.iloc[0] > 1:
            most_frequent = vc.index[0]
            txt = f"Column `{col_name}` is not unique. Most frequent value is `{most_frequent}`"
            raise DataFrameValidationError(txt)

    @exception_collector
    def _validate_oneof(self, vc: pd.Series, col_name: str) -> None:
        mask = vc.index.isin(self.value_set)
        if not mask.all():
            not_one_of = set(vc.index[~mask])  # type: ignore
            txt = f"Column `{col_name}` contains values not in set: `{not_one_of}`, should be one of `{self.value_set}`"
            raise DataFrameValidationError(txt)

    @exception_collector
    def _validate_include(self, vc: pd.Series, col_name: str) -> None:
        diff = self.value_set - set(vc.index)  # type: ignore
        if len(diff) > 0:
            txt = f"Column `{col_name}` contains does not include: `{diff}` columns"
            raise DataFrameValidationError(txt)
        pass

    def validate_column(self, series: pd.Series, col_name: str, root) -> None:
        vc = series.value_counts()

        if self.value_set:
            if self.mode in {"oneof", "exact_set"}:
                self._validate_oneof(vc, col_name, root=root)
            if self.mode in {"include", "exact_set"}:
                self._validate_include(vc, col_name, root=root)

        if self.unique:
            self._validate_unique(vc, col_name, root=root)


class ColSchema(BaseModel):
    name: str = Field(..., description="Name of the column")
    dtype: Optional[DtypeLiteral] = Field(None, description="Data type of the column")  # type: ignore

    # accepted for value limitation checks
    _val_accepted_types = {None, "int", "float", "datetime64[ns]"}

    na_limit: Optional[float] = Field(
        None,
        ge=0,
        lt=1.0,
        description="limit of missing values. If set to true, will raise if all values are empty. If set to a number, will raise if more than that fraction of values are empty (Nan)",
    )
    value_limits: Optional[ValueLimits] = Field(
        None, description="Value limits for the column"
    )
    categorical: Optional[Categorical] = Field(
        None, description="Categorical expectations for the column"
    )

    distribution: Optional[Distribution] = Field(
        None, description="Distribution expectations for the column"
    )

    str_pattern: Union[str, List[str], None] = Field(
        None,
        description="Regex pattern for string columns. Should pass `pd.Series.str.match`",
    )
    _dtypepool: dict = DtypeAliasPool

    class Config:
        extra = Extra.forbid
        use_enum_values = True

    def _map_dtype(
        self, dtype: Optional[str] = None, raise_error: bool = True
    ) -> Optional[str]:
        if dtype in self._dtypepool:
            return self._dtypepool[dtype]
        else:
            if raise_error:
                raise ValueError(f"Unsupported dtype: {self.dtype}")
            else:
                warn(f"Unsupported dtype: {self.dtype}")
        return None

    # abstract dtypes with a corresponding checker
    _dtype_test_func = {
        "numeric": pd.api.types.is_numeric_dtype,
        "int": pd.api.types.is_integer_dtype,
        "float": pd.api.types.is_float_dtype,
        "string": lambda s: (pd.api.types.is_string_dtype(s) or pd.isnull(s).all()),
        "timedelta64[ns]": pd.api.types.is_timedelta64_dtype,
    }

    @exception_collector
    def _validate_dtype(self, series: pd.Series) -> None:
        _tmplt: str = "Column `{0}` has wrong datatype: {1}, should be {2} ({3})"
        _dtype = self._map_dtype(self.dtype)

        if _dtype and (_dtype in self._dtype_test_func.keys()):
            if not self._dtype_test_func[_dtype](series):
                txt = _tmplt.format(self.name, series.dtype, _dtype, self.dtype)
                raise DataFrameValidationError(txt)
        elif series.dtype != _dtype:
            txt = _tmplt.format(self.name, series.dtype, _dtype, self.dtype)
            raise DataFrameValidationError(txt)

    @exception_collector
    def _validate_na_limit(self, series: pd.Series) -> None:
        na_fraction = series.isnull().mean()

        if na_fraction > self.na_limit:  # type: ignore
            text = f"Column `{self.name}` has too many NAs: {na_fraction}, should be <= {self.na_limit}"
            raise DataFrameValidationError(text)

    @exception_collector
    def _validate_str_patterns(self, series: pd.Series) -> None:
        """
        validates that the series matches the regex pattern or string (using `pd.Series.str.match`)
        details: https://pandas.pydata.org/docs/reference/api/pandas.Series.str.match.html
        """
        if not pd.api.types.is_string_dtype(series):
            raise DataFrameSchemaError(
                f"Column `{self.name}` is not a string dtype: can't validate string patterns"
            )

        if isinstance(self.str_pattern, str):
            ptrns = [
                self.str_pattern,
            ]
        else:
            ptrns = self.str_pattern  # type: ignore

        mask = series.isnull()
        for ptrn in ptrns:  # type: ignore
            mask = mask | series.str.contains(ptrn)
        if not mask.all():
            invalid_example = [el for el in series.loc[~mask].sample(3, random_state=0)]
            raise DataFrameValidationError(
                f"Column `{self.name}` does not match patterns `{ptrns}`: {invalid_example}"
            )

    def validate_column(self, series: pd.Series, root) -> None:
        """if use `validate`, raises Pydantic exception"""

        if self.dtype:
            self._validate_dtype(series, root=root)

        if self.na_limit:
            self._validate_na_limit(series, root=root)

        if self.value_limits:
            mapped_dtype = self._map_dtype(str(series.dtype), raise_error=False)

            if mapped_dtype in self._val_accepted_types:
                self.value_limits.validate_column(series, self.name, root=root)
            else:
                warn(
                    f"Dtype `{series.dtypes}` for Column `{self.name}` is not supported by `value_limits`, should be one of `{self._val_accepted_types}`. Ignoring value limits "
                )

        if self.str_pattern:
            self._validate_str_patterns(series, root=root)

        if self.distribution:
            mapped_dtype = self._map_dtype(str(series.dtype), raise_error=False)

            if mapped_dtype in self._val_accepted_types:
                self.distribution.validate_column(
                    series=series, col_name=self.name, root=root
                )
            else:
                warn(
                    f"Dtype `{series.dtypes}` for Column `{self.name}` is not supported by `distribution limits`, should be one of `{self._val_accepted_types}`. Ignoring value limits "
                )

        if self.categorical:
            self.categorical.validate_column(series, self.name, root=root)
