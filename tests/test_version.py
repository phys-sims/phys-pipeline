from phys_pipeline import __version__


def test_version_matches_release() -> None:
    assert __version__ == "2.0.0"
