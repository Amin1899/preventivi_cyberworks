import os
import sys
import json
from io import StringIO
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Percorsi base
PKG_DIR      = Path(__file__).resolve().parent               # .../preventivi_cyberworks
TEMPLATE_DIR = PKG_DIR.parent.parent / "templates"           # .../src/templates
BRAND_DIR    = PKG_DIR.parent.parent / "branding"            # .../src/branding

# Environment Jinja2
env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

def load_brand(name: str = "default") -> dict:
    brand_path = BRAND_DIR / name / "brand.json"
    if not brand_path.exists():
        raise FileNotFoundError(f"Brand '{name}' non trovato in {brand_path}")
    with brand_path.open(encoding="utf-8") as f:
        brand = json.load(f)
    # Risolvi percorso logo
    logo_name     = Path(brand.get("logo", "")).name
    brand["logo"] = str((BRAND_DIR / name / logo_name).resolve())
    return brand

def create_simple_pdf(output_path: str | Path, context: dict):
    """Fallback ReportLab."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 50, f"Cliente: {context.get('cliente', 'N/A')}")
    c.drawString(50, height - 70, f"Data: {context.get('data', 'N/A')}")
    c.drawString(50, height - 90, f"Totale: € {context.get('totale', '0,00')}")
    c.save()

def render_pdf(
    template_name: str,
    context: dict = None,
    output_path: str | Path = None,
    **extra_context
):
    """
    Renderizza da Jinja2+WeasyPrint, con fallback ReportLab.
    """

    # 1) Validazione output_path
    if output_path is None:
        raise ValueError("render_pdf: serve un percorso di output")
    output_path = Path(output_path)
    # 1b) Creo le directory padre se mancano
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_str = str(output_path)

    # 2) Import dinamico di WeasyPrint
    try:
        old_stdout  = sys.stdout
        sys.stdout  = StringIO()
        from weasyprint import HTML
        sys.stdout  = old_stdout
        use_weasy   = True
    except (OSError, ImportError):
        # Ripristino stdout
        if 'old_stdout' in locals():
            sys.stdout = old_stdout
        use_weasy = False

    # 3) Preparo il contesto
    merged = {} if context is None else context.copy()
    merged.update(extra_context)

    # 4) Provo con WeasyPrint
    if use_weasy:
        try:
            template = env.get_template(template_name)
            html_str = template.render(**merged)
            HTML(string=html_str).write_pdf(output_str)
            return
        except Exception:
            # su errore, caduta su ReportLab
            create_simple_pdf(output_str, merged)
            return

    # 5) Fallback puro ReportLab
    create_simple_pdf(output_str, merged)
