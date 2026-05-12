import streamlit as st
import pandas as pd

# Sayfa Başlığı
st.set_page_config(page_title="SAP Veri Analiz Portalı", layout="wide")
st.title("📊 Satın Alma Veri İşleme Paneli")

# Dosya Yükleme Alanı
uploaded_file = st.file_uploader("SAP'den aldığın Excel dosyasını seç", type=['xlsx', 'csv'])

if uploaded_file:
    # Veriyi Oku (CSV veya XLSX durumuna göre)
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # İhtiyacımız olan sütunları seçelim (Senin istediğin liste)
    columns_to_show = [
        "Üretim Yeri Tanim", 
        "Satınalma grubu", 
        "SA siparişi miktarı", 
        "SAS ölçü birimi", 
        "Kısa metin"
    ]
    
    # Sütunların varlığını kontrol et ve filtrele
    existing_cols = [col for col in columns_to_show if col in df.columns]
    filtered_df = df[existing_cols]

    # --- FİLTRELEME ALANI ---
    st.sidebar.header("Filtreleme Seçenekleri")
    
    if "Üretim Yeri Tanim" in filtered_df.columns:
        uretim_yerleri = filtered_df["Üretim Yeri Tanim"].unique()
        secilen_yer = st.sidebar.multiselect("Üretim Yeri Seçin", uretim_yerleri, default=uretim_yerleri)
        
        # Seçime göre tabloyu güncelle
        final_df = filtered_df[filtered_df["Üretim Yeri Tanim"].isin(secilen_yer)]
        
        st.subheader(f"📍 Seçilen Üretim Yerleri: {', '.join(secilen_yer)}")
        st.dataframe(final_df, use_container_width=True)
        
        # İndirme Butonu
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("İşlenmiş Veriyi İndir", csv, "islenmis_sap_verisi.csv", "text/csv")
    else:
        st.error("Dosyada 'Üretim Yeri Tanim' sütunu bulunamadı!")
