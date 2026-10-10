import os
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
def setup_test_db(tmp_path, monkeypatch):
    test_data_dir = tmp_path / "data"
    test_data_dir.mkdir()
    monkeypatch.setenv("REKAP_DATA_DIR", str(test_data_dir))
    reset_local_db_for_test()

def test_get_menu_df():
    df = get_menu_df()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "id_menu" in df.columns
    assert "harga" in df.columns
    assert len(df) >= 15

def test_save_and_retrieve_order():
    order_data = {
        "nama_customer": "Budi Santoso",
        "no_wa": "08123456789",
        "alamat_lengkap": "Jl. Mawar No. 10 Malang",
        "cabang_asal": "Malang (Sukun Pondok Indah)",
        "tanggal_kirim": "2026-10-15",
        "ekspedisi": "Paxel",
        "rincian_order_text": "Ungkep 4 Potong x 2 (Rp 90.000)",
        "total_harga": 90000,
        "catatan_khusus": "Jangan terlalu pedas"
    }
    order_id = save_order(order_data)
    assert order_id.startswith("ORD-")

    orders_df = get_orders_df()
    assert len(orders_df) == 1
    assert orders_df.iloc[0]["order_id"] == order_id
    assert orders_df.iloc[0]["status_order"] == "Menunggu Konfirmasi Bayar"

def test_update_order_status():
    order_id = save_order({
        "nama_customer": "Siti Aminah",
        "no_wa": "08987654321",
        "alamat_lengkap": "Tangerang",
        "cabang_asal": "Tangerang (Islamic Village)",
        "tanggal_kirim": "2026-10-16",
        "ekspedisi": "NCS",
        "rincian_order_text": "Fillet Oseng Mercon x 1",
        "total_harga": 30000,
        "catatan_khusus": ""
    })
    success = update_order_status(order_id, "Pembayaran Terverifikasi / Diproses", nomor_resi="PAX-123456")
    assert success is True

    orders_df = get_orders_df()
    row = orders_df[orders_df["order_id"] == order_id].iloc[0]
    assert row["status_order"] == "Pembayaran Terverifikasi / Diproses"
    assert row["nomor_resi"] == "PAX-123456"

def test_search_orders_by_customer():
    save_order({
        "nama_customer": "Dewi Sartika",
        "no_wa": "081122334455",
        "alamat_lengkap": "Malang",
        "cabang_asal": "Malang (Sukun Pondok Indah)",
        "tanggal_kirim": "2026-10-18",
        "ekspedisi": "Paxel",
        "rincian_order_text": "Garang Asem x 2",
        "total_harga": 70000,
        "catatan_khusus": ""
    })
    res_wa = search_orders_by_customer("081122334455")
    assert len(res_wa) == 1
    assert res_wa.iloc[0]["nama_customer"] == "Dewi Sartika"

    res_nama = search_orders_by_customer("dewi")
    assert len(res_nama) == 1

def test_add_or_update_menu_item():
    new_item = {
        "id_menu": "CUSTOM-01",
        "kategori": "Menu Favorit",
        "nama_item": "Ayam Bakar Madu Spesial",
        "porsi_varian": "1 Ekor",
        "harga": 80000,
        "is_promo": True,
        "is_active": True,
        "deskripsi": "Ayam bakar madu gurih manis."
    }
    assert add_or_update_menu_item(new_item) is True
    df = get_menu_df()
    row = df[df["id_menu"] == "CUSTOM-01"]
    assert not row.empty
    assert row.iloc[0]["harga"] == 80000
