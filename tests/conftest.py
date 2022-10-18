import pytest
import pandas as pd
import numpy as np
from hypothesis.extra.pandas import column, data_frames
from pathlib import Path
import json


@pytest.fixture()
def df1():
    return pd.DataFrame({"x": [1, 2, 3, 4], "y": ["foo", "bar", "baz", None]})


def df1_hypothesis():
    return data_frames(
        columns=[
            column("x", dtype=int),
            column("y", dtype=str, elements=["foo", "bar", "baz"]),
        ]
    )


@pytest.fixture()
def df2():
    return pd.DataFrame({"x": [None, 2, 3, 4], "y": ["foo", "bar", "baz", None]})


@pytest.fixture()
def df3():
    return pd.DataFrame({"x": [np.nan] * 4, "y": ["foo", "bar", "baz", np.nan]})


# This section for `test_jsonvalidate.py`


def _get_schemas_v1(name):
    """
    Gets json schemas
    """
    test_dir = Path(__file__).parent / "test_schemas/v1/"

    schema_files = list((test_dir / name).glob("*.json"))
    assert len(schema_files) > 0, f"No schema files found in {test_dir / name}"
    return (
        {"name": file.stem, "schema": json.loads(file.read_text())}
        for file in schema_files
    )


def _get_schemas_v2(name):
    """
    Gets json schemas
    """
    test_dir = Path(__file__).parent / "test_schemas/v2/"

    schema_files = list((test_dir / name).glob("*.json"))
    assert len(schema_files) > 0, f"No schema files found in {test_dir / name}"
    return (
        {"name": file.stem, "schema": json.loads(file.read_text())}
        for file in schema_files
    )


def pytest_generate_tests(metafunc):
    """
    If a test uses one of the data fixtures this loops the test over
    each record in that dataset
    """
    if "good_schema" in metafunc.fixturenames:
        good_schemas = _get_schemas_v2("good")
        metafunc.parametrize("good_schema", good_schemas)
    elif "bad_schema" in metafunc.fixturenames:
        bad_schemas = _get_schemas_v2("bad")
        metafunc.parametrize("bad_schema", bad_schemas)

    elif "good_schema_v1" in metafunc.fixturenames:
        good_schemas = _get_schemas_v1("good")
        metafunc.parametrize("good_schema_v1", good_schemas)
    elif "bad_schema_v1" in metafunc.fixturenames:
        bad_schemas = _get_schemas_v1("bad")
        metafunc.parametrize("bad_schema_v1", bad_schemas)
