# 🍗 Sistem Pre-Order (PO) Makanan Tradisional Premium

Aplikasi Pre-Order (PO) makanan rumahan berkualitas premium berbasis **Python & Streamlit**, dirancang khusus untuk kenyamanan layar smartphone customer (*Mobile-First*) dan kemudahan operasional penjual (*Admin Dashboard*).

---

## 🌟 Fitur Utama

### 📱 1. Aplikasi Customer (`app_customer.py`)
- **Mobile-First & Touch-Friendly:** Desain hangat, responsif, dan ringan dibuka di browser HP.
- **Katalog Menu Lengkap:** Ayam Kampung, Ayam Negri, Ikan (Lele/Patin), Daging Sapi (Empal Gepuk), Ayam Fillet Promo, dan Menu Favorit (Pepes, Ayam Pop, Garang Asem).
- **Keranjang & Counter Interaktif:** Stepper `+` / `-` yang cepat untuk memilih jumlah porsi per menu.
- **Form Checkout Cepat:** Pilihan asal cabang (*Malang* / *Tangerang*), Datepicker tanggal PO, opsi ekspedisi (*Paxel*, *NCS*, *Bus*), dan catatan pesanan.
- **Invoice Otomatis & CTA WhatsApp:** Menampilkan total tagihan, rekening transfer, dan tombol sekali-klik untuk kirim bukti bayar ke WhatsApp penjual.
- **Cek Status Pesanan Mandiri:** Customer dapat mengecek status pesanan & nomor resi pengiriman cukup dengan memasukkan No. WhatsApp atau Nama.

### 📊 2. Dashboard Penjual / Admin (`app_admin.py`)
- **Login Keamanan PIN/Password:** Proteksi akses admin dengan pembatas percobaan gagal (anti-brute force).
- **Manajemen Pesanan Realtime:** Filter status (*Menunggu Konfirmasi*, *Diproses*, *Dikirim*, *Selesai*), cabang asal, dan tanggal kirim.
- **Quick Update Status & Resi:** Update status dan input nomor resi langsung tersimpan.
- **Rekap Dapur (Kitchen Prep List):** Agregasi otomatis total porsi/pack per masakan berdasarkan tanggal PO untuk memudahkan belanja & masak.
- **Kelola Menu & Harga:** Tambah menu baru, edit harga, atau aktifkan/nonaktifkan menu *sold out*.

---

## 🚀 Cara Menjalankan Aplikasi di Komputer Lokal

1. **Clone repository & masuk ke direktori:**
   ```bash
   git clone <repo-url>
   cd Rekap
   ```

2. **Install dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Aplikasi Customer:**
   ```bash
   streamlit run app_customer.py
   ```
   *(Buka di browser: `http://localhost:8501`)*

4. **Jalankan Dashboard Admin (di tab/port terpisah):**
   ```bash
   streamlit run app_admin.py --server.port 8502
   ```
   *(Buka di browser: `http://localhost:8502` — Password default: `admin123`)*

---

## ☁️ Panduan Deploy ke Streamlit Community Cloud (2 Subdomain Terpisah)

Anda dapat membuat 2 aplikasi terpisah di **[share.streamlit.io](https://share.streamlit.io)** dari repositori GitHub yang sama:

### App 1: Aplikasi Customer (Contoh URL: `pesan-dapur.streamlit.app`)
- **Repository:** `username/Rekap`
- **Branch:** `main`
- **Main file path:** `app_customer.py`
- **App URL:** `pesan-dapur` (atau nama pilihan Anda)

### App 2: Dashboard Penjual (Contoh URL: `admin-dapur.streamlit.app`)
- **Repository:** `username/Rekap`
- **Branch:** `main`
- **Main file path:** `app_admin.py`
- **App URL:** `admin-dapur` (atau nama pilihan Anda)
- **Secrets:** Masukkan password admin di menu *Settings > Secrets*:
  ```toml
  admin_password = "password_rahasia_anda_disini"
  ```

---

## 📊 Integrasi Google Sheets (Opsional)

Secara default, aplikasi telah memiliki **Local Storage Fallback** (data otomatis tersimpan di file CSV lokal). Jika ingin menghubungkan langsung ke Google Sheets live:
1. Buat Service Account di Google Cloud Console dan berikan akses Editor ke Spreadsheet Anda.
2. Tambahkan konfigurasi di `.streamlit/secrets.toml` sesuai contoh di `.streamlit/secrets.toml.example`.

---

## 🧪 Menjalankan Pengujian Otomatis (Testing)

Jalankan seluruh rangkaian test unit & end-to-end:
```bash
pytest -v
```
