import click
from .core import generate_preventivo

@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Abilita output dettagliato (verbose)")
@click.pass_context
def cli(ctx, verbose: bool):
    """
    CLI per Preventivi Cyberworks.
    """
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    if verbose:
        click.echo("[DEBUG] Verbose mode attivo.")

@cli.command()
@click.argument("cliente", required=True)
@click.option("-d", "--dest", default="output.pdf", show_default=True,
              help="Percorso file di output del preventivo")
@click.pass_context
def genera(ctx, cliente: str, dest: str):
    """
    Genera un preventivo per il CLIENTE e lo salva in DEST.
    """
    # Chiama la logica di generazione del PDF
    generate_preventivo(cliente, dest, verbose=ctx.obj.get("VERBOSE", False))
    # Messaggio di conferma
    click.echo(f"Preventivo per '{cliente}' salvato in '{dest}'")

if __name__ == "__main__":
    cli()
