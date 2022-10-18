import pytest
from typer.testing import CliRunner

runner = CliRunner(mix_stderr=False)


@pytest.mark.parametrize("format", ["json", "yaml"])
def test_cli_generate(format):
    from dfs.cli import app
    import json
    import yaml

    result = runner.invoke(
        app, ["generate", "--format", format, "tests/test_data/test1.csv"]
    )
    assert result.exit_code == 0, result.stdout
    assert "metadata" in result.stdout, result.stdout

    if format == "json":
        assert json.loads(result.stdout)
    elif format == "yaml":
        assert yaml.safe_load(result.stdout)


def test_cli_validate():
    from dfs.cli import app

    result = runner.invoke(
        app,
        [
            "validate",
            "tests/test_data/test1.csv",
            "tests/test_schemas/v2/good/v2_raw.json",
        ],
    )
    assert result.exit_code == 0
    assert "File passed the validation!" in result.stdout


def test_cli_validate_error():
    from dfs.cli import app

    result = runner.invoke(
        app,
        [
            "validate",
            "tests/test_data/test1.csv",
            "tests/test_schemas/v2/good/v2_raw2.json",
        ],
    )
    # assert result.exit_code == 1
    assert "File violates schema:" in result.stderr
