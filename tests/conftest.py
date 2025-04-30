import pytest
from reportlab.pdfgen import canvas
from datetime import date
from pathlib import Path

@pytest.fixture
def sample_pdf(tmp_path):
    """PDF di esempio con cliente, data e totale da parsare."""
    path = tmp_path / "sample.pdf"
    c = canvas.Canvas(str(path))
    c.drawString(72, 750, f"Preventivo per ACME S.p.A.")
    today = date.today().isoformat()
    c.drawString(72, 720, f"Data: {today}")
    c.drawString(72, 700, "Totale: € 123,45")
    c.save()
    return str(path)
