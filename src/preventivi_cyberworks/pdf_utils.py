"""
Estrazione di cliente, data e totale da un PDF di preventivo.
Si assume che il PDF contenga linee tipo:
  Preventivo per <cliente>
  Data: YYYY-MM-DD
  Totale: € N,NN
"""

from pdfminer.high_level import extract_text
import re
from datetime import datetime

_PATTERNS = {
    "cliente": re.compile(r"Preventivo per\s+(.+)", re.IGNORECASE),
    "data":    re.compile(r"Data:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})"),
    "totale":  re.compile(r"Totale:\s*€\s*([0-9]+\,[0-9]{2})"),
}


def parse_preventivo_pdf(path: str) -> dict:
    """Estrae i metadati dal PDF indicato."""
    text = extract_text(path)
    result = {}
    # Cliente
    m = _PATTERNS["cliente"].search(text)
    result["cliente"] = m.group(1).strip() if m else ""
    # Data
    m = _PATTERNS["data"].search(text)
    result["data"] = m.group(1) if m else datetime.today().date().isoformat()
    # Totale
    m = _PATTERNS["totale"].search(text)
    result["totale"] = m.group(1) if m else "0,00"
    return result
