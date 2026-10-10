"""Aplikasi Dashboard Penjual & Manajemen Pesanan Pre-Order (PO) - Admin Streamlit."""

import datetime
import streamlit as st
import pandas as pd
from src.database import (
    get_orders_df,
    update_order_status,
    get_menu_df,
    add_or_update_menu_item
)
from src.styles import apply_custom_styles, format_rupiah

# Page configuration
st.set_page_config(
    page_title="Dashboard Admin - Pre-Order Dapur Tradisional",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Styles
apply_custom_styles()

# Authentication & Session State Setup
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0

def check_admin_password(input_pw: str) -> bool:
    expected_pw = "admin123"
    if hasattr(st, "secrets") and "admin_password" in st.secrets:
        expected_pw = st.secrets["admin_password"]
    return input_pw.strip() == expected_pw

# ==========================================
# LOGIN GATE (KEAMANAN SEDERHANA)
# ==========================================
if not st.session_state.admin_authenticated:
    st.markdown(
        """
        <div style="max-width: 420px; margin: 3rem auto; padding: 2rem; background: white; border-radius: 16px; border: 1px solid #fef3c7; box-shadow: 0 10px 25px -5px rgba(217, 119, 6, 0.2); text-align: center;">
            <h2 style="color: #92400e; margin-bottom: 0.5rem;">🔒 Akses Admin Dapur</h2>
            <p style="color: #78716c; font-size: 0.88rem; margin-bottom: 1.5rem;">Silakan masukkan PIN / Password Admin untuk membuka dashboard pesanan.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        if st.session_state.login_attempts >= 5:
            st.error("⛔ Terlalu banyak percobaan gagal (Maksimal 5x). Sesi dikunci sementara.")
        else:
            with st.form("admin_login_form"):
                admin_pw = st.text_input("Password Admin:", type="password", placeholder="Masukkan password...")
                login_btn = st.form_submit_button("Masuk ke Dashboard", type="primary", use_container_width=True)

                if login_btn:
                    if check_admin_password(admin_pw):
                        st.session_state.admin_authenticated = True
                        st.session_state.login_attempts = 0
                        st.success("Login berhasil!")
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        remaining = 5 - st.session_state.login_attempts
                        st.error(f"Password salah! Sisa percobaan: {remaining}")
    st.stop()

# ==========================================
# DASHBOARD UTAMA SETELAH LOGIN
# ==========================================

# Top Navbar / Header
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.markdown("## 📊 Dashboard Penjual & Manajemen Pre-Order")
    st.caption("Kelola pesanan customer, rekap persiapan masak dapur, dan update status pengiriman realtime.")
with col_head2:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.admin_authenticated = False
        st.rerun()

# Load Data
orders_df = get_orders_df(force_reload=True)
menu_df = get_menu_df(force_reload=True)

# KPI Summary Cards
total_orders = len(orders_df)
total_revenue = orders_df["total_harga"].sum() if not orders_df.empty and "total_harga" in orders_df.columns else 0
pending_orders = len(orders_df[orders_df["status_order"] == "Menunggu Konfirmasi Bayar"]) if not orders_df.empty else 0
processed_orders = len(orders_df[orders_df["status_order"].str.contains("Diproses|Terverifikasi", na=False)]) if not orders_df.empty else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("📦 Total Pesanan", f"{total_orders} Order")
kpi2.metric("💰 Total Omset PO", format_rupiah(total_revenue))
kpi3.metric("⏳ Menunggu Konfirmasi", f"{pending_orders} Order")
kpi4.metric("🍳 Sedang Diproses", f"{processed_orders} Order")

st.markdown("---")

# Main Dashboard Tabs
tab_orders, tab_kitchen, tab_menu = st.tabs([
    "📦 Manajemen Pesanan & Resi",
    "🍳 Rekap Dapur (Kitchen Prep List)",
    "🍽️ Kelola Menu & Harga"
])

# ==========================================
# TAB 1: MANAJEMEN PESANAN & STATUS
# ==========================================
with tab_orders:
    st.subheader("📋 Daftar Seluruh Pesanan")

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        status_options = ["Semua"] + list(orders_df["status_order"].dropna().unique()) if not orders_df.empty else ["Semua"]
        filter_status = st.selectbox("Filter Status Pesanan:", status_options)
    with col_f2:
        cabang_options = ["Semua", "Malang (Sukun Pondok Indah)", "Tangerang (Islamic Village)"]
        filter_cabang = st.selectbox("Filter Asal Cabang:", cabang_options)
    with col_f3:
        search_kw = st.text_input("Cari Customer / WA / Order ID:", placeholder="Ketik kata kunci...")

    # Apply Filters
    filtered_df = orders_df.copy()
    if not filtered_df.empty:
        if filter_status != "Semua":
            filtered_df = filtered_df[filtered_df["status_order"] == filter_status]
        if filter_cabang != "Semua":
            filtered_df = filtered_df[filtered_df["cabang_asal"] == filter_cabang]
        if search_kw.strip():
            kw = search_kw.strip().lower()
            filtered_df = filtered_df[
                filtered_df["nama_customer"].astype(str).str.lower().str.contains(kw) |
                filtered_df["no_wa"].astype(str).str.contains(kw) |
                filtered_df["order_id"].astype(str).str.lower().str.contains(kw)
            ]

    if filtered_df.empty:
        st.info("Tidak ada data pesanan yang sesuai dengan filter.")
    else:
        # Display Table
        display_cols = ["order_id", "timestamp", "nama_customer", "no_wa", "tanggal_kirim", "cabang_asal", "ekspedisi", "total_harga", "status_order", "nomor_resi"]
        available_cols = [c for c in display_cols if c in filtered_df.columns]
        st.dataframe(filtered_df[available_cols], use_container_width=True, hide_index=True)

        st.markdown("### ⚡ Update Status & Resi Pesanan")
        col_up1, col_up2 = st.columns([1, 1])

        with col_up1:
            order_list = filtered_df["order_id"].tolist()
            selected_order_id = st.selectbox("Pilih Order ID:", order_list)
            
            selected_order = filtered_df[filtered_df["order_id"] == selected_order_id].iloc[0]
            current_status = selected_order.get("status_order", "Menunggu Konfirmasi Bayar")
            current_resi = str(selected_order.get("nomor_resi", ""))
            if current_resi == "nan":
                current_resi = ""

            status_choices = [
                "Menunggu Konfirmasi Bayar",
                "Pembayaran Terverifikasi / Diproses",
                "Sedang Dikirim",
                "Selesai",
                "Dibatalkan"
            ]
            current_idx = status_choices.index(current_status) if current_status in status_choices else 0
            new_status = st.selectbox("Ubah Status Pesanan:", status_choices, index=current_idx)
            new_resi = st.text_input("Nomor Resi Pengiriman:", value=current_resi, placeholder="Contoh: PAX-8812349")

            if st.button("💾 Simpan Perubahan Status", type="primary", use_container_width=True):
                success = update_order_status(selected_order_id, new_status, new_resi)
                if success:
                    st.success(f"Status pesanan {selected_order_id} berhasil diperbarui!")
                    st.rerun()
                else:
                    st.error("Gagal memperbarui status.")

        with col_up2:
            st.markdown(
                f"""
                <div style="background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 1.2rem;">
                    <h4 style="color: #92400e; margin-top: 0;">Detail Pesanan: {selected_order_id}</h4>
                    <p style="font-size: 0.88rem; line-height: 1.6; color: #334155;">
                        <b>👤 Nama:</b> {selected_order.get('nama_customer', '-')}<br>
                        <b>📱 WhatsApp:</b> {selected_order.get('no_wa', '-')}<br>
                        <b>📍 Alamat:</b> {selected_order.get('alamat_lengkap', '-')}<br>
                        <b>📅 Tgl Kirim:</b> {selected_order.get('tanggal_kirim', '-')}<br>
                        <b>🚚 Ekspedisi:</b> {selected_order.get('ekspedisi', '-')}<br>
                        <b>💰 Total:</b> {format_rupiah(selected_order.get('total_harga', 0))}<br>
                        <b>📝 Catatan:</b> {selected_order.get('catatan_khusus', '-') or '-'}<br>
                    </p>
                    <div style="background: #f8fafc; padding: 0.6rem; border-radius: 6px; font-size: 0.82rem;">
                        <b>Rincian Menu:</b>
                        <pre style="white-space: pre-wrap; font-family: inherit; margin: 0.2rem 0 0 0;">{selected_order.get('rincian_order_text', '-')}</pre>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Direct WhatsApp Chat button
            cust_wa = "".join(filter(str.isdigit, str(selected_order.get("no_wa", ""))))
            if cust_wa.startswith("0"):
                cust_wa = "62" + cust_wa[1:]
            if cust_wa:
                wa_chat_url = f"https://wa.me/{cust_wa}?text=Halo%20kak%20{selected_order.get('nama_customer','')}%2C%20kami%20dari%20Dapur%20Tradisional%20ingin%20menginformasikan%20pesanan%20PO%20{selected_order_id}..."
                st.link_button("💬 Hubungi Customer via WhatsApp", wa_chat_url, use_container_width=True)

# ==========================================
# TAB 2: REKAP DAPUR (KITCHEN PREP LIST)
# ==========================================
with tab_kitchen:
    st.subheader("🍳 Rekap Persiapan Dapur (Kitchen Prep List)")
    st.caption("Hitung otomatis akumulasi porsi/pack yang harus dimasak dan disiapkan berdasarkan tanggal kirim PO.")

    if orders_df.empty:
        st.info("Belum ada pesanan masuk.")
    else:
        available_dates = sorted(list(orders_df["tanggal_kirim"].dropna().unique()))
        selected_date = st.selectbox("Pilih Tanggal Pengiriman PO:", ["Semua Tanggal"] + available_dates)

        if selected_date != "Semua Tanggal":
            prep_orders = orders_df[orders_df["tanggal_kirim"] == selected_date]
        else:
            prep_orders = orders_df

        # Parse and aggregate item counts
        item_counts = {}
        for _, r in prep_orders.iterrows():
            text = str(r.get("rincian_order_text", ""))
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("•"):
                    # Format: • Ayam Kampung Ungkep (4 Potong) x 2 = Rp 90.000
                    try:
                        main_part = line[1:].split("=")[0].strip()
                        dish_part, qty_part = main_part.rsplit("x", 1)
                        dish_name = dish_part.strip()
                        qty_val = int(qty_part.strip())
                        item_counts[dish_name] = item_counts.get(dish_name, 0) + qty_val
                    except Exception:
                        pass

        if item_counts:
            prep_df = pd.DataFrame(list(item_counts.items()), columns=["Menu & Varian", "Total Porsi / Pack"])
            prep_df = prep_df.sort_values(by="Total Porsi / Pack", ascending=False)

            col_k1, col_k2 = st.columns([1, 1])
            with col_k1:
                st.markdown(f"**Daftar Masak ({len(prep_orders)} Pesanan):**")
                st.dataframe(prep_df, use_container_width=True, hide_index=True)
            with col_k2:
                st.bar_chart(prep_df.set_index("Menu & Varian"))
        else:
            st.info("Tidak ada item pesanan untuk tanggal ini.")

# ==========================================
# TAB 3: KELOLA MENU & HARGA
# ==========================================
with tab_menu:
    st.subheader("🍽️ Pengelolaan Master Menu & Harga")
    st.caption("Ubah harga, status ketersediaan (aktif/sold out), atau tambah menu baru.")

    st.dataframe(menu_df, use_container_width=True, hide_index=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("### ✏️ Edit Menu yang Sudah Ada")
        menu_items_list = menu_df["nama_item"].tolist()
        edit_target_name = st.selectbox("Pilih Menu:", menu_items_list)
        
        target_row = menu_df[menu_df["nama_item"] == edit_target_name].iloc[0]
        edit_price = st.number_input("Harga (Rp):", value=int(target_row["harga"]), step=1000)
        edit_active = st.checkbox("Status Tersedia (Aktif):", value=bool(target_row["is_active"]))
        edit_promo = st.checkbox("Status Promo 🔥:", value=bool(target_row.get("is_promo", False)))

        if st.button("💾 Simpan Perubahan Menu", type="primary"):
            updated_dict = target_row.to_dict()
            updated_dict["harga"] = int(edit_price)
            updated_dict["is_active"] = edit_active
            updated_dict["is_promo"] = edit_promo
            add_or_update_menu_item(updated_dict)
            st.success(f"Menu '{edit_target_name}' berhasil diperbarui!")
            st.rerun()

    with col_m2:
        st.markdown("### ➕ Tambah Menu Baru")
        with st.form("add_menu_form"):
            new_id = st.text_input("ID Menu (Unik):", placeholder="Contoh: FAV-04 / AK-07")
            new_cat = st.selectbox("Kategori:", ["Ayam Kampung", "Ayam Negri", "Ikan", "Daging Sapi", "Ayam Fillet", "Menu Favorit", "Lainnya"])
            new_name = st.text_input("Nama Hidangan:", placeholder="Contoh: Bebek Goreng Kremes")
            new_portion = st.text_input("Porsi / Varian:", placeholder="Contoh: 1 Ekor / 4 Potong / 250gr")
            new_price = st.number_input("Harga (Rp):", min_value=1000, value=35000, step=1000)
            new_desc = st.text_area("Deskripsi Singkat:", placeholder="Deskripsi bumbu dan kelezatan...")
            new_promo = st.checkbox("Tandai sebagai Promo 🔥")

            add_btn = st.form_submit_button("Tambah Menu Baru")
            if add_btn:
                if not new_id.strip() or not new_name.strip():
                    st.error("ID Menu dan Nama Hidangan wajib diisi.")
                else:
                    new_item_dict = {
                        "id_menu": new_id.strip(),
                        "kategori": new_cat,
                        "nama_item": new_name.strip(),
                        "porsi_varian": new_portion.strip(),
                        "harga": int(new_price),
                        "is_promo": new_promo,
                        "is_active": True,
                        "deskripsi": new_desc.strip()
                    }
                    add_or_update_menu_item(new_item_dict)
                    st.success(f"Menu '{new_name}' berhasil ditambahkan!")
                    st.rerun()
