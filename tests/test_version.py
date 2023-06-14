import toml
from pathlib import Path
import dfschema


def test_versions_are_in_sync():
    """Checks if the pyproject.toml and package.__init__.py __version__ are in sync."""

    try:
        path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    except Exception as e:
        files = Path(__file__).resolve().parents[1]
        for item in files.iterdir():
            print(f"{item} - {'dir' if item.is_dir() else 'file'}")
        raise Exception(e)

    pyproject = toml.loads(open(str(path)).read())
    pyproject_version = pyproject["tool"]["poetry"]["version"]

    package_init_version = dfschema.__version__

    assert package_init_version == pyproject_version
