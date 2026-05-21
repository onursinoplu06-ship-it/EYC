import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

# Sayfa Ayarları
st.set_page_config(page_title="Enerjisa Üretim - Stok & Satın Alma Yönetimi", layout="wide")

# --- OTURUM HAFIZASI (SESSION STATE) ---
if "transfer_kayitlari" not in st.session_state:
    st.session_state.transfer_kayitlari = []

SUREC_ASAMALARI = ["Stok Kontrolü", "Transfer Talebi", "Ambar Onayı", "Yönetici Onayı", "Sevkiyat", "Teslimat"]

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
    .step-container {
        display: flex;
        justify-content: space-between;
        background-color: #f1f3f5;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 5px solid #004a99;
    }
    .step-item { font-family: 'Segoe UI', sans-serif; font-size: 13px; font-weight: 600; }
    .step-done { color: #2b8a3e; }
    .step-active { color: #e67e22; font-weight: 700; }
    .step-waiting { color: #adb5bd; }
    
    /* AI Sayfası Mail Kutusu Tasarımı */
    .mail-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px dashed #004a99;
        font-family: monospace;
        white-space: pre-wrap;
        margin-bottom: 15px;
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

# --- NAVİGASYON (SAYFA SEÇİMİ - 4 SAYFA OLDU) ---
st.sidebar.title("📌 Menü")
sayfa = st.sidebar.radio(
    "Gitmek İstediğiniz Sayfa:", 
    [
        "📊 Stok Kontrol Paneli", 
        "🔄 Mal Transfer Kayıt Sayfası", 
        "📋 Mal Transfer Takip Sayfası",
        "🤖 AI Teklif & Mail Asistanı" # Yeni Eklenen Sayfa
    ]
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
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)

            df.columns = df.columns.str.strip()
            cols_to_show = ["Üretim Yeri Tanim", "Satınalma grubu", "Mal grubu", "SA siparişi miktarı", "SAS ölçü birimi", "Kısa metin"]
            existing = [c for c in cols_to_show if c in df.columns]
            
            if existing:
                data = df[existing].copy()
                for c in data.columns: data[c] = data[c].fillna("N/A")

                st.markdown("### 🔍 Akıllı Filtreleme")
                filtre_modu = st.radio("Çalışma Modu Seçin:", ["Tüm Verileri Göster", "Sadece Seçtiklerimi Göster"], horizontal=True)

                f_col1, f_col2, f_col3 = st.columns(3)
                u_sites = sorted(data["Üretim Yeri Tanim"].unique().tolist())
                u_groups = sorted(data["Mal grubu"].unique().astype(str).tolist())
                u_purchase = sorted(data["Satınalma grubu"].unique().astype(str).tolist())

                default_sites = u_sites if filtre_modu == "Tüm Verileri Göster" else []
                default_groups = u_groups if filtre_modu == "Tüm Verileri Göster" else []
                default_purchase = u_purchase if filtre_modu == "Tüm Verileri Göster" else []

                with f_col1: sel_sites = st.multiselect("📍 Üretim Yeri", u_sites, default=default_sites)
                with f_col2: sel_groups = st.multiselect("🔢 Mal Grubu", u_groups, default=default_groups)
                with f_col3: sel_purchase = st.multiselect("💼 Satınalma Grubu", u_purchase, default=default_purchase)

                if filtre_modu == "Sadece Seçtiklerimi Göster":
                    filtered = data[(data["Üretim Yeri Tanim"].isin(sel_sites)) & (data["Mal grubu"].astype(str).isin(sel_groups)) & (data["Satınalma grubu"].astype(str).isin(sel_purchase))]
                else:
                    f_sites = sel_sites if sel_sites else u_sites
                    f_groups = sel_groups if sel_groups else u_groups
                    f_purchase = sel_purchase if sel_purchase else u_purchase
                    filtered = data[(data["Üretim Yeri Tanim"].isin(f_sites)) & (data["Mal grubu"].astype(str).isin(f_groups)) & (data["Satınalma grubu"].astype(str).isin(f_purchase))]

                st.markdown("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("Toplam Kalem", f"{len(filtered)} Adet")
                m2.metric("Listelenen Grup", len(sel_purchase) if sel_purchase else len(u_purchase))
                if "SA siparişi miktarı" in filtered.columns: m3.metric("Toplam Miktar", f"{filtered['SA siparişi miktarı'].sum():,.0f}")

                st.dataframe(filtered, use_container_width=True, height=500)
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
            sag_no = st.text_input("📋 SAS / SAG Numarası")
            malzeme_kodu = st.text_input("🔢 Malzeme Stok Kodu")
            mal_grubu = st.text_input("📂 Mal Grubu No")
            transfer_miktari = st.number_input("📦 Transfer Miktarı", min_value=1, value=1)
        with col_form2:
            cikis_santral = st.text_input("📤 Çıkış Yapacak Santral (Kaynak)")
            varis_santral = st.text_input("📥 Teslim Alacak Santral (Hedef)")
            transfer_tipi = st.radio("🔄 Transfer Türü", ["Kalıcı Transfer", "Geçici Transfer (Geri Dönecek)"], horizontal=True)
            aciklama = st.text_area("💬 Transfer Açıklaması / Notlar")

        if st.button("🚀 Transfer Kaydını Tamamla", use_container_width=True):
            if not sag_no or not malzeme_kodu or not cikis_santral or not varis_santral:
                st.error("⚠️ Lütfen zorunlu alanları doldurun!")
            else:
                yeni_kayit = {
                    "id": len(st.session_state.transfer_kayitlari) + 1, "sag_no": sag_no, "malzeme_kodu": malzeme_kodu,
                    "mal_grubu": mal_grubu if mal_grubu else "N/A", "miktar": transfer_miktari, "cikis": cikis_santral,
                    "varis": varis_santral, "tip": transfer_tipi, "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"), "step_index": 0
                }
                st.session_state.transfer_kayitlari.append(yeni_kayit)
                st.success("🎉 Transfer Kaydı Başarıyla Hafızaya Alındı!")

# ==========================================
# 3. SAYFA: MAL TRANSFER TAKİP SAYFASI
# ==========================================
elif sayfa == "📋 Mal Transfer Takip Sayfası":
    st.markdown('<div class="main-title">MAL TRANSFER TAKİP VE NOVA ONAY SÜRECİ</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">Hazırlayan: Onur Sinoplu</div>', unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.transfer_kayitlari:
        st.info("💡 Henüz açılmış bir transfer kaydı bulunmuyor.")
    else:
        t_df = pd.DataFrame(st.session_state.transfer_kayitlari)
        for idx, row in t_df.iterrows():
            current_step_idx = row['step_index']
            current_step_name = SUREC_ASAMALARI[current_step_idx]
            durum_emojisi = "🟢" if current_step_idx == len(SUREC_ASAMALARI) - 1 else "🔵"
            
            with st.expander(f"{durum_emojisi} SAG No: {row['sag_no']} | Mevcut Aşama: {current_step_name}"):
                pipeline_html = '<div class="step-container">'
                for i, step in enumerate(SUREC_ASAMALARI):
                    if i < current_step_idx: pipeline_html += f'<span class="step-item step-done">✅ {step}</span>'
                    elif i == current_step_idx: pipeline_html += f'<span class="step-item step-active">➔ {step}</span>'
                    else: pipeline_html += f'<span class="step-item step-waiting">○ {step}</span>'
                    if i < len(SUREC_ASAMALARI) - 1: pipeline_html += ' | '
                pipeline_html += '</div>'
                st.markdown(pipeline_html, unsafe_allow_html=True)
                
                col_detay1, col_control = st.columns([3, 1])
                with col_detay1:
                    st.write(f"**Stok Kodu:** {row['malzeme_kodu']} | **Miktar:** {row['miktar']} | **Rota:** {row['cikis']} -> {row['varis']}")
                with col_control:
                    if current_step_idx < len(SUREC_ASAMALARI) - 1:
                        next_step_name = SUREC_ASAMALARI[current_step_idx + 1]
                        if st.button(f"➡️ Aşamayı İlerlet", key=f"next_{row['id']}", use_container_width=True):
                            st.session_state.transfer_kayitlari[idx]['step_index'] += 1
                            st.rerun()

# ==========================================
# 4. SAYFA:🤖 AI TEKLİF & MAİL ASİSTANI (YENİ!)
# ==========================================
elif sayfa == "🤖 AI Teklif & Mail Asistanı":
    st.markdown('<div class="main-title">AI DESTEKLİ SATIN ALMA VE TEKLİF İSTEMİ PANELİ</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">Hazırlayan: Onur Sinoplu</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🤖 Akıllı Teklif Toplama Sihirbazı")
    st.info("💡 Satın alınacak mal grubunu veya malzeme detayını girdiğinizde, yapay zeka piyasa taraması yaparak en uygun 3 potansiyel firmayı belirler ve otomatik RFQ (Teklif İstemi) mailleri hazırlar.")

    # Giriş Alanları
    col_ai1, col_ai2 = st.columns([2, 1])
    with col_ai1:
        mal_grubu_input = st.text_input("📂 Satın Alınacak Mal Grubu / Malzeme Tanımı", placeholder="Örn: 40x40x2 mm Çelik Profil veya Güneş Paneli Konstrüksiyon Elemanları")
    with col_ai2:
        talep_miktari = st.text_input("📦 İhtiyaç Miktarı ve Birimi", placeholder="Örn: 500 Metre, 50 Adet")

    if st.button("🔍 AI ile Piyasayı Tara ve Taslak Mailleri Hazırla", use_container_width=True):
        if not mal_grubu_input or not talep_miktari:
            st.error("⚠️ Lütfen Mal Grubu Tanımını ve Miktarını giriniz!")
        else:
            # Yapay zeka arama simülasyonu (Loading animasyonu)
            with st.spinner("AI internet ağlarında tedarikçi havuzunu tarıyor, 3 adet optimize şirket profili seçiliyor..."):
                time.sleep(2) # Simülasyon gecikmesi
            
            st.success("🤖 AI Taraması Tamamlandı! En uygun fiyat/performans sağlayabilecek 3 şirket ve özel taslak mailler çıkarıldı.")
            st.markdown("---")

            # Simüle edilen Şirketler (İleride burası tamamen Gemini çıktısı olacak)
            sirketler = [
                {"isim": "Global Çelik Yapı Endüstrisi A.Ş.", "mail": "satis@globalcelik.com"},
                {"isim": "Anadolu Metal ve Lojistik Ticaret", "mail": "teklif@anadolumetal.com.tr"},
                {"isim": "Özdemir Profil Sanayi Ltd. Şti.", "mail": "info@ozdemirprofil.com"}
            ]

            # 3 Şirket için Yan Yana Kartlar ve Mailler
            for i, sirket in enumerate(sirketler):
                st.markdown(f"#### 🏢 {i+1}. Şirket: {sirket['isim']}")
                st.write(f"📩 **Alıcı:** {sirket['mail']} | 📝 **Konu:** Teklif İstemi (RFQ) - Enerjisa Üretim A.Ş.")
                
                # Dinamik olarak oluşturulan taslak mail içeriği
                taslak_mail = f"""Sayın Yetkili,

Enerjisa Üretim A.Ş. Tedarik ve Ticari Yönetim departmanı olarak, stok ve tesis ihtiyaçlarımız kapsamında aşağıda detayları belirtilen mal grubu için piyasa fiyat araştırması yapmaktayız:

Talep Edilen Malzeme: {mal_grubu_input}
Miktar: {talep_miktari}

Şirketiniz tarafından sağlanabilecek en uygun birim fiyat, teslim süresi ve ödeme koşullarını içeren teklif mektubunuzun tarafımıza iletilmesini rica ederiz.

Saygılarımızla,
Onur Sinoplu
Enerjisa Üretim A.Ş."""

                # Taslağı Göster
                st.markdown(f'<div class="mail-box">{taslak_mail}</div>', unsafe_allow_html=True)
                
                # Onay ve Gönderim Butonu
                if st.button(f"✅ Onayla ve Maili Otomatik Gönder ({sirket['isim']})", key=f"send_mail_{i}"):
                    with st.spinner("Mail sunucusuna bağlanılıyor, kriptolu çıkış yapılıyor..."):
                        time.sleep(1)
                    st.success(f"🚀 Başarılı: Taslak mail onaylandı ve {sirket['mail']} adresine otomatik olarak gönderildi!")
                st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Enerjisa Üretim Stok Kontrol ve Transfer Sistemi | Onur Sinoplu")
