# Changelog

v0.0.10:
- relaxed Pydantic requirement to `>=1.9`

v0.0.9:
- Pydantic bumped to `1.10`
- Bug Fix: Categorical constraints (`exact_set`, `oneof`, `include`) now can keeo `int` and `float` values. That expands to legacy schemas as well.

v0.0.8:
Legacy Schema Aliases (support for legacy schemas):
- `min_value` now also supports `min` alias
- `max_value` now also supports `max` alias
- `oneof` now also supports `one_of` alias
- `version` is now correctly moved to `metadata` from root on migration
- If column schema has both `oneof` and `includes` and they are identical, will replace with `exact_set`

Testing:
- conftest code improved to showcase bad json on Exception
- multiple v1 schemas were added for testing
- pre-commit setup was updated


v0.0.7:
- rename `DfSchema.validate_df` to `DfSchema.validate` (UNDONE: `validate` is reserved by Pydantic object)
- updated documentation

v0.0.6:
    - `DfSchema.to_file`, `DfSchema.from_file` proper testing
    - CLI command help texts
    - added pre-commit install to the repo
    - Some benchmarking
    - renamed `dfs.validate_df` to `dfs.validate`
    
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
