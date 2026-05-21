import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Enerjisa Üretim - Stok & Transfer Yönetimi", layout="wide")

# --- OTURUM HAFIZASI (SESSION STATE) İLKLENDİRME ---
# Sayfalar arası veri taşımak ve kayıtları tutmak için hafıza alanı oluşturuyoruz
if "transfer_kayitlari" not in st.session_state:
    st.session_state.transfer_kayitlari = []

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
    .nova-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
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
sayfa = st.sidebar.radio(
    "Gitmek İstediğiniz Sayfa:", 
    ["📊 Stok Kontrol Paneli", "🔄 Mal Transfer Kayıt Sayfası", "📋 Mal Transfer Takip Sayfası"]
)
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
            
            transfer_tipi = st.radio(
                "🔄 Transfer Türü",
                ["Kalıcı Transfer", "Geçici Transfer (Geri Dönecek)"],
                horizontal=True
            )
            aciklama = st.text_area("💬 Transfer Açıklaması / Notlar", placeholder="Transfer nedeni...")

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Transfer Kaydını Tamamla", use_container_width=True):
            if not sag_no or not malzeme_kodu or not cikis_santral or not varis_santral:
                st.error("⚠️ Lütfen zorunlu alanları doldurun!")
            else:
                # Yeni kaydı session_state listesine bir sözlük (dict) olarak ekliyoruz
                yeni_kayit = {
                    "id": len(st.session_state.transfer_kayitlari) + 1,
                    "sag_no": sag_no,
                    "malzeme_kodu": malzeme_kodu,
                    "mal_grubu": mal_grubu if mal_grubu else "N/A",
                    "miktar": transfer_miktari,
                    "cikis": cikis_santral,
                    "varis": varis_santral,
                    "tip": transfer_tipi,
                    "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "nova_durum": "Talep Oluşturuldu" # Başlangıç onay statüsü
                }
                st.session_state.transfer_kayitlari.append(yeni_kayit)
                st.success(f"🎉 {sag_no} numaralı Transfer Kaydı Başarıyla Hafızaya Alındı! Takip sayfasından kontrol edebilirsiniz.")

# ==========================================
# 3. SAYFA: MAL TRANSFER TAKİP SAYFASI (YENİ!)
# ==========================================
elif sayfa == "📋 Mal Transfer Takip Sayfası":
    st.markdown('<div class="main-title">MAL TRANSFER TAKİP VE NOVA ONAY SÜRECİ</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">Hazırlayan: Onur Sinoplu</div>', unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.transfer_kayitlari:
        st.info("💡 Henüz açılmış bir transfer kaydı bulunmuyor. Kayıt oluşturmak için 'Mal Transfer Kayıt Sayfası'nı kullanın.")
    else:
        # Özet İstatistikler
        t_df = pd.DataFrame(st.session_state.transfer_kayitlari)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Transfer Talebi", f"{len(t_df)} Adet")
        m2.metric("Bekleyen Nova Onayı", f"{len(t_df[t_df['nova_durum'] != 'Onaylandı'])} Kalem")
        m3.metric("Tamamlanan", f"{len(t_df[t_df['nova_durum'] == 'Onaylandı'])} Kalem")
        
        st.markdown("### 🔍 Güncel Transfer Talepleri ve Nova Durumu")
        
        # Kullanıcıların onay süreçlerini tek tek yönetebileceği interaktif bir alan tasarlayalım
        for idx, row in t_df.iterrows():
            # Her kayıt için ayrı bir kutu (expander) açıyoruz
            durum_rengi = "🔵" if row['nova_durum'] == "Talep Oluşturuldu" else "🟢" if row['nova_durum'] == "Onaylandı" else "🔴"
            
            with st.expander(f"{durum_rengi} SAG No: {row['sag_no']} | {row['cikis']} -> {row['varis']} ({row['tip']})"):
                col_detay1, col_detay2, col_detay3 = st.columns([2, 2, 1])
                
                with col_detay1:
                    st.markdown(f"**Stok Kodu:** {row['malzeme_kodu']}")
                    st.markdown(f"**Mal Grubu No:** {row['mal_grubu']}")
                    st.markdown(f"**Miktar:** {row['miktar']}")
                    
                with col_detay2:
                    st.markdown(f"**Oluşturulma Tarihi:** {row['tarih']}")
                    st.markdown(f"**Nova Onay Durumu:** `{row['nova_durum']}`")
                
                # Nova Onay Süreci Butonları
                with col_detay3:
                    st.markdown("**Nova İşlemleri**")
                    if row['nova_durum'] == "Talep Oluşturuldu":
                        if st.button("✅ Onayla", key=f"onay_{row['id']}"):
                            st.session_state.transfer_kayitlari[idx]['nova_durum'] = "Onaylandı"
                            st.rerun()
                        if st.button("❌ Reddet", key=f"red_{row['id']}"):
                            st.session_state.transfer_kayitlari[idx]['nova_durum'] = "Reddedildi"
                            st.rerun()
                    elif row['nova_durum'] == "Onaylandı":
                        st.success("Süreç Tamamlandı")
                    else:
                        st.error("Talep Reddedildi")

        # Toplu Tablo Görünümü
        st.markdown("### 📋 Toplu Liste Görünümü")
        st.dataframe(
            t_df[["sag_no", "malzeme_kodu", "mal_grubu", "miktar", "cikis", "varis", "tip", "tarih", "nova_durum"]],
            use_container_width=True
        )

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Enerjisa Üretim Stok Kontrol ve Transfer Sistemi | Onur Sinoplu")
