from importlib.metadata import version

from practicelens import __version__


def test_package_version_matches_installed_metadata() -> None:
    assert __version__ == version("practicelens")
