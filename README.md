# DFS (aka Dataframe_Schema)

**DFS** is a lightweight validator for `pandas.DataFrame`. You can think of it as a `jsonschema` for dataframe. 

Key features:
1. **Lightweight**: only dependent on `pandas`  and `pydantic` (which depends only on `typing_extensions`)
2. **Explicit**: inspired by `JsonSchema`, all schemas are stored as json (or yaml) files and can be generated or changed on the fly.
3. **Simple**: Easy to use, no need to change your workflow and dive into the implementation details. 
4. **Comprehensive**: Summarizes all errors in a single summary exception, checks for distributions, works on subsets of the dataframe 
5. **Rapid**: base schemas can be generated from given dataframe or sql query (using `pd.read_sql`).
6. **Handy**: Supports command line interface (with `[cli]` extra).
7. **Extendable**: Core idea is to validate *dataframes* of any type. While now supports only pandas, we'll add abstractions to run same checks on different types of dataframes (CuDF, Dask, SparkDF, etc )

## QuickStart

### 1. Validate DataFrame

Via wrapper
```python
import pandas as pd
import dfschema as dfs


df = pd.DataFrame({
  "a": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  "b": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
})

schema_pass = {
  "shape": {"min_rows": 10}
}

schema_raise = {
  "shape": {"min_rows": 20}
}


dfs.validate(df, schema_pass)  # won't raise any issues
dfs.validate(df, schema_raise) # will Raise DataFrameSchemaError
```
Alternatively (v2 optional), you can use the root class, `DfSchema`:
```python
dfs.DfSchema.from_dict(schema_pass).validate(df)  # won't raise any issues
dfs.DfSchema.from_dict(schema_raise).validate(df)  # will Raise DataFrameSchemaError
```

### 2. Generate Schema

```python
dfs.DfSchema.from_df(df)
```
### 3. Read and Write Schemas
  
```python
schema = dfs.DfSchema.from_file('schema.json')
schema.to_file("schema.yml")
```

### 4. Using CLI
> Note: requires [cli] extra as relies on `Typer` and `click`

#### Validate via CLI
```shell
dfschema validate --read_kwargs_json '{delimiter="|"}' FILEPATH SCHEMA_FILEPATH
```
Supports
- csv
- xlsx
- parquet
- feather

#### Generate via CLI
```shell
dfs generate --format 'yaml' DATA_PATH > schema.yaml
```

## Installation

WIP

## Alternatives
- [TableScheme](https://pypi.org/project/tableschema/)
- [GreatExpectations](https://greatexpectations.io/). Large and complex package with Html reports, Airflow Operator, connectors, etc. an work on out-of-memory data, SQL databases, parquet, etc
- [Pandera](https://pandera.readthedocs.io/en/stable/) - awesome package, great and suitable for type hinting, compatible with `hypothesis`
  - [great talk](https://www.youtube.com/watch?v=PI5UmKi14cM)
- [Tensorflow validate](https://www.tensorflow.org/tfx/guide/tfdv)
- [DTF expectations](https://github.com/calogica/dbt-expectations)

## Changes
- [[changelog]]

## Roadmap
- [ ] Add tutorial Notebook
- [ ] Support tableschema
- [ ] Support Modin models
- [ ] Support SQLAlchemy ORM models
- [ ] Built-in Airflow Operator?
- [ ] Interactive CLI/jupyter for schema generation