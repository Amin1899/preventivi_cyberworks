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


def test_cli_confronta():
    storage.add_preventivo(
        {"cliente": "A", "data": date.today().isoformat(), "file": "a.pdf"}
    )
    storage.add_preventivo(
        {"cliente": "B", "data": date.today().isoformat(), "file": "b.pdf"}
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["confronta", "1", "2"])
    assert result.exit_code == 0
    assert "Confronto ID 1 vs ID 2" in result.output
    # deve evidenziare differenza cliente
    assert "cliente" in result.output and "≠" in result.output
