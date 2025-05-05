from click.testing import CliRunner
from preventivi_cyberworks.cli import cli
from preventivi_cyberworks import storage
import pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "_DB_DIR", tmp_path / ".db")
    monkeypatch.setattr(storage, "_DB_FILE", storage._DB_DIR / "db.json")
    yield

def test_cli_importa_auto(sample_pdf, monkeypatch):
    runner = CliRunner()
    result = runner.invoke(cli, ["importa", sample_pdf])
    assert result.exit_code == 0
    out = result.output
    assert "Importato" in out and "ACME S.p.A." in out and "123,45" in out

    # Verifica che lo storage contenga il record
    recs = storage.list_preventivi()
    assert recs and recs[0]["cliente"] == "ACME S.p.A."
