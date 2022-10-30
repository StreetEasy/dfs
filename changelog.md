# Changelog




v0.0.6:
    - `DfSchema.to_file`, `DfSchema.from_file` proper testing
    - CLI command help texts
    - added pre-commit install to the repo
    - Some benchmarking
v0.0.5: fix column dtype generation/validation bug

## Pre-Publication
v1.3.0
- renamed strict_column_set to additionalColumns
- renamed strict_column_order to exactColumnOrder

v1.2.0
- Metadata SubObject
- Summary Exception is now collected for specific DfSchema, not via Borg State
- Supports SubSets
- Support reading and writing schemas as yaml
- added `validate_sql` method (based on `pd.read_sql` for everything including dtype mapping)
- added cli support for schema generation or validation
- support for subsets in `from_df`
- support for `str_patterns` (string columns are matched against string prefix / regex patterns )

v1.1.0
- added support for "exact_set" (exact match of categorical values)
- better structure of tests and code
- added `summary` argument. If True, all tests will be ran and errors will be summarized in `DataFrameSummaryError` exception.
- re-enabled schema generation
