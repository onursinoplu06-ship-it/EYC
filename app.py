import streamlit as st
import pandas as pd
import os

# Sayfa Ayarları
st.set_page_config(page_title="Enerjisa Üretim - Stok Kontrol", layout="wide")

# Logo ve Başlık Alanı
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=150)
    else:
        st.write("🏢") # Logo bulunamazsa bir bina ikonu gösterir

with col2:
    st.title("ENERJİSA ÜRETİM")
    st.subheader("STOK KONTROL VE ANALİZ SAYFASI")

st.markdown("---")

# Dosya Yükleme
uploaded_file = st.file_uploader("📊 SAP ZMM012 Raporunu Yükleyin (Excel veya CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Veri okuma
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Sütun isimlerini temizle
        df.columns = df.columns.str.strip()
        
        # Gösterilecek sütunlar (Mal grubu eklendi)
        cols = ["Üretim Yeri Tanim", "Satınalma grubu", "Mal grubu", "SA siparişi miktarı", "SAS ölçü birimi", "Kısa metin"]
        existing = [c for c in cols if c in df.columns]
        
        if not existing:
            st.error("Gerekli sütunlar (Üretim Yeri Tanim, Mal grubu vb.) bulunamadı.")
        else:
            data = df[existing].copy()
            # Veri ön hazırlığı
            for c in ["Üretim Yeri Tanim", "Mal grubu"]:
                if c in data.columns:
                    data[c] = data[c].fillna("N/A").astype(str)

            # --- YAN MENÜ FİLTRELEME ---
            st.sidebar.header("🔍 Filtreleme Paneli")
            
            # Üretim Yeri Filtresi
            sites = sorted(data["Üretim Yeri Tanim"].unique())
            sel_sites = st.sidebar.multiselect("📍 Üretim Yerleri", sites, default=sites)
            
            # Mal Grubu Filtresi (Senin script'te kullandığın kodlar)
            groups = sorted(data["Mal grubu"].unique())
            sel_groups = st.sidebar.multiselect("🔢 Mal Grubu Numaraları", groups, default=groups)

            # Filtreleme İşlemi
            filtered = data[(data["Üretim Yeri Tanim"].isin(sel_sites)) & (data["Mal grubu"].isin(sel_groups))]

            # --- ANALİZ METRİKLERİ ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Kalem", f"{len(filtered)} Adet")
            c2.metric("Seçili Üretim Yeri", len(sel_sites))
            if "SA siparişi miktarı" in filtered.columns:
                c3.metric("Toplam Sipariş Miktarı", f"{filtered['SA siparişi miktarı'].sum():,.0f}")

            # --- VERİ TABLOSU ---
            st.markdown("### 📋 Güncel Liste")
            st.dataframe(filtered, use_container_width=True, height=500)

            # --- DIŞA AKTARMA ---
            st.sidebar.markdown("---")
            csv = filtered.to_csv(index=False).encode('utf-8-sig')
            st.sidebar.download_button("📥 Filtrelenmiş Listeyi İndir", csv, "stok_kontrol_raporu.csv", "text/csv")

    except Exception as e:
        st.error(f"Dosya işlenirken hata oluştu: {e}")
else:
    st.info("💡 Başlamak için lütfen bir SAP veri dosyası yükleyin.")

st.markdown("---")
st.caption("Enerjisa Üretim Tedarik ve Ticari Yönetim | v2.0")
