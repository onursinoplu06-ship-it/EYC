import streamlit as st
import pandas as pd

# Sayfa Genişlik ve Başlık Ayarı
st.set_page_config(page_title="Enerjisa Üretim - Stok Kontrol", layout="wide")

# --- LOGO VE BAŞLIK ALANI ---
# Logo ekleme (Web üzerinden resmi logoyu çeker)
st.image("https://www.enerjisauretim.com.tr/assets/images/logo.png", width=200)

st.title("🏢 ENERJİSA ÜRETİM TEDARİK VE TİCARİ YÖNETİM STOK KONTROL SAYFASI")
st.markdown("---")

# Dosya Yükleme Alanı
uploaded_file = st.file_uploader("SAP ZMM012 Raporunu (Excel veya CSV) buraya yükleyin", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Veriyi oku
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Sütun İsimlerini Temizle (Gereksiz boşlukları siler)
        df.columns = df.columns.str.strip()

        # İhtiyacımız olan ana sütunlar
        columns_to_show = [
            "Üretim Yeri Tanim", 
            "Satınalma grubu", 
            "SA siparişi miktarı", 
            "SAS ölçü birimi", 
            "Kısa metin"
        ]
        
        # Dosyada mevcut olan sütunları bul
        existing_cols = [col for col in columns_to_show if col in df.columns]
        
        if not existing_cols:
            st.error("Dosyada beklenen sütunlar (Üretim Yeri Tanim vb.) bulunamadı!")
        else:
            # Sadece seçilen sütunları al
            display_df = df[existing_cols].copy()
            
            # Veri Temizleme: Boş üretim yerlerini 'Belirtilmemiş' yap
            if "Üretim Yeri Tanim" in display_df.columns:
                display_df["Üretim Yeri Tanim"] = display_df["Üretim Yeri Tanim"].fillna("Belirtilmemiş").astype(str)
            
            # --- FİLTRELEME (Kenar Çubuğu) ---
            st.sidebar.header("🔍 Filtreleme Paneli")
            
            if "Üretim Yeri Tanim" in display_df.columns:
                uretim_yerleri = sorted(display_df["Üretim Yeri Tanim"].unique())
                secilen_yerler = st.sidebar.multiselect("Üretim Yerlerini Seçin", uretim_yerleri, default=uretim_yerleri)
                
                # Tabloyu filtrele
                final_df = display_df[display_df["Üretim Yeri Tanim"].isin(secilen_yerler)]
                
                # --- ANA EKRAN GÖSTERİMİ ---
                st.subheader(f"📍 Filtrelenmiş Stok Verileri ({len(final_df)} Kayıt)")
                st.dataframe(final_df, use_container_width=True)
                
                # İndirme Butonu
                st.divider()
                csv_data = final_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Listeyi CSV Olarak İndir",
                    data=csv_data,
                    file_name="stok_kontrol_verisi.csv",
                    mime="text/csv"
                )
            else:
                st.dataframe(display_df, use_container_width=True)

    except Exception as e:
        st.error(f"Dosya işlenirken bir hata oluştu: {e}")
else:
    st.info("Lütfen işlem yapmak için bir SAP veri dosyası yükleyin.")

# Alt Bilgi
st.markdown("---")
st.caption("Enerjisa Üretim Tedarik ve Ticari Yönetim - Gelecek Nesil Raporlama v1.1")
