import os
import pytest
from preventivi_cyberworks.pdf_utils import parse_preventivo_pdf
from datetime import date

def test_parse_preventivo_pdf(sample_pdf):
    meta = parse_preventivo_pdf(sample_pdf)
    assert meta["cliente"] == "ACME S.p.A."
    assert meta["data"] == date.today().isoformat()
    assert meta["totale"] == "123,45"
