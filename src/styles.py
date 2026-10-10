"""UI styling system, CSS injections, and helper formatters."""

import urllib.parse
import streamlit as st

def format_rupiah(amount: int) -> str:
    """Format integer amount to Indonesian Rupiah currency string."""
    try:
        val = int(amount)
        formatted = f"{val:,}".replace(",", ".")
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return "Rp 0"

def generate_whatsapp_invoice_url(order_id: str, total_harga: int, nama_customer: str, wa_penjual: str = "6282139721092") -> str:
    """Generate a direct WhatsApp click-to-chat link with prefilled order verification text."""
    total_str = format_rupiah(total_harga)
    message = (
        f"Halo Admin, saya ingin konfirmasi pembayaran untuk pesanan Pre-Order berikut:\n\n"
        f"📋 *Order ID:* {order_id}\n"
        f"👤 *Nama:* {nama_customer}\n"
        f"💰 *Total Bayar:* {total_str}\n\n"
        f"Berikut saya lampirkan bukti transfernya. Mohon segera diproses ya. Terima kasih! 🙏"
    )
    encoded = urllib.parse.quote(message)
    # Ensure phone number is clean
    clean_wa = "".join(filter(str.isdigit, wa_penjual))
    if clean_wa.startswith("0"):
        clean_wa = "62" + clean_wa[1:]
    return f"https://wa.me/{clean_wa}?text={encoded}"

def apply_custom_styles():
    """Inject premium warm appetizing CSS styles optimized for smartphones."""
    st.markdown(
        """
        <style>
        /* Mobile-First Custom Styles */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Container padding reduction on mobile */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            max-width: 650px !important;
            margin: 0 auto !important;
        }

        /* Brand Banner Header */
        .brand-header {
            background: linear-gradient(135deg, #78350f 0%, #b45309 50%, #d97706 100%);
            border-radius: 18px;
            padding: 1.2rem 1rem;
            color: #ffffff;
            text-align: center;
            box-shadow: 0 10px 25px -5px rgba(180, 83, 9, 0.3);
            margin-bottom: 1.2rem;
        }
        .brand-title {
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin: 0;
            color: #ffffff;
        }
        .brand-subtitle {
            font-size: 0.85rem;
            opacity: 0.95;
            margin-top: 0.3rem;
            font-weight: 500;
        }
        .branch-badge-container {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 0.6rem;
            flex-wrap: wrap;
        }
        .branch-badge {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 600;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        /* Menu Card Styling */
        .menu-card {
            background: #ffffff;
            border: 1px solid #fef3c7;
            border-radius: 14px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 2px 8px rgba(217, 119, 6, 0.08);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .menu-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(217, 119, 6, 0.15);
        }
        .menu-title {
            font-size: 1rem;
            font-weight: 700;
            color: #292524;
            margin-bottom: 0.2rem;
        }
        .menu-desc {
            font-size: 0.78rem;
            color: #78716c;
            line-height: 1.3;
            margin-bottom: 0.4rem;
        }
        .menu-price {
            font-size: 1.05rem;
            font-weight: 800;
            color: #b45309;
        }
        .promo-pill {
            background: #ef4444;
            color: white;
            padding: 0.15rem 0.45rem;
            border-radius: 12px;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
            margin-left: 0.3rem;
        }
        .portion-pill {
            background: #fef3c7;
            color: #92400e;
            padding: 0.15rem 0.45rem;
            border-radius: 12px;
            font-size: 0.68rem;
            font-weight: 600;
            display: inline-block;
        }

        /* Floating / Sticky Cart Summary Bar */
        .sticky-cart {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #ffffff;
            border-top: 2px solid #fef3c7;
            padding: 0.8rem 1.2rem;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
            z-index: 9999;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Invoice Box */
        .invoice-card {
            background: #ffffff;
            border: 2px dashed #d97706;
            border-radius: 16px;
            padding: 1.4rem;
            margin-top: 1rem;
            box-shadow: 0 4px 15px rgba(217, 119, 6, 0.1);
        }
        .invoice-header {
            text-align: center;
            border-bottom: 1px solid #f3f4f6;
            padding-bottom: 0.8rem;
            margin-bottom: 1rem;
        }
        .invoice-id {
            font-size: 1.1rem;
            font-weight: 800;
            color: #b45309;
            letter-spacing: 0.5px;
        }
        .bank-info-box {
            background: #fffbeb;
            border-radius: 10px;
            padding: 0.9rem;
            border-left: 4px solid #d97706;
            margin: 0.8rem 0;
        }

        /* Status Badges */
        .badge-pending {
            background-color: #fef3c7;
            color: #92400e;
            padding: 0.25rem 0.6rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.75rem;
        }
        .badge-process {
            background-color: #dbeafe;
            color: #1e40af;
            padding: 0.25rem 0.6rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.75rem;
        }
        .badge-shipped {
            background-color: #dcfce7;
            color: #166534;
            padding: 0.25rem 0.6rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.75rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
