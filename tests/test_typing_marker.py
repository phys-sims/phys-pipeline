from importlib import resources


def test_py_typed_marker_present() -> None:
    marker = resources.files("phys_pipeline").joinpath("py.typed")
    assert marker.is_file()
