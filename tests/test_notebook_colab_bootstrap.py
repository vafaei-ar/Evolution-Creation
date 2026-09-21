import json
from pathlib import Path


NOTEBOOK_DIR = Path("notebooks")


def _notebooks():
    return sorted(NOTEBOOK_DIR.glob("*.ipynb"))


def test_all_notebooks_have_robust_colab_bootstrap():
    notebooks = _notebooks()
    assert len(notebooks) >= 16

    for path in notebooks:
        payload = json.loads(path.read_text())
        code_cells = [
            cell
            for cell in payload["cells"]
            if cell.get("cell_type") == "code"
        ]
        assert code_cells, path
        setup = "".join(code_cells[0].get("source", []))

        assert "import google.colab" in setup, path
        assert "IN_COLAB = True" in setup, path
        assert "sys.path.insert(0, src_path)" in setup, path
        assert "'google.colab' in sys.modules" not in setup, path


def test_notebooks_do_not_use_fragile_colab_detection_anywhere():
    for path in _notebooks():
        text = path.read_text()
        assert "'google.colab' in sys.modules" not in text, path


def test_explorer_uses_resolved_repo_dir_for_data():
    path = NOTEBOOK_DIR / "interactive_continental_explorer.ipynb"
    text = path.read_text()
    assert "REPO_DIR / 'data' / 'continental_explorer_defaults.json'" in text


def test_evidence_notebook_uses_resolved_repo_dir_for_data():
    path = NOTEBOOK_DIR / "10_evidence_calibration.ipynb"
    text = path.read_text()
    assert "REPO_DIR / 'data' / 'model10_evidence.json'" in text
