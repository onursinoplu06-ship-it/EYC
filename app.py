import streamlit as st
import pandas as pd

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="SAP Veri Analiz Portalı", layout="wide")

# Başlık ve Açıklama
st.title("📊 Satın Alma Veri İşleme Paneli")
st.markdown("""
    SAP'den aldığınız **ZMM012** raporunu buraya yükleyerek; Üretim Yeri bazlı filtreleme yapabilir ve 
    istediğiniz sütunları yan yana görebilirsiniz.
""")

# Dosya Yükleme Alanı
uploaded_file = st.file_uploader("Excel veya CSV dosyasını sürükleyin", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Veriyi oku
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # 1. Sütun İsimlerini Temizle (Gereksiz boşlukları siler)
        df.columns = df.columns.str.strip()

        # 2. İhtiyacımız olan ana sütunlar
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
            st.error("Yüklenen dosyada beklenen sütun başlıkları bulunamadı. Lütfen sütun isimlerini kontrol edin.")
        else:
            # Sadece seçilen sütunlarla yeni bir tablo oluştur
            display_df = df[existing_cols].copy()

            # --- FİLTRELEME ALANI (Sol Panel) ---
            st.sidebar.header("🔍 Filtreleme Menüsü")
            
            if "Üretim Yeri Tanim" in display_df.columns:
                # Üretim yeri listesini temizle ve benzersizleri al
                display_df["Üretim Yeri Tanim"] = display_df["Üretim Yeri Tanim"].fillna("Tanımsız").astype(str)
                uretim_yerleri = sorted(display_df["Üretim Yeri Tanim"].unique())
                
                secilen_yer = st.sidebar.multiselect(
                    "Üretim Yeri Seçin", 
                    options=uretim_yerleri, 
                    default=uretim_yerleri
                )
                
                # Tabloyu filtrele
                final_df = display_df[display_df["Üretim Yeri Tanim"].isin(secilen_yer)]
                
                # --- ANA EKRAN GÖSTERİMİ ---
                # Hata aldığın başlık kısmını güvenli hale getirdik (map(str, ...))
                yer_metni = ", ".join(map(str, secilen_yer))
                st.subheader(f"📍 Filtrelenen Üretim Yerleri")
                st.info(f"Görüntülenen: {yer_metni[:200]}..." if len(yer_metni) > 200 else f"Görüntülenen: {yer_metni}")
                
                # Veri Tablosu
                st.dataframe(final_df, use_container_width=True)
                
                # İndirme Butonu (İşlenmiş Veri)
                st.divider()
                csv_data = final_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 İşlenmiş Tabloyu CSV Olarak İndir",
                    data=csv_data,
                    file_name="islenmis_sap_verisi.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Dosyada 'Üretim Yeri Tanim' sütunu bulunamadı, tabloyu ham haliyle gösteriyorum.")
                st.dataframe(display_df, use_container_width=True)

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
else:
    st.info("Lütfen işlem yapmak için bir SAP dışa aktarım dosyası yükleyin.")

# Alt Bilgi
st.caption("Enerjisa Üretim - Otomasyon Projesi v1.0")
