from preventivi_cyberworks import storage
from datetime import date
import os


def test_add_and_list(tmp_path, monkeypatch):
    # isola il DB sull’fs temporaneo
    monkeypatch.setattr(storage, "_DB_DIR", tmp_path / ".preventivi_test")
    monkeypatch.setattr(storage, "_DB_FILE", storage._DB_DIR / "db.json")

    rec = {"cliente": "ClienteTest", "data": date.today().isoformat(), "file": "x.pdf"}
    storage.add_preventivo(rec)

    res = storage.list_preventivi("ClienteTest")
    assert len(res) == 1
    assert res[0]["cliente"] == "ClienteTest"
