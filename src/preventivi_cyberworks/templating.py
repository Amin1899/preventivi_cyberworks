from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
import json

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
BRAND_DIR = Path(__file__).resolve().parent.parent / "branding"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

def load_brand(name: str = "default") -> dict:
    brand_path = BRAND_DIR / name / "brand.json"
    if not brand_path.exists():
        raise FileNotFoundError(f"Brand '{name}' non trovato")
    with brand_path.open(encoding="utf-8") as f:
        brand = json.load(f)
        # path logo in absolute
        brand["logo"] = str((BRAND_DIR / name / Path(brand["logo"]).name).resolve())
        return brand

def render_pdf(out_path: str, context: dict, brand: str = "default"):
    tmpl = env.get_template("preventivo.html")
    context["brand"] = load_brand(brand)
    html_str = tmpl.render(**context)
    HTML(string=html_str, base_url=str(TEMPLATE_DIR)).write_pdf(out_path)
