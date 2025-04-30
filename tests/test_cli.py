import os
from click.testing import CliRunner
from preventivi_cyberworks.cli import cli


def test_cli_genera_crea_pdf(tmp_path):
    runner = CliRunner()
    dest = tmp_path / "preventivo_cli.pdf"
    # Assicurarsi che il file non esista prima
    assert not dest.exists()

    # Esegui il comando genera con destinazione assoluta
    result = runner.invoke(cli, ["genera", "ClienteCLI", "-d", str(dest)])

    # Verifica exit code
    assert result.exit_code == 0
    # Output corretto
    assert f"Preventivo per 'ClienteCLI' salvato in '{dest}'" in result.output
    # Il file PDF deve esistere e non essere vuoto
    assert dest.exists()
    assert dest.stat().st_size > 0


def test_cli_verbose(tmp_path):
    runner = CliRunner()
    dest = tmp_path / "preventivo_verbose.pdf"
    assert not dest.exists()

    # Esegui con --verbose
    result = runner.invoke(cli, ["--verbose", "genera", "ClienteCLI", "-d", str(dest)])

    # exit code OK
    assert result.exit_code == 0
    # Debug logs presenti
    assert "[DEBUG] Verbose mode attivo." in result.output
    assert f"[DEBUG] Inizio generazione PDF per: ClienteCLI" in result.output
    # PDF generato correttamente
    assert dest.exists()
    assert dest.stat().st_size > 0
