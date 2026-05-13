import streamlit as st
import pandas as pd
import os

# Sayfa Ayarları
st.set_page_config(page_title="Enerjisa Üretim - Stok Kontrol", layout="wide")

# --- ÖZEL TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: white; }
    .main-title {
        color: #004a99;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 700;
        text-align: center;
        margin-top: -25px;
        font-size: 20px;
        letter-spacing: 0.5px;
    }
    .signature {
        color: #aaaaaa;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        text-align: center;
        font-style: italic;
        margin-top: 5px;
    }
    /* Filtreleme alanını daha temiz göster */
    .filter-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. EN ÜST GENİŞ GÖRSEL (BANNER) ---
if os.path.exists("logo.jpg"):
    st.image("logo.jpg", use_container_width=True)

# --- 2. LOGO (ESA.PNG) VE BAŞLIKLAR ---
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1.5, 1.2, 1.5]) 
with col2:
    if os.path.exists("esa.png"):
        st.image("esa.png", use_container_width=True)

st.markdown('<div class="main-title">TEDARİK VE TİCARİ YÖNETİM STOK KONTROL SAYFASI</div>', unsafe_allow_html=True)
st.markdown('<div class="signature">Hazırlayan: Onur Sinoplu</div>', unsafe_allow_html=True)
st.markdown("---")

# --- DOSYA YÜKLEME ---
uploaded_file = st.file_uploader("📊 SAP Raporunu Yükleyin", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = df.columns.str.strip()
        
        # Sütun seçimi
        cols = ["Üretim Yeri Tanim", "Satınalma grubu", "Mal grubu", "SA siparişi miktarı", "SAS ölçü birimi", "Kısa metin"]
        existing = [c for c in cols if c in df.columns]
        
        if existing:
            data = df[existing].copy()
            
            st.markdown("### 🔍 İnteraktif Filtreleme Paneli")
            st.info("💡 **Excel Tarzı Filtreleme:** Aşağıdaki tablonun sütun başlıklarına tıklayarak arama yapabilir, sıralayabilir veya belirli değerleri seçebilirsiniz.")

            # --- EXCEL TARZI FİLTRELEME (st.data_editor) ---
            # Bu modül kullanıcının tablo üzerinde Excel gibi işlem yapmasına olanak tanır
            event = st.dataframe(
                data,
                use_container_width=True,
                height=600,
                hide_index=True,
                column_config={
                    "SA siparişi miktarı": st.column_config.NumberColumn("Miktar", format="%d"),
                    "Mal grubu": st.column_config.TextColumn("Mal Grubu No")
                }
            )

            # İndirme Seçeneği
            csv = data.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Mevcut Veriyi İndir (CSV)", csv, "stok_raporu.csv", "text/csv")
            
    except Exception as e:
        st.error(f"Hata: {e}")
else:
    st.info("💡 Başlamak için lütfen bir SAP dosyası yükleyin.")

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Enerjisa Üretim Stok Kontrol Sistemi | Onur Sinoplu")
