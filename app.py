import streamlit as st
import pandas as pd
import os

# Sayfa Ayarları
st.set_page_config(page_title="Enerjisa Üretim - Stok Kontrol & Transfer", layout="wide")

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
    .transfer-form {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
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

# --- NAVİGASYON (SAYFA SEÇİMİ) ---
st.sidebar.title("📌 Menü")
sayfa = st.sidebar.radio("Gitmek İstediğiniz Sayfa:", ["📊 Stok Kontrol Paneli", "🔄 Mal Transfer Kayıt Sayfası"])
st.sidebar.markdown("---")

# ==========================================
# 1. SAYFA: STOK KONTROL PANELİ
# ==========================================
if sayfa == "📊 Stok Kontrol Paneli":
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

                # --- AKILLI FİLTRELEME PANELİ ---
                st.markdown("### 🔍 Akıllı Filtreleme")
                
                filtre_modu = st.radio(
                    "Çalışma Modu Seçin:",
                    ["Tüm Verileri Göster", "Sadece Seçtiklerimi Göster"],
                    horizontal=True,
                    help="Sadece 1-2 grup seçecekseniz 'Sadece Seçtiklerimi Göster' moduna geçin."
                )

                f_col1, f_col2, f_col3 = st.columns(3)
                
                u_sites = sorted(data["Üretim Yeri Tanim"].unique().tolist())
                u_groups = sorted(data["Mal grubu"].unique().astype(str).tolist())
                u_purchase = sorted(data["Satınalma grubu"].unique().astype(str).tolist())

                default_sites = u_sites if filtre_modu == "Tüm Verileri Göster" else []
                default_groups = u_groups if filtre_modu == "Tüm Verileri Göster" else []
                default_purchase = u_purchase if filtre_modu == "Tüm Verileri Göster" else []

                with f_col1:
                    sel_sites = st.multiselect("📍 Üretim Yeri", u_sites, default=default_sites)
                with f_col2:
                    sel_groups = st.multiselect("🔢 Mal Grubu", u_groups, default=default_groups)
                with f_col3:
                    sel_purchase = st.multiselect("💼 Satınalma Grubu", u_purchase, default=default_purchase)

                if filtre_modu == "Sadece Seçtiklerimi Göster":
                    filtered = data[
                        (data["Üretim Yeri Tanim"].isin(sel_sites)) & 
                        (data["Mal grubu"].astype(str).isin(sel_groups)) &
                        (data["Satınalma grubu"].astype(str).isin(sel_purchase))
                    ]
                else:
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

# ==========================================
# 2. SAYFA: MAL TRANSFER KAYIT SAYFASI
# ==========================================
elif sayfa == "🔄 Mal Transfer Kayıt Sayfası":
    st.markdown('<div class="main-title">SANTRALLER ARASI MAL TRANSFER KAYIT SAYFASI</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">Hazırlayan: Onur Sinoplu</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 📝 Yeni Transfer Kaydı Oluştur")
    
    # Form Alanları
    with st.container():
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            sag_no = st.text_input("📋 SAS / SAG Numarası", placeholder="Örn: 45000xxxxx")
            malzeme_kodu = st.text_input("🔢 Malzeme Stok Kodu", placeholder="Örn: 100100xx")
            mal_grubu = st.text_input("📂 Mal Grubu No", placeholder="Örn: K0704xx")
            transfer_miktari = st.number_input("📦 Transfer Miktarı", min_value=1, value=1, step=1)
            
        with col_form2:
            cikis_santral = st.text_input("📤 Çıkış Yapacak Santral (Kaynak)", placeholder="Örn: Bandırma DGKÇS")
            varis_santral = st.text_input("📥 Teslim Alacak Santral (Hedef)", placeholder="Örn: Çanakkale RES")
            
            # İstediğin Kalıcı / Geçici seçeneği
            transfer_tipi = st.radio(
                "🔄 Transfer Türü",
                ["Kalıcı Transfer", "Geçici Transfer (Geri Dönecek)"],
                help="Malzemenin hedef santralde kalıcı mı olacağını yoksa geçici mi gittiğini belirtin.",
                horizontal=True
            )
            
            aciklama = st.text_area("💬 Transfer Açıklaması / Notlar", placeholder="Transfer nedeni, onaylayan kişi vb...")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Kaydet Butonu
        if st.button("🚀 Transfer Kaydını Tamamla", use_container_width=True):
            if not sag_no or not malzeme_kodu or not cikis_santral or not varis_santral:
                st.error("⚠️ Lütfen zorunlu alanları (SAG No, Stok Kodu, Çıkış ve Varış Santralleri) doldurun!")
            else:
                st.success(f"🎉 {sag_no} numaralı Transfer Kaydı Başarıyla Sistemde Oluşturuldu!")
                
                # Girilen verilerin özeti
                st.markdown("#### 📋 Oluşturulan Kayıt Özeti")
                ozet_data = {
                    "Parametre": ["SAS/SAG No", "Malzeme Kodu", "Mal Grubu No", "Miktar", "Çıkış Santrali", "Varış Santrali", "Transfer Tipi", "Açıklama"],
                    "Değer": [sag_no, malzeme_kodu, mal_grubu if mal_grubu else "Belirtilmedi", transfer_miktari, cikis_santral, varis_santral, transfer_tipi, aciklama if aciklama else "-"]
                }
                st.table(pd.DataFrame(ozet_data))

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Enerjisa Üretim Stok Kontrol ve Transfer Sistemi | Onur Sinoplu")
