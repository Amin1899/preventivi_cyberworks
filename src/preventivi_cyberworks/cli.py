from datetime import date
from pathlib import Path

import click
from reportlab.pdfgen import canvas

from preventivi_cyberworks.storage import add_preventivo, list_preventivi, get_by_index


@click.group()
@click.option("--verbose", is_flag=True, help="Modalità verbosa.")
@click.pass_context
def cli(ctx, verbose):
    """Preventivi Cyberworks – gestione preventivi in PDF."""
    ctx.obj = {"verbose": verbose}
    if verbose:
        click.echo("[DEBUG] Verbose mode attivo.")


# ------------------------------------------------------------------
# COMANDO: GENERA
# ------------------------------------------------------------------
@cli.command()
@click.argument("cliente")
@click.option(
    "-d",
    "--dest",
    type=click.Path(dir_okay=False),
    default="output.pdf",
    help="File di destinazione PDF.",
)
@click.pass_context
def genera(ctx, cliente, dest):
    """Genera un preventivo PDF fittizio per CLIENTE."""
    verbose = ctx.obj["verbose"]
    if verbose:
        click.echo(f"[DEBUG] Inizio generazione PDF per: {cliente}")

    c = canvas.Canvas(dest)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, f"Preventivo per {cliente}")
    c.setFont("Helvetica", 12)
    c.drawString(72, 720, f"Data: {date.today().isoformat()}")
    c.drawString(72, 700, "Totale: € 0,00 (demo)")
    c.save()

    add_preventivo(
        {
            "cliente": cliente,
            "data": date.today().isoformat(),
            "file": str(Path(dest).resolve()),
        }
    )
    click.echo(f"Preventivo per '{cliente}' salvato in '{dest}'")


# ------------------------------------------------------------------
# COMANDO: IMPORTA
# ------------------------------------------------------------------
@cli.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--cliente", prompt="Cliente", help="Nome cliente")
@click.option(
    "--data", prompt="Data (YYYY-MM-DD)", default=date.today().isoformat()
)
def importa(file, cliente, data):
    """Importa un PDF esistente nell'archivio."""
    add_preventivo(
        {"cliente": cliente, "data": data, "file": str(Path(file).resolve())}
    )
    click.echo(f"Importato '{file}' per il cliente '{cliente}'.")


# ------------------------------------------------------------------
# COMANDO: LISTA
# ------------------------------------------------------------------
@cli.command()
@click.option("--cliente", help="Filtra per cliente")
def lista(cliente):
    """Elenca i preventivi archiviati."""
    rows = list_preventivi(cliente)
    if not rows:
        click.echo("Nessun preventivo trovato.")
        return

    click.echo(f"{'ID':<3} {'Data':<10} {'Cliente':<20} File")
    click.echo("-" * 60)
    for idx, rec in enumerate(rows, 1):
        click.echo(f"{idx:<3} {rec['data']:<10} {rec['cliente']:<20} {rec['file']}")
# ------------------------------------------------------------------
# COMANDO: CONFRONTA
# ------------------------------------------------------------------
@cli.command()
@click.argument("id1", type=int)
@click.argument("id2", type=int)
def confronta(id1, id2):
    """Confronta due preventivi per indice (come mostrato in `lista`)."""
    p1 = get_by_index(id1)
    p2 = get_by_index(id2)

    if not p1 or not p2:
        click.echo("Indici non validi.")
        return

    click.echo(f"Confronto ID {id1} vs ID {id2}")
    click.echo("-" * 40)

    keys = ["cliente", "data", "file"]
    for k in keys:
        v1, v2 = p1[k], p2[k]
        status = "✓" if v1 == v2 else "≠"
        click.echo(f"{k:<8}: {v1}  {status}  {v2}")
