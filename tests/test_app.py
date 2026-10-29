from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_starts_without_uploaded_files() -> None:
    app_path = Path(__file__).parents[1] / "app.py"

    app = AppTest.from_file(str(app_path)).run(timeout=10)

    assert not app.exception
    assert app.title[0].value == "Omics Research Workspace"
