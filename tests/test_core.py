import os
import pytest
from preventivi_cyberworks.core import generate_preventivo


def test_generate_preventivo_creates_file(tmp_path, capsys):
    cliente = "TestCliente"
    dest = tmp_path / "test_preventivo.pdf"
    # Prima del test il file non deve esistere
    assert not dest.exists()

    # Genera il PDF in verbose per catturare i log
    generate_preventivo(cliente, str(dest), verbose=True)

    # Il file deve esistere e non essere vuoto
    assert dest.exists()
    assert dest.stat().st_size > 0

    # Verifica i log debug in stdout
    captured = capsys.readouterr()
    assert f"[DEBUG] Inizio generazione PDF per: {cliente}" in captured.out
    assert "[DEBUG] PDF generato con successo." in captured.out
