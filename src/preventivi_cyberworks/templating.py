import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Percorsi base
PKG_DIR = Path(__file__).resolve().parent        # .../preventivi_cyberworks
TEMPLATE_DIR = PKG_DIR / "templates"             # .../preventivi_cyberworks/templates
BRAND_DIR    = PKG_DIR / "branding"              # .../preventivi_cyberworks/branding 

# Environment Jinja2 riutilizzabile
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

def create_simple_pdf(output_path, context: dict):
    """
    Crea un PDF minimale con ReportLab.
    Accetta Path o stringa come output_path.
    """
    # 🔧 1) normalizza a stringa
    output_path = str(output_path)

    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    width, height = A4

    # Se la cartella non esiste la creiamo (utile in /tmp di pytest)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
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
    Se WeasyPrint non è disponibile, crea un PDF semplice usando ReportLab.
    """
    # Import ritardato di WeasyPrint per evitare errori di libreria mancanti a import-time
    try:
        import sys
        from io import StringIO
        # Salva stdout originale
        old_stdout = sys.stdout
        # Reindirizza stdout a un buffer
        sys.stdout = StringIO()
        from weasyprint import HTML
        # Ripristina stdout
        sys.stdout = old_stdout
        use_weasyprint = True
    except (OSError, ImportError):
        # Ripristina stdout se necessario
        if 'old_stdout' in locals():
            sys.stdout = old_stdout
        use_weasyprint = False

    # Prepara context per il template
    merged_context = {} if context is None else context.copy()
    merged_context.update(extra_context)

    if use_weasyprint:
        try:
            # Renderizza template
            template = env.get_template(template_name)
            html_str = template.render(**merged_context)
            # Genera il PDF
            HTML(string=html_str).write_pdf(output_path)
        except Exception as e:
            # Se WeasyPrint fallisce, usa il fallback
            create_simple_pdf(output_path, merged_context)
    else:
        # Fallback: crea un PDF semplice
        create_simple_pdf(output_path, merged_context)
