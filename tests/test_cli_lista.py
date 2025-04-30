from click.testing import CliRunner
from preventivi_cyberworks.cli import cli
from preventivi_cyberworks import storage
from datetime import date
import pytest


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "_DB_DIR", tmp_path / ".preventivi_test")
    monkeypatch.setattr(storage, "_DB_FILE", storage._DB_DIR / "db.json")
    yield


def test_cli_lista_mostra_record():
    storage.add_preventivo(
        {"cliente": "Test", "data": date.today().isoformat(), "file": "x.pdf"}
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["lista"])
    assert result.exit_code == 0
    assert "Test" in result.output
