import urllib.parse
from src.styles import format_rupiah, generate_whatsapp_invoice_url

def test_format_rupiah():
    assert format_rupiah(45000) == "Rp 45.000"
    assert format_rupiah(0) == "Rp 0"
    assert format_rupiah(1250000) == "Rp 1.250.000"

def test_generate_whatsapp_invoice_url():
    url = generate_whatsapp_invoice_url("ORD-20261010-001", 90000, "Budi Santoso")
    assert "https://wa.me/6282139721092" in url
    assert "ORD-20261010-001" in url
    assert "Budi" in url
    # Verify proper URL encoding
    assert " " not in url
