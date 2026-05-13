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
    }
    .signature {
        color: #aaaaaa;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        text-align: center;
        font-style: italic;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GÖRSELLER VE BAŞLIK ---
if os.path.exists("logo.jpg"):
    st.image("logo.jpg", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1.5, 1.2, 1.5]) 
with col2:
    if os.path.exists("esa.png"):
        st.image("esa.png", use_container_width=True)

st.markdown('<div class="main-title">TEDARİK VE TİCARİ YÖNETİM STOK KONTROL SAYFASI</div>', unsafe_allow_html=True)
st.markdown('<div class="signature">Hazırlayan: Onur Sinoplu</div>', unsafe_allow_html=True)
st.markdown("---")

uploaded_file = st.file_uploader("📊 SAP ZMM012 Raporunu Yükleyin", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = df.columns.str.strip()
        cols_to_show = ["Üretim Yeri Tanim", "Satınalma grubu", "Mal grubu", "SA siparişi miktarı", "SAS ölçü birimi", "Kısa metin"]
        existing = [c for c in cols_to_show if c in df.columns]
        
        if existing:
            data = df[existing].copy()
            for c in data.columns:
                data[c] = data[c].fillna("N/A")

            # --- YENİ AKILLI FİLTRELEME PANELİ ---
            st.markdown("### 🔍 Akıllı Filtreleme")
            
            # Kullanıcıya seçim kolaylığı sağlayan anahtar
            filtre_modu = st.radio(
                "Çalışma Modu Seçin:",
                ["Tüm Verileri Göster", "Sadece Seçtiklerimi Göster"],
                horizontal=True,
                help="Sadece 1-2 grup seçecekseniz 'Sadece Seçtiklerimi Göster' moduna geçin."
            )

            f_col1, f_col2, f_col3 = st.columns(3)
            
            # Filtre listelerini hazırla
            u_sites = sorted(data["Üretim Yeri Tanim"].unique().tolist())
            u_groups = sorted(data["Mal grubu"].unique().astype(str).tolist())
            u_purchase = sorted(data["Satınalma grubu"].unique().astype(str).tolist())

            # Mod seçimine göre varsayılan listeyi belirle
            default_sites = u_sites if filtre_modu == "Tüm Verileri Göster" else []
            default_groups = u_groups if filtre_modu == "Tüm Verileri Göster" else []
            default_purchase = u_purchase if filtre_modu == "Tüm Verileri Göster" else []

            with f_col1:
                sel_sites = st.multiselect("📍 Üretim Yeri", u_sites, default=default_sites)
            with f_col2:
                sel_groups = st.multiselect("🔢 Mal Grubu", u_groups, default=default_groups)
            with f_col3:
                sel_purchase = st.multiselect("💼 Satınalma Grubu", u_purchase, default=default_purchase)

            # Filtreleme Mantığı (Eğer mod "Sadece Seçtiklerimi Göster" ise ve kutu boşsa hiçbir şey gösterme)
            if filtre_modu == "Sadece Seçtiklerimi Göster":
                filtered = data[
                    (data["Üretim Yeri Tanim"].isin(sel_sites)) & 
                    (data["Mal grubu"].astype(str).isin(sel_groups)) &
                    (data["Satınalma grubu"].astype(str).isin(sel_purchase))
                ]
            else:
                # Tüm veriler modunda boş kutu = filtre yok demektir
                f_sites = sel_sites if sel_sites else u_sites
                f_groups = sel_groups if sel_groups else u_groups
                f_purchase = sel_purchase if sel_purchase else u_purchase
                
                filtered = data[
                    (data["Üretim Yeri Tanim"].isin(f_sites)) & 
                    (data["Mal grubu"].astype(str).isin(f_groups)) &
                    (data["Satınalma grubu"].astype(str).isin(f_purchase))
                ]

            st.markdown("---")
            
            # --- METRİKLER ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam Kalem", f"{len(filtered)} Adet")
            m2.metric("Listelenen Grup", len(sel_purchase) if sel_purchase else len(u_purchase))
            if "SA siparişi miktarı" in filtered.columns:
                m3.metric("Toplam Miktar", f"{filtered['SA siparişi miktarı'].sum():,.0f}")

            st.dataframe(filtered, use_container_width=True, height=500)

            # İndirme
            csv = filtered.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Veriyi İndir (CSV)", csv, "stok_raporu.csv", "text/csv")

    except Exception as e:
        st.error(f"Hata: {e}")
else:
    st.info("💡 Başlamak için lütfen bir SAP dosyası yükleyin.")
