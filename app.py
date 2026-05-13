import streamlit as st
import pandas as pd
import os

# Sayfa Ayarları
st.set_page_config(page_title="Enerjisa Üretim - Stok Kontrol", layout="wide")

# --- TASARIM VE ÜST GÖRSEL (CSS) ---
st.markdown("""
    <style>
    /* Sayfa genel arka planı beyaz */
    .stApp {
        background-color: white;
    }
    
    /* Üstteki görselin (Banner) ayarları */
    .banner-container {
        width: 100%;
        height: auto;
        overflow: hidden;
        margin-top: -60px; /* Streamlit'in varsayılan boşluğunu kapatır */
    }
    
    .banner-img {
        width: 100%;
        max-height: 400px; /* Görselin çok devasa olmaması için sınır */
        object-fit: cover; /* Görseli kesmeden/bozmadan sığdırır */
    }

    /* Başlık ve Metin Renkleri */
    h1, h2, h3 {
        color: #004a99 !important;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stMetric {
        border: 1px solid #004a99;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ÜST GÖRSEL (BANNER) ---
if os.path.exists("logo.jpg"):
    st.image("logo.jpg", use_container_width=True)
else:
    st.warning("⚠️ logo.jpg dosyası bulunamadı. Lütfen ana dizine yükleyin.")

# --- BAŞLIK ALANI ---
st.markdown("<br>", unsafe_allow_html=True) # Küçük bir boşluk
st.title("ENERJİSA ÜRETİM")
st.subheader("TEDARİK VE TİCARİ YÖNETİM STOK KONTROL SAYFASI")
st.markdown("---")

# --- DOSYA YÜKLEME ---
uploaded_file = st.file_uploader("📊 SAP ZMM012 Raporunu Buraya Yükleyin", type=['xlsx', 'csv'])

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
            m1.metric("Kalem Sayısı", f"{len(filtered)} Adet")
            m2.metric("Seçili Üretim Yeri", len(sel_sites))
            if "SA siparişi miktarı" in filtered.columns:
                m3.metric("Toplam Sipariş Miktarı", f"{filtered['SA siparişi miktarı'].sum():,.0f}")

            # --- VERİ TABLOSU ---
            st.markdown("### 📋 Stok Listesi")
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
st.caption("Enerjisa Üretim Stok Kontrol Sistemi v2.2")
