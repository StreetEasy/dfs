class DataFrameValidationError(Exception):
    """root DataFrame Validation Exception"""

    pass


class DataFrameSchemaError(Exception):
    """Schema Error Exception. Something wrong with the schema itself"""

    pass


class SubsetSummaryError(DataFrameValidationError):
    """Subset Summary Error. Summary Error for a sub-dataframe"""

    pass


class DataFrameSummaryError(DataFrameValidationError):
    """DataFrame Summary Error. Summary Error for a dataframe with a collection
    of all violations"""

    pass
