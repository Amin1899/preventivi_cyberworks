"""
Gestione dello “storico” preventivi su file JSON.
Percorso default: ~/.preventivi_cyberworks/db.json
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List

_DB_DIR = Path.home() / ".preventivi_cyberworks"
_DB_FILE = _DB_DIR / "db.json"


def _ensure_dir() -> None:
    """Crea la cartella ~/.preventivi_cyberworks se non esiste."""
    _DB_DIR.mkdir(parents=True, exist_ok=True)


def _default_db() -> Dict[str, List[dict]]:
    """Struttura iniziale dell’archivio."""
    return {"preventivi": []}


def load_db() -> Dict[str, List[dict]]:
    """Carica l’archivio; se non esiste lo crea vuoto."""
    _ensure_dir()
    if not _DB_FILE.exists():
        return _default_db()
    with _DB_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data: Dict[str, List[dict]]) -> None:
    """Salva l’archivio su disco (pretty-print, UTF-8)."""
    _ensure_dir()
    with _DB_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_preventivo(record: dict) -> None:
    """Aggiunge un record (dict) all’archivio."""
    db = load_db()
    db["preventivi"].append(record)
    save_db(db)


def list_preventivi(cliente: str | None = None) -> List[dict]:
    """Ritorna tutti i preventivi (filtrati per cliente se specificato)."""
    db = load_db()
    items = db["preventivi"]
    if cliente:
        items = [p for p in items if p["cliente"].lower() == cliente.lower()]
    # ordina per data (stringa ISO YYYY-MM-DD)
    return sorted(items, key=lambda p: p["data"])
