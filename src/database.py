"""Database access layer with Google Sheets connection & resilient local storage fallback."""

import os
import uuid
import datetime
import pandas as pd
from typing import List, Dict, Any, Optional
from src.seed_data import INITIAL_MENU_ITEMS

# Local storage configuration
def _get_data_dir() -> str:
    data_dir = os.environ.get("REKAP_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def _get_menu_csv_path() -> str:
    return os.path.join(_get_data_dir(), "menu.csv")

def _get_orders_csv_path() -> str:
    return os.path.join(_get_data_dir(), "orders.csv")

def reset_local_db_for_test():
    """Reset local database for automated test suites."""
    menu_path = _get_menu_csv_path()
    orders_path = _get_orders_csv_path()
    if os.path.exists(menu_path):
        os.remove(menu_path)
    if os.path.exists(orders_path):
        os.remove(orders_path)

def _init_local_menu_if_needed():
    path = _get_menu_csv_path()
    if not os.path.exists(path):
        df = pd.DataFrame(INITIAL_MENU_ITEMS)
        df.to_csv(path, index=False)

def _init_local_orders_if_needed():
    path = _get_orders_csv_path()
    if not os.path.exists(path):
        columns = [
            "order_id", "timestamp", "nama_customer", "no_wa",
            "alamat_lengkap", "cabang_asal", "tanggal_kirim", "ekspedisi",
            "rincian_order_text", "total_harga", "catatan_khusus",
            "status_order", "nomor_resi"
        ]
        df = pd.DataFrame(columns=columns)
        df["nomor_resi"] = df["nomor_resi"].astype(str)
        df.to_csv(path, index=False)

# --- Data Access Functions ---

def get_menu_df(force_reload: bool = False) -> pd.DataFrame:
    """Retrieve active menu catalog. Supports Google Sheets with automatic local CSV fallback."""
    # Attempt Google Sheets if configured
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            from streamlit_gsheets import GSheetsConnection
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(worksheet="DB_Menu", ttl=0 if force_reload else 300)
            if df is not None and not df.empty:
                return df
    except Exception:
        pass

    # Local fallback
    _init_local_menu_if_needed()
    df = pd.read_csv(_get_menu_csv_path())
    # Ensure types
    df["harga"] = pd.to_numeric(df["harga"], errors="coerce").fillna(0).astype(int)
    df["is_active"] = df["is_active"].astype(bool)
    df["is_promo"] = df["is_promo"].astype(bool)
    return df

def save_order(order_data: dict) -> str:
    """Save customer order and return generated order_id."""
    now = datetime.datetime.now()
    order_id = f"ORD-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}"

    record = {
        "order_id": str(order_id),
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "nama_customer": str(order_data.get("nama_customer", "")).strip(),
        "no_wa": str(order_data.get("no_wa", "")).strip(),
        "alamat_lengkap": str(order_data.get("alamat_lengkap", "")).strip(),
        "cabang_asal": str(order_data.get("cabang_asal", "")).strip(),
        "tanggal_kirim": str(order_data.get("tanggal_kirim", "")).strip(),
        "ekspedisi": str(order_data.get("ekspedisi", "")).strip(),
        "rincian_order_text": str(order_data.get("rincian_order_text", "")).strip(),
        "total_harga": int(order_data.get("total_harga", 0)),
        "catatan_khusus": str(order_data.get("catatan_khusus", "")).strip(),
        "status_order": "Menunggu Konfirmasi Bayar",
        "nomor_resi": ""
    }

    # Attempt Google Sheets write if configured
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            from streamlit_gsheets import GSheetsConnection
            conn = st.connection("gsheets", type=GSheetsConnection)
            existing_df = conn.read(worksheet="DB_Pesanan")
            updated_df = pd.concat([existing_df, pd.DataFrame([record])], ignore_index=True)
            conn.update(worksheet="DB_Pesanan", data=updated_df)
            return order_id
    except Exception:
        pass

    # Local fallback
    _init_local_orders_if_needed()
    path = _get_orders_csv_path()
    df = pd.read_csv(path, dtype=str)
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(path, index=False)
    return order_id

def get_orders_df(force_reload: bool = False) -> pd.DataFrame:
    """Retrieve all orders dataframe."""
    # Attempt Google Sheets if configured
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            from streamlit_gsheets import GSheetsConnection
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(worksheet="DB_Pesanan", ttl=0 if force_reload else 60)
            if df is not None and not df.empty:
                return df
    except Exception:
        pass

    # Local fallback
    _init_local_orders_if_needed()
    df = pd.read_csv(_get_orders_csv_path(), dtype=str)
    if "total_harga" in df.columns:
        df["total_harga"] = pd.to_numeric(df["total_harga"], errors="coerce").fillna(0).astype(int)
    return df

def update_order_status(order_id: str, new_status: str, nomor_resi: str = "") -> bool:
    """Update order status and optional tracking number."""
    # Attempt Google Sheets if configured
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            from streamlit_gsheets import GSheetsConnection
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(worksheet="DB_Pesanan")
            if df is not None and not df.empty:
                idx = df[df["order_id"] == order_id].index
                if len(idx) > 0:
                    df.loc[idx, "status_order"] = new_status
                    if nomor_resi:
                        df.loc[idx, "nomor_resi"] = str(nomor_resi)
                    conn.update(worksheet="DB_Pesanan", data=df)
                    return True
    except Exception:
        pass

    # Local fallback
    _init_local_orders_if_needed()
    path = _get_orders_csv_path()
    df = pd.read_csv(path, dtype=str)
    idx = df[df["order_id"] == order_id].index
    if len(idx) > 0:
        df.loc[idx, "status_order"] = new_status
        if nomor_resi:
            df.loc[idx, "nomor_resi"] = str(nomor_resi)
        df.to_csv(path, index=False)
        return True
    return False

def search_orders_by_customer(query: str) -> pd.DataFrame:
    """Search orders matching WhatsApp number or full customer name (case-insensitive)."""
    df = get_orders_df()
    if df.empty or not query.strip():
        return pd.DataFrame(columns=df.columns if not df.empty else [])

    q = query.strip().lower()
    q_digits = "".join(filter(str.isdigit, q))

    def matches(row):
        name_match = q in str(row.get("nama_customer", "")).lower()
        row_phone = "".join(filter(str.isdigit, str(row.get("no_wa", ""))))
        phone_match = bool(q_digits and (q_digits in row_phone or row_phone in q_digits))
        order_id_match = q in str(row.get("order_id", "")).lower()
        return name_match or phone_match or order_id_match

    matched_mask = df.apply(matches, axis=1)
    return df[matched_mask].copy()

def add_or_update_menu_item(menu_item: dict) -> bool:
    """Add a new dish or update existing menu item."""
    _init_local_menu_if_needed()
    path = _get_menu_csv_path()
    df = pd.read_csv(path)

    id_menu = menu_item.get("id_menu")
    if id_menu in df["id_menu"].values:
        for key, val in menu_item.items():
            if key in df.columns:
                df.loc[df["id_menu"] == id_menu, key] = val
    else:
        df = pd.concat([df, pd.DataFrame([menu_item])], ignore_index=True)

    df.to_csv(path, index=False)
    return True
