import sys
import json
from io import StringIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# 1) Percorsi base dentro il package
PKG_DIR = Path(__file__).resolve().parent                  # .../preventivi_cyberworks
TEMPLATE_DIR = PKG_DIR / "templates"                        # .../preventivi_cyberworks/templates
BRAND_DIR    = PKG_DIR / "branding"                         # .../preventivi_cyberworks/branding

# 2) Jinja2 environment
env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

def load_brand(name: str = "default") -> dict:
    """
    Carica i dati di branding da src/preventivi_cyberworks/branding/{name}/brand.json
    Restituisce un dict con almeno la chiave 'logo' puntata al file assoluto.
    """
    brand_path = BRAND_DIR / name / "brand.json"
    if not brand_path.exists():
        raise FileNotFoundError(f"Brand '{name}' non trovato in {brand_path}")
    data = json.loads(brand_path.read_text(encoding="utf-8"))
    logo_file = brand_path.parent / Path(data.get("logo", "")).name
    data["logo"] = str(logo_file.resolve())
    return data

def create_simple_pdf(output: str | Path, context: dict):
    """
    Fallback minimale con ReportLab: stampa cliente, data e totale.
    """
    output = Path(output)
    c = canvas.Canvas(str(output), pagesize=A4)
    w, h = A4
    c.setFont("Helvetica", 12)
    c.drawString(50, h - 50, f"Cliente: {context.get('cliente', 'N/A')}")
    c.drawString(50, h - 70, f"Data: {context.get('data', 'N/A')}")
    c.drawString(50, h - 90, f"Totale: € {context.get('totale', '0,00')}")
    c.save()

def render_pdf(
    template_name: str,
    context: dict = None,
    output_path: str | Path = None,
    **extra_context
):
    """
    Renderizza un PDF da un template HTML Jinja2 con WeasyPrint.
    Se WeasyPrint non c’è o fallisce, ricorre a ReportLab.
    """
    # ——— Validazione e preparazione output_path ———
    if not output_path:
        raise ValueError("render_pdf: serve un percorso di output")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_str = str(output_path)

    # ——— Import dinamico WeasyPrint (silenzia stdout) ———
    try:
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        from weasyprint import HTML
        sys.stdout = old_stdout
        have_weasy = True
    except Exception:
        if 'old_stdout' in locals():
            sys.stdout = old_stdout
        have_weasy = False

    # ——— Prepara contesto ———
    merged = {} if context is None else dict(context)
    merged.update(extra_context)

    # ——— Se WeasyPrint disponibile, prova a generare ———
    if have_weasy:
        try:
            tmpl = env.get_template(template_name)
            html = tmpl.render(**merged)
            HTML(string=html).write_pdf(output_str)
            return
        except Exception:
            # fallback silenzioso
            create_simple_pdf(output_str, merged)
            return

    # ——— Fallback ReportLab quando WeasyPrint assente ———
    create_simple_pdf(output_str, merged)
