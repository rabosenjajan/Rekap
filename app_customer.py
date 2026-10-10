"""Aplikasi Pemesanan Pre-Order (PO) Makanan Rumahan Premium - Tampilan Customer Mobile-First."""

import datetime
import streamlit as st
import pandas as pd
from src.database import get_menu_df, save_order, search_orders_by_customer
from src.styles import apply_custom_styles, format_rupiah, generate_whatsapp_invoice_url

# Page configuration
st.set_page_config(
    page_title="Pre-Order Menu Makanan Tradisional",
    page_icon="🍗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply Mobile Custom Styles
apply_custom_styles()

# Initialize session state for cart quantities
if "cart" not in st.session_state:
    st.session_state.cart = {}  # {id_menu: quantity}
if "submitted_order" not in st.session_state:
    st.session_state.submitted_order = None

# Header Brand Banner
st.markdown(
    """
    <div class="brand-header">
        <h1 class="brand-title">🍗 Dapur Tradisional Premium</h1>
        <p class="brand-subtitle">Rasa tradisional berkualitas premium • Pilihan tepat keluarga tercinta</p>
        <div class="branch-badge-container">
            <span class="branch-badge">📍 Asal: Malang (Sukun Pondok Indah)</span>
            <span class="branch-badge">📍 Asal: Tangerang (Islamic Village)</span>
            <span class="branch-badge">📦 Ekspedisi: Paxel / NCS / Bus</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Navigation Tabs
tab_order, tab_status = st.tabs(["🛍️ Pesan Menu (Katalog PO)", "🔍 Cek Status Pesanan"])

# ==========================================
# TAB 1: FORM PEMESANAN & KATALOG MENU
# ==========================================
with tab_order:
    # If order was just submitted, show invoice
    if st.session_state.submitted_order:
        order = st.session_state.submitted_order
        st.success("🎉 Pesanan Anda Berhasil Diterima!")
        
        wa_url = generate_whatsapp_invoice_url(
            order_id=order["order_id"],
            total_harga=order["total_harga"],
            nama_customer=order["nama_customer"]
        )

        st.markdown(
            f"""
            <div class="invoice-card">
                <div class="invoice-header">
                    <div style="font-size: 0.85rem; color: #78716c; text-transform: uppercase; font-weight: 700;">INVOICE PRE-ORDER</div>
                    <div class="invoice-id">{order["order_id"]}</div>
                    <div style="font-size: 0.8rem; color: #a8a29e;">{order["timestamp"]}</div>
                </div>
                
                <div style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 0.8rem;">
                    <b>👤 Pemesan:</b> {order["nama_customer"]} ({order["no_wa"]})<br>
                    <b>📍 Alamat Kirim:</b> {order["alamat_lengkap"]}<br>
                    <b>🏢 Asal Cabang:</b> {order["cabang_asal"]}<br>
                    <b>📅 Tgl Kirim PO:</b> {order["tanggal_kirim"]}<br>
                    <b>🚚 Ekspedisi:</b> {order["ekspedisi"]}<br>
                </div>

                <div style="background: #f8fafc; border-radius: 8px; padding: 0.8rem; font-size: 0.88rem; margin: 0.8rem 0;">
                    <b>📋 Rincian Pesanan:</b><br>
                    <pre style="white-space: pre-wrap; font-family: inherit; margin: 0.4rem 0 0 0; color: #334155;">{order["rincian_order_text"]}</pre>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 2px dashed #e2e8f0; padding-top: 0.8rem; margin-top: 0.8rem;">
                    <span style="font-size: 1.05rem; font-weight: 700; color: #1e293b;">Total Tagihan:</span>
                    <span style="font-size: 1.3rem; font-weight: 800; color: #b45309;">{format_rupiah(order["total_harga"])}</span>
                </div>

                <div class="bank-info-box">
                    <b style="color: #92400e;">💳 Instruksi Pembayaran:</b><br>
                    <div style="font-size: 0.85rem; color: #78350f; margin-top: 0.3rem;">
                        Silakan transfer sesuai total tagihan ke salah satu rekening berikut:<br>
                        • <b>BCA:</b> 123-456-7890 (a.n. Dapur Kuliner)<br>
                        • <b>Mandiri:</b> 142-00-1234567-8 (a.n. Dapur Kuliner)<br>
                        • <b>QRIS:</b> Minta via WhatsApp
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        # WhatsApp CTA button
        st.link_button(
            "📲 Kirim Bukti Transfer ke WhatsApp Penjual",
            wa_url,
            type="primary",
            use_container_width=True
        )

        if st.button("➕ Buat Pesanan Baru Lainnya", use_container_width=True):
            st.session_state.cart = {}
            st.session_state.submitted_order = None
            st.rerun()

    else:
        # Load Menu
        menu_df = get_menu_df()
        active_menu = menu_df[menu_df["is_active"] == True].copy()

        # Category Filter
        categories = ["Semua"] + sorted(list(active_menu["kategori"].unique()))
        selected_cat = st.selectbox("📂 Pilih Kategori Menu:", categories, index=0)

        if selected_cat != "Semua":
            display_menu = active_menu[active_menu["kategori"] == selected_cat]
        else:
            display_menu = active_menu

        st.markdown("### 📋 Pilih Menu Pesanan")
        
        # Display Menu Items with Quantity Counters
        for _, item in display_menu.iterrows():
            item_id = item["id_menu"]
            item_name = item["nama_item"]
            item_price = int(item["harga"])
            item_portion = item["porsi_varian"]
            item_desc = item.get("deskripsi", "")
            is_promo = bool(item.get("is_promo", False))
            current_qty = st.session_state.cart.get(item_id, 0)

            promo_html = '<span class="promo-pill">PROMO 🔥</span>' if is_promo else ''
            portion_html = f'<span class="portion-pill">📦 {item_portion}</span>' if item_portion else ''

            st.markdown(
                f"""
                <div class="menu-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div class="menu-title">{item_name} {promo_html}</div>
                            <div style="margin-bottom: 0.3rem;">{portion_html}</div>
                            <div class="menu-desc">{item_desc}</div>
                        </div>
                        <div class="menu-price">{format_rupiah(item_price)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Compact Quantity Input
            col_qty, col_space = st.columns([1, 1])
            with col_qty:
                qty = st.number_input(
                    f"Jumlah porsi ({item_name})",
                    min_value=0,
                    max_value=100,
                    value=current_qty,
                    step=1,
                    key=f"qty_{item_id}",
                    label_visibility="collapsed"
                )
                st.session_state.cart[item_id] = qty

        # Calculate Cart Totals
        total_items = 0
        total_price = 0
        order_lines = []

        for item_id, qty in st.session_state.cart.items():
            if qty > 0:
                match = menu_df[menu_df["id_menu"] == item_id]
                if not match.empty:
                    m = match.iloc[0]
                    subtotal = qty * int(m["harga"])
                    total_items += qty
                    total_price += subtotal
                    order_lines.append(f"• {m['nama_item']} ({m['porsi_varian']}) x {qty} = {format_rupiah(subtotal)}")

        st.markdown("---")
        st.markdown("### 🛒 Ringkasan Pilihan Anda")
        if total_items == 0:
            st.info("Pilih minimal 1 porsi menu di atas untuk melanjutkan pemesanan.")
        else:
            for line in order_lines:
                st.write(line)
            st.markdown(f"**Total Pesanan: {total_items} item — {format_rupiah(total_price)}**")

        st.markdown("---")
        st.markdown("### 📝 Lengkapi Data Pengiriman")
        with st.form("checkout_form"):
            nama_customer = st.text_input("Nama Lengkap:*", placeholder="Contoh: Ibu Rina / Bpk. Hendra")
            no_wa = st.text_input("Nomor WhatsApp (Aktif):*", placeholder="Contoh: 081234567890")
            alamat_lengkap = st.text_area("Alamat Lengkap Pengiriman:*", placeholder="Jl. Nama Jalan No. RT/RW, Kelurahan, Kecamatan, Kota/Kabupaten, Kode Pos")
            
            col_cabang, col_tgl = st.columns(2)
            with col_cabang:
                cabang_asal = st.selectbox(
                    "Cabang Asal Pengiriman:*",
                    ["Malang (Sukun Pondok Indah)", "Tangerang (Islamic Village)"]
                )
            with col_tgl:
                # Default PO date tomorrow
                min_date = datetime.date.today() + datetime.timedelta(days=1)
                tanggal_kirim = st.date_input(
                    "Tanggal Kirim PO yang Diinginkan:*",
                    value=min_date,
                    min_value=min_date
                )

            ekspedisi = st.selectbox(
                "Pilihan Ekspedisi Pengiriman:*",
                [
                    "Paxel (Cold Chain / Next Day Frozen)",
                    "NCS Courier",
                    "Bus / Travel Cargo (Bulk Order)",
                    "Kurir Instan / Ambil Sendiri"
                ]
            )

            catatan_khusus = st.text_area(
                "Catatan Khusus (Opsional):",
                placeholder="Contoh: Tidak terlalu pedas / Kirim sebelum jam 12 siang"
            )

            submit_btn = st.form_submit_button("🚀 Kirim Pesanan Sekarang", type="primary", use_container_width=True)

            if submit_btn:
                # Validations
                if total_items == 0:
                    st.error("⚠️ Silakan pilih minimal 1 item menu terlebih dahulu!")
                elif not nama_customer.strip():
                    st.error("⚠️ Mohon isi Nama Lengkap Anda.")
                elif not no_wa.strip() or len("".join(filter(str.isdigit, no_wa))) < 9:
                    st.error("⚠️ Mohon isi Nomor WhatsApp aktif yang valid.")
                elif not alamat_lengkap.strip():
                    st.error("⚠️ Mohon isi Alamat Lengkap Pengiriman.")
                else:
                    order_payload = {
                        "nama_customer": nama_customer,
                        "no_wa": no_wa,
                        "alamat_lengkap": alamat_lengkap,
                        "cabang_asal": cabang_asal,
                        "tanggal_kirim": str(tanggal_kirim),
                        "ekspedisi": ekspedisi,
                        "rincian_order_text": "\n".join(order_lines),
                        "total_harga": total_price,
                        "catatan_khusus": catatan_khusus
                    }

                    with st.spinner("Sedang memproses dan menyimpan pesanan Anda..."):
                        order_id = save_order(order_payload)
                        order_payload["order_id"] = order_id
                        order_payload["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.submitted_order = order_payload
                        st.rerun()

# ==========================================
# TAB 2: CEK STATUS PESANAN
# ==========================================
with tab_status:
    st.markdown("### 🔍 Cek Status Pesanan Anda")
    st.caption("Masukkan Nomor WhatsApp atau Nama Lengkap Anda saat memesan:")

    search_query = st.text_input("Nomor WA / Nama / Order ID:", placeholder="Contoh: 08123456789 atau Budi", key="status_search_input")

    if search_query:
        with st.spinner("Mencari data pesanan..."):
            matched_orders = search_orders_by_customer(search_query)

        if matched_orders.empty:
            st.warning("Belum ada pesanan yang cocok dengan pencarian tersebut. Pastikan nomor WA atau Nama sudah sesuai.")
        else:
            st.success(f"Ditemukan {len(matched_orders)} pesanan:")
            for _, ord_row in matched_orders.iterrows():
                oid = ord_row.get("order_id", "-")
                status = str(ord_row.get("status_order", "Menunggu Konfirmasi Bayar"))
                resi = str(ord_row.get("nomor_resi", "")).strip()
                tgl = ord_row.get("tanggal_kirim", "-")
                total = format_rupiah(ord_row.get("total_harga", 0))
                nama = ord_row.get("nama_customer", "-")
                eksp = ord_row.get("ekspedisi", "-")
                rincian = ord_row.get("rincian_order_text", "-")

                # Determine badge styling
                if "Selesai" in status or "Dikirim" in status:
                    badge_class = "badge-shipped"
                elif "Diproses" in status or "Terverifikasi" in status:
                    badge_class = "badge-process"
                else:
                    badge_class = "badge-pending"

                st.markdown(
                    f"""
                    <div style="background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 1rem; margin-bottom: 0.8rem; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-weight: 800; color: #b45309; font-size: 0.95rem;">{oid}</span>
                            <span class="{badge_class}">{status}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
                            👤 <b>Pemesan:</b> {nama}<br>
                            📅 <b>Tgl Kirim:</b> {tgl} | 🚚 <b>Ekspedisi:</b> {eksp}<br>
                            💰 <b>Total:</b> {total}<br>
                            📦 <b>No. Resi:</b> {resi if resi and resi != 'nan' else '<i>(Belum ada / Menunggu pengiriman)</i>'}<br>
                        </div>
                        <details style="margin-top: 0.5rem; font-size: 0.82rem; color: #64748b;">
                            <summary style="cursor: pointer; font-weight: 600;">Lihat Rincian Item</summary>
                            <pre style="white-space: pre-wrap; font-family: inherit; margin-top: 0.3rem;">{rincian}</pre>
                        </details>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
