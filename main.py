import sys
import click

def configure_logging(verbose: bool):
    """
    Configura la log verbosity.
    """
    # TODO: implementare logging avanzato in futuro
    if verbose:
        click.echo("[DEBUG] Verbose mode attivo.")

@click.command()
@click.option("-v", "--verbose", is_flag=True, help="Abilita output dettagliato (verbose)")
def main(verbose: bool):
    """
    Punto di ingresso dell'applicazione Preventivi Cyberworks.
    --verbose: attiva il logging dettagliato
    """
    configure_logging(verbose)
    click.echo("Preventivi Cyberworks avviato.")

if __name__ == "__main__":
    main()
