import sys
from io import StringIO
import os
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Percorsi base
PKG_DIR      = Path(__file__).resolve().parent                           # .../src/preventivi_cyberworks
TEMPLATE_DIR = PKG_DIR / "templates"                                       # .../src/preventivi_cyberworks/templates
BRAND_DIR    = PKG_DIR / "branding"                                        # .../src/preventivi_cyberworks/branding

# Environment Jinja2
env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

def load_brand(name: str = "default") -> dict:
    """
    Carica i dati di branding da branding/{name}/brand.json
    Restituisce un dict con almeno la chiave 'logo' contenente il percorso assoluto del logo.
    """
    brand_path = BRAND_DIR / name / "brand.json"
    if not brand_path.exists():
        raise FileNotFoundError(f"Brand '{name}' non trovato in {brand_path}")
    with brand_path.open(encoding="utf-8") as f:
        brand = json.load(f)
    # Risolvi percorso logo in assoluto
    logo_name = Path(brand.get("logo", "")).name
    brand["logo"] = str((BRAND_DIR / name / logo_name).resolve())
    return brand

def create_simple_pdf(output_path: str, context: dict):
    """Crea un PDF semplice usando ReportLab come fallback."""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 50, f"Cliente: {context.get('cliente', 'N/A')}")
    c.drawString(50, height - 70, f"Data: {context.get('data', 'N/A')}")
    c.drawString(50, height - 90, f"Totale: € {context.get('totale', '0,00')}")
    c.save()

def render_pdf(
    template_name: str,
    context: dict = None,
    output_path: str = None,
    **extra_context
):
    """
    Renderizza un PDF da un template HTML Jinja2 usando WeasyPrint.
    Se WeasyPrint non è disponibile o fallisce, ricorre a ReportLab.
    """
    # 1) Controlla che ci sia un percorso di output
    if output_path is None:
        raise ValueError("render_pdf: serve un percorso di output")
    output_path = Path(output_path)
    # crea le directory padre se non esistono
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_str = str(output_path)

    # 2) Import dinamico di WeasyPrint (silenzia stdout)
    try:
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        from weasyprint import HTML
        sys.stdout = old_stdout
        use_weasy = True
    except (OSError, ImportError):
        if 'old_stdout' in locals():
            sys.stdout = old_stdout
        use_weasy = False

    # 3) Prepara il contesto
    merged = {} if context is None else context.copy()
    merged.update(extra_context)

    # 4) Se WeasyPrint c’è, prova a generare
    if use_weasy:
        try:
            template = env.get_template(template_name)
            html_str = template.render(**merged)
            HTML(string=html_str).write_pdf(output_str)
            return
        except Exception:
            # fallback su ReportLab se qualcosa va storto
            create_simple_pdf(output_str, merged)
            return

    # 5) Se non c’è WeasyPrint, usa ReportLab
    create_simple_pdf(output_str, merged)
