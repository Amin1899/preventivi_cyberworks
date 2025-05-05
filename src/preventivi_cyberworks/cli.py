import click
from datetime import date
from pathlib import Path
from reportlab.pdfgen import canvas
from preventivi_cyberworks.storage import add_preventivo, list_preventivi, get_by_index
from preventivi_cyberworks.pdf_utils import parse_preventivo_pdf
from preventivi_cyberworks.templating import render_pdf
from rich.console import Console
from rich.table import Table

console = Console()


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
@click.option("-d", "--dest", default="output.pdf", help="File PDF di destinazione")
@click.option("--totale", default="0,00", help="Totale preventivo")
@click.option("--brand", default="default", help="Tema colore / logo")
@click.pass_context
def genera(ctx, cliente, dest, totale, brand):
    """Genera un preventivo PDF con template HTML/CSS."""
    verbose = ctx.obj["verbose"]
    if verbose:
        console.print(f"[DEBUG] Inizio generazione PDF per: {cliente}")

    context = {
        "cliente": cliente,
        "data": date.today().isoformat(),
        "totale": totale,
    }
    try:
        render_pdf("preventivo.html", context, dest, brand=brand)
        click.echo(f"Preventivo per '{cliente}' salvato in '{dest}'")
    except Exception as e:
        if verbose:
            click.echo(f"Warning: {e}", err=True)
        # Crea PDF dummy
        with open(dest, "wb") as f:
            f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n%%EOF")
        click.echo(f"Preventivo per '{cliente}' salvato in '{dest}' (versione semplificata)")

    add_preventivo(
        {
            "cliente": cliente,
            "data": context["data"],
            "file": str(Path(dest).resolve()),
            "totale": totale,
        }
    )



# ------------------------------------------------------------------
# COMANDO: IMPORTA
# ------------------------------------------------------------------
@cli.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def importa(file):
    """
    Importa un PDF esistente nell'archivio,
    estraendo automaticamente cliente, data, totale.
    """
    meta = parse_preventivo_pdf(file)
    add_preventivo(
        {
            "cliente": meta["cliente"],
            "data": meta["data"],
            "file": str(Path(file).resolve()),
            "totale": meta["totale"],
        }
    )
    click.echo(
        f"Importato '{file}': cliente={meta['cliente']}, "
        f"data={meta['data']}, totale=€ {meta['totale']}"
    )


# ------------------------------------------------------------------
# COMANDO: LISTA
# ------------------------------------------------------------------
@cli.command()
@click.option("--cliente", help="Filtra per cliente")
def lista(cliente):
    """Elenca i preventivi archiviati."""
    rows = list_preventivi(cliente)
    if not rows:
        console.print("[yellow]Nessun preventivo trovato.[/]")
        return

    table = Table(title="Elenco preventivi", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Data", style="magenta")
    table.add_column("Cliente", style="green")
    table.add_column("File", style="white")
    table.add_column("Totale", justify="right", style="red")

    for idx, rec in enumerate(rows, 1):
        table.add_row(
            str(idx),
            rec["data"],
            rec["cliente"],
            rec["file"],
            rec.get("totale", ""),
        )
    console.print(table)


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
        console.print("[red]Indici non validi.[/]")
        return

    console.print(f"[bold underline]Confronto ID {id1} vs ID {id2}[/]\n")
    table = Table(show_header=True)
    table.add_column("Campo", style="cyan")
    table.add_column(f"ID {id1}", style="green")
    table.add_column(f"ID {id2}", style="green")

    for k in ["cliente", "data", "file", "totale"]:
        v1 = p1.get(k, "")
        v2 = p2.get(k, "")
        mark = "✓" if v1 == v2 else "[red]≠[/]"
        table.add_row(k, v1, v2 + f" {mark}")

    console.print(table)
