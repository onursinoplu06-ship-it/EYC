import streamlit as st
import pandas as pd
import os
import base64

# Sayfa Ayarları
st.set_page_config(page_title="Enerjisa Üretim - Stok Kontrol", layout="wide")

# --- ARKA PLAN LOGO VE TASARIM (JPG DESTEKLİ) ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# logo.jpg dosyasını arka plana gömme
if os.path.exists("logo.jpg"):
    bin_str = get_base64_of_bin_file("logo.jpg")
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bin_str}");
        background-size: 800px; /* Logo boyutu */
        background-repeat: no-repeat;
        background-position: center; /* Sayfanın tam ortası */
        background-attachment: fixed;
    }}
    
    /* Sayfayı karartmadan logoyu şeffaflaştıran katman */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(255, 255, 255, 0.94); /* 0.94 logonun çok silik durmasını sağlar */
        z-index: -1;
    }}

    /* Yazı ve Tablo okunabilirliği için ekstra gölge ve renk ayarı */
    h1, h2, h3 {{
        color: #004a99 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }}
    
    .stMetric {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px;
        border: 1px solid #004a99;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
else:
    st.sidebar.warning("⚠️ logo.jpg bulunamadı, lütfen repo'ya yükleyin.")

# --- BAŞLIK ALANI ---
st.title("🏢 ENERJİSA ÜRETİM")
st.subheader("TEDARİK VE TİCARİ YÖNETİM STOK KONTROL SAYFASI")
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
        
        # Sütunlar (Mal grubu dahil)
        cols = ["Üretim Yeri Tanim", "Satınalma grubu", "Mal grubu", "SA siparişi miktarı", "SAS ölçü birimi", "Kısa metin"]
        existing = [c for c in cols if c in df.columns]
        
        if not existing:
            st.error("Gerekli sütunlar bulunamadı. Lütfen SAP raporunu kontrol edin.")
        else:
            data = df[existing].copy()
            for c in ["Üretim Yeri Tanim", "Mal grubu"]:
                if c in data.columns:
                    data[c] = data[c].fillna("N/A").astype(str)

            # --- YAN MENÜ FİLTRELEME ---
            st.sidebar.header("🔍 Filtreleme Seçenekleri")
            
            # Alfabetik sıralı ve temiz listeler
            all_sites = sorted(data["Üretim Yeri Tanim"].unique())
            all_groups = sorted(data["Mal grubu"].unique())
            
            sel_sites = st.sidebar.multiselect("📍 Üretim Yerleri", all_sites, default=all_sites)
            sel_groups = st.sidebar.multiselect("🔢 Mal Grubu Numaraları", all_groups, default=all_groups)

            # Filtreleme
            filtered = data[(data["Üretim Yeri Tanim"].isin(sel_sites)) & (data["Mal grubu"].isin(sel_groups))]

            # --- ANALİZ KARTLARI ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Kalem Sayısı", f"{len(filtered)} Adet")
            m2.metric("Seçili Üretim Yeri", len(sel_sites))
            if "SA siparişi miktarı" in filtered.columns:
                m3.metric("Toplam Sipariş Miktarı", f"{filtered['SA siparişi miktarı'].sum():,.0f}")

            # --- VERİ TABLOSU ---
            st.markdown("### 📋 Güncel Stok Listesi")
            st.dataframe(filtered, use_container_width=True, height=500)

            # İndirme Butonu
            st.sidebar.markdown("---")
            csv = filtered.to_csv(index=False).encode('utf-8-sig')
            st.sidebar.download_button("📥 İşlenmiş Veriyi İndir", csv, "stok_kontrol_raporu.csv", "text/csv")

    except Exception as e:
        st.error(f"Dosya işlenirken hata oluştu: {e}")
else:
    st.info("💡 Analize başlamak için lütfen bir SAP veri dosyası (Excel/CSV) yükleyin.")

st.caption("Enerjisa Üretim Stok Kontrol Sistemi v2.1 | Arka plan: logo.jpg")
