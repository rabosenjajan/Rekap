# Pre-Order (PO) Food Ordering System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a mobile-first Pre-Order (PO) food ordering web application for customers and an admin dashboard for sellers, connected to Google Sheets (with local fallback) and styled with Streamlit.

**Architecture:** Dual Streamlit applications (`app_customer.py` and `app_admin.py`) sharing a unified data layer (`src/database.py`) and UI styling system (`src/styles.py`), supporting Google Sheets via `st-gsheets-connection` and automatic local offline/demo storage.

**Tech Stack:** Python 3.10+, Streamlit, Pandas, `st-gsheets-connection`, Pytest.

## Global Constraints

- Python-based Streamlit application runnable locally via `streamlit run <app_file>.py`.
- Two distinct entrypoints: `app_customer.py` (Customer PO & Status Tracker) and `app_admin.py` (Admin Dashboard).
- Data model contains exact dishes and prices extracted from the flyer images.
- Mobile-first responsive UI with custom CSS.
- Zero external database lock-in: supports Google Sheets when configured in `.streamlit/secrets.toml` and automatically falls back to local CSV storage if credentials are not present.

---

### Task 1: Project Setup and Initial Menu Dataset

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/seed_data.py`
- Create: `.streamlit/config.toml`
- Create: `.streamlit/secrets.toml.example`
- Test: `tests/test_seed_data.py`

**Interfaces:**
- Produces: `src.seed_data.INITIAL_MENU_ITEMS` (list of dicts containing full menu catalog from both flyers).

- [x] **Step 1: Create requirements.txt and Streamlit config**
- [x] **Step 2: Write the failing test for seed menu data**
- [x] **Step 3: Run test to verify it fails**
- [x] **Step 4: Implement `src/seed_data.py` with menu catalog from images**
- [x] **Step 5: Run test to verify it passes**
- [x] **Step 6: Commit**

---

### Task 2: Data Access Layer with Google Sheets & Local Fallback

**Files:**
- Create: `src/database.py`
- Test: `tests/test_database.py`

**Interfaces:**
- Consumes: `src.seed_data.INITIAL_MENU_ITEMS`
- Produces:
  - `get_menu_df() -> pd.DataFrame`
  - `save_order(order_data: dict) -> str` (returns `order_id`)
  - `get_orders_df() -> pd.DataFrame`
  - `update_order_status(order_id: str, new_status: str, nomor_resi: str = "") -> bool`
  - `search_orders_by_customer(query: str) -> pd.DataFrame`
  - `add_or_update_menu_item(menu_item: dict) -> bool`

- [x] **Step 1: Write tests for database functions**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `src/database.py`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit**

---

### Task 3: Mobile-First Styling and UI Components

**Files:**
- Create: `src/styles.py`
- Test: `tests/test_styles.py`

**Interfaces:**
- Produces:
  - `apply_custom_styles()` (injects custom CSS for mobile responsiveness, warm color scheme, badge pills, sticky bottom cart summary, touch buttons)
  - `format_rupiah(amount: int | float) -> str`
  - `generate_whatsapp_invoice_url(order_id: str, total_harga: int, nama_customer: str, wa_penjual: str = "6282139721092") -> str`

- [x] **Step 1: Write tests for helper functions in styles**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `src/styles.py`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit**

---

### Task 4: Customer Pre-Order Web Application (`app_customer.py`)

**Files:**
- Create: `app_customer.py`

**Features:**
- Header with brand title and branch locations (Malang & Tangerang).
- 2 Main Tabs:
  1. 🛍️ **Pesan Menu (Katalog PO)**
  2. 🔍 **Cek Status Pesanan**
- Category filter buttons/tabs (Ayam Kampung, Ayam Negri, Ikan, Daging Sapi, Ayam Fillet, Menu Favorit).
- Touch-friendly +/- quantity stepper per menu item.
- Realtime Sticky Cart Summary bar showing total selected items and total Rp.
- Customer Form: Nama, No WA (phone validator), Alamat Lengkap, Cabang Asal Dropdown, Tanggal Kirim Datepicker, Ekspedisi Dropdown, Catatan Khusus.
- Submit validation: minimum 1 item selected, required fields filled.
- Instant Invoice view after submit with bank transfer instructions and large green CTA: "Kirim Bukti Transfer ke WhatsApp".
- Self-serve Order Status Tracker: customer inputs WA / Name, views all their orders with colored status badge and tracking numbers.

- [x] **Step 1: Implement `app_customer.py`**
- [x] **Step 2: Validate syntax and run in headless test mode**
- [x] **Step 3: Commit**

---

### Task 5: Admin Dashboard Web Application (`app_admin.py`)

**Files:**
- Create: `app_admin.py`

**Features:**
- Password / PIN Gate with brute-force attempt limiter in `st.session_state`.
- Tab 1: **Manajemen Pesanan & Status**
  - KPI Metrics: Total Pesanan Masuk, Total Omset PO, Pesanan Menunggu Konfirmasi, Pesanan Diproses.
  - Interactive Filter: Status, Cabang, Tanggal Kirim.
  - Quick Status Update form (Change status to *Menunggu Konfirmasi*, *Pembayaran Terverifikasi / Diproses*, *Sedang Dikirim*, *Selesai*, *Dibatalkan* + Input Nomor Resi).
  - Direct WhatsApp customer link button.
- Tab 2: **Rekap Dapur (Kitchen Prep Summary)**
  - Filter by Tanggal Kirim PO.
  - Aggregated table & bar chart of total quantities per dish to prepare/cook.
- Tab 3: **Kelola Menu & Harga**
  - Add new menu item form.
  - Toggle active/inactive status (sold out / coming soon).
  - Quick edit price.

- [x] **Step 1: Implement `app_admin.py`**
- [x] **Step 2: Validate syntax and verify features**
- [x] **Step 3: Commit**

---

### Task 6: End-to-End Integration Testing & Documentation

**Files:**
- Create: `tests/test_e2e_flow.py`
- Create: `README.md`

- [x] **Step 1: Write and run end-to-end integration test**
- [x] **Step 2: Create comprehensive README.md with deployment guide for Streamlit Community Cloud and Google Sheets setup**
- [x] **Step 3: Run all pytest suites to ensure 100% pass rate**
- [x] **Step 4: Commit**
