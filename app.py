import streamlit as st
import pandas as pd
import os

# Sayfa Ayarları
st.set_page_config(page_title="Enerjisa Üretim - Stok Kontrol", layout="wide")

# --- ÖZEL TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }
    .main-title {
        color: #004a99;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 700;
        text-align: center;
        margin-top: -25px; /* Logoya iyice yaklaştırır */
        font-size: 20px; /* Net ve küçük bir değer */
        letter-spacing: 0.5px;
        line-height: 1.2;
    }
    .signature {
        color: #aaaaaa;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        text-align: center;
        font-style: italic;
        margin-top: 5px;
    }
    .stMetric {
        border: 1px solid #004a99;
        border-radius: 8px;
        background-color: rgba(0, 74, 153, 0.01);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. EN ÜST GENİŞ GÖRSEL (BANNER) ---
if os.path.exists("logo.jpg"):
    st.image("logo.jpg", use_container_width=True)

# --- 2. LOGO (ESA.PNG) VE BAŞLIKLAR ---
st.markdown("<br>", unsafe_allow_html=True)

# Logo alanı
col1, col2, col3 = st.columns([1.5, 1.2, 1.5]) 
with col2:
    if os.path.exists("esa.png"):
        st.image("esa.png", use_container_width=True)
    else:
        st.warning("⚠️ esa.png bulunamadı.")

# BAŞLIK (h1 yerine doğrudan div/p kullanarak boyutu sabitledik)
st.markdown('<div class="main-title">TEDARİK VE TİCARİ YÖNETİM STOK KONTROL SAYFASI</div>', unsafe_allow_html=True)
st.markdown('<div class="signature">Hazırlayan: Onur Sinoplu</div>', unsafe_allow_html=True)
st.markdown("---")

# --- DOSYA YÜKLEME ---
uploaded_file = st.file_uploader("📊 SAP ZMM012 Raporunu Buraya Sürükleyin", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = df.columns.str.strip()
        
        # Sütunlar
        cols = ["Üretim Yeri Tanim", "Satınalma grubu", "Mal grubu", "SA siparişi miktarı", "SAS ölçü birimi", "Kısa metin"]
        existing = [c for c in cols if c in df.columns]
        
        if not existing:
            st.error("Gerekli sütunlar bulunamadı.")
        else:
            data = df[existing].copy()
            for c in ["Üretim Yeri Tanim", "Mal grubu"]:
                if c in data.columns:
                    data[c] = data[c].fillna("N/A").astype(str)

            # --- YAN MENÜ FİLTRELEME ---
            st.sidebar.header("🔍 Filtreleme Seçenekleri")
            all_sites = sorted(data["Üretim Yeri Tanim"].unique())
            all_groups = sorted(data["Mal grubu"].unique())
            
            sel_sites = st.sidebar.multiselect("📍 Üretim Yerleri", all_sites, default=all_sites)
            sel_groups = st.sidebar.multiselect("🔢 Mal Grubu Numaraları", all_groups, default=all_groups)

            # Filtreleme
            filtered = data[(data["Üretim Yeri Tanim"].isin(sel_sites)) & (data["Mal grubu"].isin(sel_groups))]

            # --- ANALİZ KARTLARI ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam Kalem", f"{len(filtered)} Adet")
            m2.metric("Seçili Üretim Yeri", len(sel_sites))
            if "SA siparişi miktarı" in filtered.columns:
                m3.metric("Toplam Sipariş Miktarı", f"{filtered['SA siparişi miktarı'].sum():,.0f}")

            # --- VERİ TABLOSU ---
            st.markdown("### 📋 Güncel Stok Listesi")
            st.dataframe(filtered, use_container_width=True, height=500)

            # İndirme Butonu
            st.sidebar.markdown("---")
            csv = filtered.to_csv(index=False).encode('utf-8-sig')
            st.sidebar.download_button("📥 Veriyi CSV Olarak İndir", csv, "stok_kontrol_raporu.csv", "text/csv")

    except Exception as e:
        st.error(f"Hata: {e}")
else:
    st.info("💡 Lütfen bir SAP dosyası yükleyerek analize başlayın.")

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Enerjisa Üretim Stok Kontrol Sistemi | Onur Sinoplu")
