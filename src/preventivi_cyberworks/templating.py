import os
import sys
import json
from io import StringIO
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import cm

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
    """Crea un PDF professionale usando ReportLab come fallback."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Carica il brand
    brand = load_brand(context.get('brand', 'default'))
    primary_color = colors.HexColor(brand.get('primary', '#000000'))
    
    # Crea il documento
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Stili
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        textColor=primary_color,
        spaceAfter=30
    ))
    
    # Elementi del documento
    elements = []
    
    # Logo
    if 'logo' in brand:
        img = Image(brand['logo'], width=200, height=100)
        elements.append(img)
        elements.append(Spacer(1, 20))
    
    # Titolo
    elements.append(Paragraph("PREVENTIVO", styles['CustomTitle']))
    
    # Dati cliente
    data = [
        ["Cliente:", context.get('cliente', 'N/A')],
        ["Data:", context.get('data', datetime.now().strftime('%d/%m/%Y'))],
        ["Totale:", f"€ {context.get('totale', '0,00')}"]
    ]
    
    # Crea tabella
    table = Table(data, colWidths=[100, 300])
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Footer
    elements.append(Paragraph(
        "Documento generato automaticamente",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            textColor=colors.gray,
            alignment=1,
            fontSize=8
        )
    ))
    
    # Genera il PDF
    doc.build(elements)

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
