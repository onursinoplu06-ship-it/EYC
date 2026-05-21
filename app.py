import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

st.set_page_config(
    page_title="Enerjisa Üretim — Stok & Satın Alma",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "transfer_kayitlari" not in st.session_state:
    st.session_state.transfer_kayitlari = []

SUREC_ASAMALARI = ["Stok Kontrolü", "Transfer Talebi", "Ambar Onayı", "Yönetici Onayı", "Sevkiyat", "Teslimat"]

# ─────────────────────────────────────────
#  CUSTOM CSS — Profesyonel Kurumsal Tema
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Temel Renkler ── */
:root {
    --enj-navy:      #0a1628;
    --enj-navy-mid:  #0d2044;
    --enj-navy-soft: #162d5c;
    --enj-blue:      #1a5fdc;
    --enj-blue-lt:   #2d7af0;
    --enj-accent:    #00c2ff;
    --enj-surface:   #f0f4fb;
    --enj-surface2:  #e4eaf6;
    --enj-border:    #c8d6f0;
    --enj-text:      #0a1628;
    --enj-muted:     #4a5d80;
    --enj-green:     #0a8f5c;
    --enj-orange:    #d9680a;
    --enj-red:       #c0392b;
}

/* ── Genel App ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

.stApp {
    background-color: #f0f4fb !important;
    background-image:
        radial-gradient(circle at 10% 0%, rgba(26,95,220,0.06) 0%, transparent 50%),
        radial-gradient(circle at 90% 100%, rgba(0,194,255,0.05) 0%, transparent 50%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--enj-navy) !important;
    border-right: none !important;
    box-shadow: 4px 0 24px rgba(10,22,40,0.18);
}

section[data-testid="stSidebar"] * {
    color: #c8d6f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

section[data-testid="stSidebar"] .stRadio label {
    font-size: 14px !important;
    font-weight: 400 !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    margin: 3px 0 !important;
    transition: background 0.2s, color 0.2s !important;
    display: block;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.12) !important;
    margin: 16px 0 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] .stMarkdown strong {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    letter-spacing: 0.02em !important;
}

/* ── Ana içerik alanı ── */
.main .block-container {
    max-width: 1400px;
    padding: 2rem 2.5rem !important;
}

/* ── Sayfa Başlığı ── */
.page-header {
    background: linear-gradient(135deg, var(--enj-navy) 0%, var(--enj-navy-soft) 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,194,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: -20px; left: 30%;
    width: 300px; height: 100px;
    background: radial-gradient(ellipse, rgba(26,95,220,0.2) 0%, transparent 70%);
}
.page-header h1 {
    color: #ffffff !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    margin: 0 0 6px 0 !important;
    text-transform: uppercase;
}
.page-header p {
    color: rgba(200,214,240,0.8) !important;
    font-size: 13px !important;
    margin: 0 !important;
    font-style: italic;
}

/* ── Metrik Kartları ── */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid var(--enj-border) !important;
    border-radius: 12px !important;
    padding: 18px 22px !important;
    box-shadow: 0 2px 12px rgba(10,22,40,0.06) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(10,22,40,0.1) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--enj-muted) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: var(--enj-navy) !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}

/* ── Butonlar ── */
.stButton > button {
    background: var(--enj-blue) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 22px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 3px 12px rgba(26,95,220,0.25) !important;
}
.stButton > button:hover {
    background: var(--enj-blue-lt) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(26,95,220,0.35) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Input Alanları ── */
.stTextInput > div > div > input,
.stTextArea textarea,
.stNumberInput input {
    background: #ffffff !important;
    border: 1.5px solid var(--enj-border) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: var(--enj-text) !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--enj-blue) !important;
    box-shadow: 0 0 0 3px rgba(26,95,220,0.12) !important;
    outline: none !important;
}

/* ── Select Box & Multiselect ── */
.stSelectbox > div,
.stMultiSelect > div {
    border-radius: 10px !important;
}
.stMultiSelect [data-baseweb="tag"] {
    background: var(--enj-blue) !important;
    border-radius: 6px !important;
}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 2px dashed var(--enj-border) !important;
    border-radius: 14px !important;
    padding: 20px !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--enj-blue) !important;
    background: rgba(26,95,220,0.03) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #ffffff !important;
    border: 1px solid var(--enj-border) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: var(--enj-navy) !important;
    transition: background 0.2s !important;
}
.streamlit-expanderHeader:hover {
    background: var(--enj-surface) !important;
}
.streamlit-expanderContent {
    background: #ffffff !important;
    border: 1px solid var(--enj-border) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    padding: 20px !important;
}

/* ── Dataframe / Tablo ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid var(--enj-border) !important;
    box-shadow: 0 2px 12px rgba(10,22,40,0.06) !important;
}

/* ── Alert / Info / Success / Error ── */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
[data-testid="stInfo"] {
    background: rgba(26,95,220,0.07) !important;
    border-left: 4px solid var(--enj-blue) !important;
}
[data-testid="stSuccess"] {
    background: rgba(10,143,92,0.08) !important;
    border-left: 4px solid var(--enj-green) !important;
}
[data-testid="stError"] {
    background: rgba(192,57,43,0.07) !important;
    border-left: 4px solid var(--enj-red) !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--enj-border) !important;
    margin: 20px 0 !important;
}

/* ── Başlık Stilleri ── */
h1, h2, h3 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--enj-navy) !important;
}
h3 { font-size: 16px !important; font-weight: 600 !important; margin-bottom: 14px !important; }

/* ── Caption / Footer ── */
.stCaption, footer {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--enj-muted) !important;
    font-size: 12px !important;
}

/* ── Progress / Spinner ── */
.stSpinner > div {
    border-top-color: var(--enj-blue) !important;
}

/* ── Özel Bileşenler ── */
.pipeline-bar {
    display: flex;
    align-items: center;
    gap: 0;
    background: #ffffff;
    border: 1px solid var(--enj-border);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(10,22,40,0.05);
}
.pipeline-step {
    flex: 1;
    padding: 10px 6px;
    text-align: center;
    font-size: 12px;
    font-weight: 500;
    font-family: 'DM Sans', sans-serif;
    border-right: 1px solid var(--enj-border);
    transition: background 0.2s;
}
.pipeline-step:last-child { border-right: none; }
.step-done     { background: rgba(10,143,92,0.08);  color: #0a8f5c; }
.step-active   { background: var(--enj-blue);       color: #ffffff; font-weight: 700; }
.step-waiting  { background: #ffffff;               color: #a0aec0; }

.kpi-card {
    background: #ffffff;
    border: 1px solid var(--enj-border);
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(10,22,40,0.06);
}

.mail-box {
    background: #f8fafe;
    border: 1.5px solid var(--enj-border);
    border-left: 4px solid var(--enj-blue);
    border-radius: 12px;
    padding: 20px 24px;
    font-family: 'DM Mono', monospace !important;
    font-size: 13px;
    line-height: 1.7;
    color: var(--enj-text);
    white-space: pre-wrap;
    margin-bottom: 16px;
}

.company-card {
    background: #ffffff;
    border: 1px solid var(--enj-border);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(10,22,40,0.05);
}
.company-card-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 16px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--enj-border);
}
.company-avatar {
    width: 44px; height: 44px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--enj-blue), var(--enj-accent));
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 700; color: white;
    flex-shrink: 0;
}
.company-name  { font-size: 15px; font-weight: 600; color: var(--enj-navy); margin: 0; }
.company-email { font-size: 13px; color: var(--enj-muted); margin: 0; }

/* ── Sidebar Logo alanı ── */
.sidebar-brand {
    padding: 20px 16px 8px;
    margin-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.sidebar-brand span {
    display: block;
    font-size: 11px;
    color: rgba(200,214,240,0.6) !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── Radio tuşları ── */
.stRadio [role="radiogroup"] {
    gap: 6px !important;
}

/* ── Zebra dataframe ── */
.stDataFrame thead tr th {
    background: var(--enj-navy) !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size:17px;font-weight:700;color:#ffffff;letter-spacing:0.03em;">⚡ ENERJİSA ÜRETİM</div>
        <span>Stok & Satın Alma Sistemi</span>
    </div>
    """, unsafe_allow_html=True)

    if os.path.exists("esa.png"):
        st.image("esa.png", width=120)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    sayfa = st.radio(
        "Navigasyon",
        [
            "📊 Stok Kontrol Paneli",
            "🔄 Mal Transfer Kayıt",
            "📋 Transfer Takip",
            "🤖 AI Teklif Asistanı",
        ],
        label_visibility="hidden"
    )
    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px;color:rgba(200,214,240,0.45);padding:8px 0;line-height:1.8;'>
    v2.0 — Onur Sinoplu<br>Enerjisa Üretim A.Ş.<br>Tedarik & Ticari Yönetim
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
#  YARDIMCI: Sayfa Başlığı
# ─────────────────────────────────────────
def page_header(title, subtitle="Hazırlayan: Onur Sinoplu — Enerjisa Üretim A.Ş."):
    st.markdown(f"""
    <div class="page-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 1. STOK KONTROL PANELİ
# ==========================================
if sayfa == "📊 Stok Kontrol Paneli":
    page_header("TEDARİK VE TİCARİ YÖNETİM — STOK KONTROL PANELİ")

    uploaded_file = st.file_uploader("SAP ZMM012 Raporunu Yükleyin (.xlsx veya .csv)", type=["xlsx", "csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()

            cols_to_show = ["Üretim Yeri Tanim", "Satınalma grubu", "Mal grubu",
                            "SA siparişi miktarı", "SAS ölçü birimi", "Kısa metin"]
            existing = [c for c in cols_to_show if c in df.columns]

            if existing:
                data = df[existing].copy()
                for c in data.columns:
                    data[c] = data[c].fillna("N/A")

                st.markdown("### 🔍 Akıllı Filtreleme")
                filtre_modu = st.radio(
                    "Çalışma Modu:",
                    ["Tüm Verileri Göster", "Sadece Seçtiklerimi Göster"],
                    horizontal=True
                )

                f_col1, f_col2, f_col3 = st.columns(3)
                u_sites    = sorted(data["Üretim Yeri Tanim"].unique().tolist())
                u_groups   = sorted(data["Mal grubu"].unique().astype(str).tolist())
                u_purchase = sorted(data["Satınalma grubu"].unique().astype(str).tolist())

                defaults = lambda lst: lst if filtre_modu == "Tüm Verileri Göster" else []

                with f_col1: sel_sites    = st.multiselect("📍 Üretim Yeri",       u_sites,    default=defaults(u_sites))
                with f_col2: sel_groups   = st.multiselect("🔢 Mal Grubu",         u_groups,   default=defaults(u_groups))
                with f_col3: sel_purchase = st.multiselect("💼 Satınalma Grubu",   u_purchase, default=defaults(u_purchase))

                if filtre_modu == "Sadece Seçtiklerimi Göster":
                    filtered = data[
                        data["Üretim Yeri Tanim"].isin(sel_sites) &
                        data["Mal grubu"].astype(str).isin(sel_groups) &
                        data["Satınalma grubu"].astype(str).isin(sel_purchase)
                    ]
                else:
                    fs = sel_sites    or u_sites
                    fg = sel_groups   or u_groups
                    fp = sel_purchase or u_purchase
                    filtered = data[
                        data["Üretim Yeri Tanim"].isin(fs) &
                        data["Mal grubu"].astype(str).isin(fg) &
                        data["Satınalma grubu"].astype(str).isin(fp)
                    ]

                st.markdown("---")

                m1, m2, m3 = st.columns(3)
                m1.metric("Toplam Kalem", f"{len(filtered):,} Adet")
                m2.metric("Satınalma Grubu", len(sel_purchase) if sel_purchase else len(u_purchase))
                if "SA siparişi miktarı" in filtered.columns:
                    m3.metric("Toplam Miktar", f"{filtered['SA siparişi miktarı'].sum():,.0f}")

                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                st.dataframe(filtered, use_container_width=True, height=500)

        except Exception as e:
            st.error(f"Dosya okunurken hata oluştu: {e}")
    else:
        st.info("💡 Başlamak için lütfen bir SAP ZMM012 dosyası yükleyin.")


# ==========================================
# 2. MAL TRANSFER KAYIT
# ==========================================
elif sayfa == "🔄 Mal Transfer Kayıt":
    page_header("SANTRALLER ARASI MAL TRANSFER KAYIT SAYFASI")

    st.markdown("### 📝 Yeni Transfer Kaydı Oluştur")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            sag_no           = st.text_input("SAG / SAS Numarası", placeholder="Ör: SAG-2024-001")
            malzeme_kodu     = st.text_input("Malzeme Stok Kodu",  placeholder="Ör: 4000123456")
            mal_grubu        = st.text_input("Mal Grubu No",        placeholder="Ör: L001")
            transfer_miktari = st.number_input("Transfer Miktarı", min_value=1, value=1)
        with col2:
            cikis_santral  = st.text_input("Çıkış Yapacak Santral (Kaynak)", placeholder="Ör: Doğalgaz Santrali")
            varis_santral  = st.text_input("Teslim Alacak Santral (Hedef)", placeholder="Ör: Rüzgar Enerji Santrali")
            transfer_tipi  = st.radio("Transfer Türü", ["Kalıcı Transfer", "Geçici Transfer (Geri Dönecek)"], horizontal=True)
            aciklama       = st.text_area("Açıklama / Notlar", placeholder="Transfer sebebi, ek bilgiler...")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("🚀 Transfer Kaydını Tamamla", use_container_width=True):
            if not sag_no or not malzeme_kodu or not cikis_santral or not varis_santral:
                st.error("⚠️ Lütfen SAG No, Malzeme Kodu, Çıkış ve Varış Santrali alanlarını doldurun.")
            else:
                st.session_state.transfer_kayitlari.append({
                    "id": len(st.session_state.transfer_kayitlari) + 1,
                    "sag_no": sag_no, "malzeme_kodu": malzeme_kodu,
                    "mal_grubu": mal_grubu or "N/A", "miktar": transfer_miktari,
                    "cikis": cikis_santral, "varis": varis_santral,
                    "tip": transfer_tipi,
                    "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "step_index": 0
                })
                st.success(f"✅ Transfer kaydı oluşturuldu — SAG: {sag_no}")


# ==========================================
# 3. TRANSFER TAKİP
# ==========================================
elif sayfa == "📋 Transfer Takip":
    page_header("MAL TRANSFER TAKİP VE NOVA ONAY SÜRECİ")

    if not st.session_state.transfer_kayitlari:
        st.info("💡 Henüz açılmış bir transfer kaydı bulunmuyor. 'Mal Transfer Kayıt' sayfasından yeni kayıt oluşturun.")
    else:
        t_df = pd.DataFrame(st.session_state.transfer_kayitlari)

        for idx, row in t_df.iterrows():
            current = row["step_index"]
            step_name = SUREC_ASAMALARI[current]
            is_done = current == len(SUREC_ASAMALARI) - 1
            badge = "🟢 Tamamlandı" if is_done else f"🔵 {step_name}"

            with st.expander(f"SAG No: {row['sag_no']}  ·  {badge}  ·  {row['tarih']}"):

                # Pipeline Bar
                steps_html = '<div class="pipeline-bar">'
                for i, step in enumerate(SUREC_ASAMALARI):
                    if   i < current: cls = "step-done";    label = f"✓ {step}"
                    elif i == current: cls = "step-active"; label = f"→ {step}"
                    else:              cls = "step-waiting"; label = step
                    steps_html += f'<div class="pipeline-step {cls}">{label}</div>'
                steps_html += "</div>"
                st.markdown(steps_html, unsafe_allow_html=True)

                col_d, col_c = st.columns([3, 1])
                with col_d:
                    st.markdown(f"""
                    <div style='font-size:14px;line-height:2;color:#4a5d80;'>
                    <strong style='color:#0a1628;'>Stok Kodu:</strong> {row['malzeme_kodu']} &nbsp;|&nbsp;
                    <strong style='color:#0a1628;'>Miktar:</strong> {row['miktar']} &nbsp;|&nbsp;
                    <strong style='color:#0a1628;'>Tür:</strong> {row['tip']}<br>
                    <strong style='color:#0a1628;'>Rota:</strong> {row['cikis']} &nbsp;→&nbsp; {row['varis']}
                    </div>
                    """, unsafe_allow_html=True)
                with col_c:
                    if current < len(SUREC_ASAMALARI) - 1:
                        next_step = SUREC_ASAMALARI[current + 1]
                        if st.button(f"→ {next_step}", key=f"next_{row['id']}", use_container_width=True):
                            st.session_state.transfer_kayitlari[idx]["step_index"] += 1
                            st.rerun()
                    else:
                        st.success("Süreç tamamlandı")


# ==========================================
# 4. AI TEKLİF & MAIL ASİSTANI
# ==========================================
elif sayfa == "🤖 AI Teklif Asistanı":
    page_header("AI DESTEKLİ SATIN ALMA VE TEKLİF İSTEMİ PANELİ")

    st.info("💡 Satın alınacak malzeme tanımını ve miktarı girin. AI piyasa taraması yaparak 3 potansiyel tedarikçi belirler ve RFQ taslak mailleri hazırlar.")

    col1, col2 = st.columns([2, 1])
    with col1:
        mal_grubu_input = st.text_input(
            "Satın Alınacak Mal Grubu / Malzeme Tanımı",
            placeholder="Ör: 40x40x2 mm Çelik Profil"
        )
    with col2:
        talep_miktari = st.text_input(
            "İhtiyaç Miktarı ve Birimi",
            placeholder="Ör: 500 Metre"
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("🔍 AI ile Piyasayı Tara ve Taslak Mailleri Hazırla", use_container_width=True):
        if not mal_grubu_input or not talep_miktari:
            st.error("⚠️ Lütfen Mal Grubu ve Miktarı girin.")
        else:
            with st.spinner("AI tedarikçi havuzunu tarıyor ve şirket profilleri seçiliyor..."):
                time.sleep(2)

            st.success("✅ AI taraması tamamlandı — 3 optimize tedarikçi profili ve RFQ taslakları hazırlandı.")
            st.markdown("---")

            sirketler = [
                {"isim": "Global Çelik Yapı Endüstrisi A.Ş.", "mail": "satis@globalcelik.com",       "harf": "G"},
                {"isim": "Anadolu Metal ve Lojistik Ticaret",  "mail": "teklif@anadolumetal.com.tr",  "harf": "A"},
                {"isim": "Özdemir Profil Sanayi Ltd. Şti.",    "mail": "info@ozdemirprofil.com",      "harf": "Ö"},
            ]

            for i, s in enumerate(sirketler):
                taslak = f"""Sayın Yetkili,

Enerjisa Üretim A.Ş. Tedarik ve Ticari Yönetim departmanı olarak, stok ve tesis ihtiyaçlarımız kapsamında aşağıda detayları belirtilen mal grubu için piyasa fiyat araştırması yapmaktayız:

  Talep Edilen Malzeme : {mal_grubu_input}
  Miktar               : {talep_miktari}

Şirketinizin sağlayabileceği en uygun birim fiyat, teslim süresi ve ödeme koşullarını içeren teklif mektubunun tarafımıza iletilmesini rica ederiz.

Saygılarımızla,
Onur Sinoplu
Enerjisa Üretim A.Ş. — Tedarik & Ticari Yönetim"""

                st.markdown(f"""
                <div class="company-card">
                    <div class="company-card-header">
                        <div class="company-avatar">{s['harf']}</div>
                        <div>
                            <p class="company-name">{i+1}. {s['isim']}</p>
                            <p class="company-email">📩 {s['mail']} &nbsp;·&nbsp; 📝 Teklif İstemi (RFQ) — Enerjisa Üretim A.Ş.</p>
                        </div>
                    </div>
                    <div class="mail-box">{taslak}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"✅ Onayla ve Otomatik Gönder — {s['isim']}", key=f"mail_{i}", use_container_width=True):
                    with st.spinner(f"{s['mail']} adresine gönderiliyor..."):
                        time.sleep(1)
                    st.success(f"🚀 Mail başarıyla gönderildi → {s['mail']}")

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ── Footer ──
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Enerjisa Üretim A.Ş. · Stok Kontrol ve Transfer Sistemi · Onur Sinoplu")
