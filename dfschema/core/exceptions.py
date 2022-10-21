class DataFrameValidationError(Exception):
    pass


class DataFrameSchemaError(Exception):
    pass


class SubsetSummaryError(DataFrameValidationError):
    pass


class DataFrameSummaryError(DataFrameValidationError):
    pass
