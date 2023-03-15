try:
    import typer
except ImportError:
    raise ImportError("typer is required, install with `dfs[cli]` extra")

from typing import Optional
import pandas as pd
from enum import Enum
from pathlib import Path

from .core import DfSchema


class Format(str, Enum):
    yaml = "yaml"
    json = "json"


app = typer.Typer()


def _infer_read_df(path: Path, **kwargs) -> pd.DataFrame:
    methods = {
        ".csv": pd.read_csv,
        ".xlsx": pd.read_excel,
        ".parquet": pd.read_parquet,
        ".feather": pd.read_feather,
    }

    extension = path.suffix
    if extension not in methods:
        raise ValueError(
            f"Unsupported extension: {extension}, should be one of {list(methods.keys())}"
        )

    return methods[extension](path, **kwargs)


@app.command()
def validate(
    file: Path = typer.Argument(..., help="Data file to validate"),
    schema: Path = typer.Argument(..., help="Schema file to validate against"),
    read_kwargs_json: Optional[str] = typer.Option(
        None, help="Extra read options to be passed to pandas method, as a json objec"
    ),
    summary: bool = typer.Option(
        True,
        help="Print summary of validation results. If `no-summary`, will stop at first violation (faster)",
    ),
):
    """
    Validate data from file against given schema
    """
    if read_kwargs_json is not None:
        import json

        read_kwargs: dict = json.loads(read_kwargs_json)  # type: ignore
    else:
        read_kwargs: dict = dict()  # type: ignore

    df = _infer_read_df(file, **read_kwargs)
    Schema = DfSchema.from_file(schema)

    try:
        Schema.validate_df(df, summary=summary)
    except Exception as e:
        typer.echo(f"File violates schema: {e}", err=True)
    else:
        typer.echo("File passed the validation!")


@app.command()
def generate(
    file: Path = typer.Argument(..., help="data file to generate schema from"),
    format: Format = typer.Option(
        "json",
        help="output format, either `json` or `yaml`",
        show_default=True,
        prompt=True,
    ),
):
    """
    Generate Schema from given dataset.

    Will Print Schema to stdout. to write it to the file, use piping:
    $ dfschema generate data.csv > schema.dfs.json
    """
    df = _infer_read_df(file)
    S: DfSchema = DfSchema.from_df(df)  # type: ignore

    if format.value == "json":
        import json

        print(json.dumps(S.dict(exclude_none=True), indent=4))
    elif format.value == "yaml":
        import yaml

        print(yaml.dump(S.dict(exclude_none=True), indent=4))
    else:
        raise ValueError(
            f"Unsupported extension: {format}, should be one of [json, yaml]"
        )
