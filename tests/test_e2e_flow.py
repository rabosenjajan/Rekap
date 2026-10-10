"""End-to-End integration test for complete PO lifecycle:
Customer orders -> App saves order -> Admin reviews & updates status -> Customer checks status.
"""

import pytest
import pandas as pd
from src.database import (
    get_menu_df,
    save_order,
    get_orders_df,
    update_order_status,
    search_orders_by_customer,
    add_or_update_menu_item,
    reset_local_db_for_test
)

@pytest.fixture(autouse=True)
def setup_clean_env(tmp_path, monkeypatch):
    test_dir = tmp_path / "e2e_data"
    test_dir.mkdir()
    monkeypatch.setenv("REKAP_DATA_DIR", str(test_dir))
    reset_local_db_for_test()

def test_full_po_lifecycle():
    # 1. Customer views menu catalog
    menu = get_menu_df()
    assert len(menu) >= 15
    ayam_kampung_item = menu[menu["id_menu"] == "AK-01"].iloc[0]
    assert ayam_kampung_item["harga"] == 45000

    # 2. Customer places order
    order_input = {
        "nama_customer": "Kak Aurel",
        "no_wa": "081299887766",
        "alamat_lengkap": "Komp. Sukun Indah Blok C No. 4 Malang",
        "cabang_asal": "Malang (Sukun Pondok Indah)",
        "tanggal_kirim": "2026-10-20",
        "ekspedisi": "Paxel (Cold Chain / Next Day Frozen)",
        "rincian_order_text": "• Ayam Kampung Ungkep (4 Potong) x 2 = Rp 90.000\n• Ayam Fillet Oseng Mercon (Base 250gr) x 1 = Rp 30.000",
        "total_harga": 120000,
        "catatan_khusus": "Tolong kirim sebelum jam 11 siang ya"
    }
    order_id = save_order(order_input)
    assert order_id.startswith("ORD-")

    # 3. Customer checks status immediately
    search_res = search_orders_by_customer("081299887766")
    assert len(search_res) == 1
    assert search_res.iloc[0]["status_order"] == "Menunggu Konfirmasi Bayar"
    assert search_res.iloc[0]["nomor_resi"] == ""

    # 4. Admin opens dashboard and views order
    all_orders = get_orders_df()
    assert len(all_orders) == 1
    assert all_orders.iloc[0]["total_harga"] == 120000

    # 5. Admin updates status to "Pembayaran Terverifikasi / Diproses"
    up1 = update_order_status(order_id, "Pembayaran Terverifikasi / Diproses")
    assert up1 is True

    # 6. Admin ships order and inputs tracking number (Resi)
    up2 = update_order_status(order_id, "Sedang Dikirim", nomor_resi="PAX-MLG-998822")
    assert up2 is True

    # 7. Customer checks status again using their Name
    search_by_name = search_orders_by_customer("aurel")
    assert len(search_by_name) == 1
    updated_order = search_by_name.iloc[0]
    assert updated_order["status_order"] == "Sedang Dikirim"
    assert updated_order["nomor_resi"] == "PAX-MLG-998822"
