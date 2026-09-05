import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Geliştirilmiş Canlı Neon Tasarım
st.set_page_config(page_title="BTA Finans Üssü", page_icon="📈", layout="wide")

st.markdown("""
<style>
    @keyframes neonPulse {
        0% { text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 30px #00f2fe; box-shadow: 0 0 15px rgba(0, 242, 254, 0.4); }
        50% { text-shadow: 0 0 20px #4facfe, 0 0 40px #4facfe, 0 0 60px #4facfe; box-shadow: 0 0 30px rgba(79, 172, 254, 0.8); }
        100% { text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 30px #00f2fe; box-shadow: 0 0 15px rgba(0, 242, 254, 0.4); }
    }
    .stApp {
        background: linear-gradient(135deg, #090a0f 0%, #12131c 100%)!important; 
        padding: 0.5rem;
    } 
    h1,h2,h3,h4,h5,h6,p,span,label {
        font-family: 'Segoe UI', sans-serif;
    } 
    input {
        color: #000!important; 
        background-color: #fff!important;
    } 
    .stDataFrame {
        width: 100% !important; 
        border: 2px solid #00f2fe !important; 
        border-radius: 12px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.15);
    } 
    div.block-container {
        padding-top: 1rem; 
        padding-bottom: 0.5rem;
    } 
    .alsat-baslik {
        background: linear-gradient(90deg, #ff007f 0%, #12131c 100%); 
        padding: 12px; 
        border-radius: 8px; 
        font-weight: bold; 
        margin-top: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #ff007f;
        box-shadow: 0 0 10px rgba(255, 0, 127, 0.3);
        font-size: 1.2rem;
        letter-spacing: 1px;
    } 
    .al-baslik {
        background: linear-gradient(90deg, #00f2fe 0%, #12131c 100%); 
        padding: 12px; 
        border-radius: 8px; 
        font-weight: bold; 
        margin-top: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #00f2fe;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
        font-size: 1.2rem;
        letter-spacing: 1px;
    } 
    .spk-kutusu {
        background-color: rgba(255, 75, 75, 0.05); 
        border: 1px dashed #ff4b4b; 
        padding: 12px; 
        border-radius: 8px; 
        margin-top: 30px; 
        margin-bottom: 10px; 
        color: #ff9999 !important; 
        font-size: 0.8rem; 
        text-align: justify;
        line-height: 1.4;
    } 
    .bta-logo-konteyner {
        display: flex; 
        align-items: center; 
        margin-top: 10px; 
        margin-bottom: 15px;
    } 
    .bta-logo {
        background: transparent; 
        color: #00f2fe !important; 
        font-family: 'Segoe UI', sans-serif !important; 
        font-weight: 900; 
        font-size: 3rem; 
        padding: 4px 30px; 
        border-radius: 14px; 
        border: 3px solid #00f2fe;
        animation: neonPulse 2s infinite ease-in-out;
        letter-spacing: 4px;
    } 
    .kilit-uyari {
        background: rgba(255, 75, 75, 0.1); 
        border: 2px solid #ff4b4b; 
        padding: 20px; 
        border-radius: 10px; 
        margin-bottom: 20px; 
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.2);
    } 
    .piyasa-kart {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        font-size: 1.25rem !important; 
        font-weight: bold !important; 
        color: #ffffff !important;
    } 
    div.stButton > button {
        background-color: transparent; 
        color: #00f2fe; 
        border: 2px solid #00f2fe; 
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.2); 
        border-radius: 8px; 
        transition: 0.3s;
    } 
    div.stButton > button:hover {
        background-color: #00f2fe; 
        color: #111; 
        box-shadow: 0 0 25px #00f2fe;
    }
</style>
""", unsafe_allow_html=True)

# 🔑 PARAMETRELER
YONETICI_SIFRESI = "bta2026"
MESAJ_DOSYASI = "gelen_mesajlar.txt"

# Hafıza Kontrolleri
if "oda_kilitli_mi" not in st.session_state: st.session_state["oda_kilitli_mi"] = False
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

for k in ["kisitli_liste", "ziyaret_sayaci", "topham_oy_sayisi", "topham_yildiz_puani"]:
    if k not in st.session_state: st.session_state[k] = 0 if "sayaci" in k or "sayisi" in k or "puani" in k else []

if "sayildi" not in st.session_state:
    st.session_state["ziyaret_sayaci"] += 1
    st.session_state["sayildi"] = True

# BTA LOGO ALANI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# 🛠️ SOL MENÜ: ODA YÖNETİM MERKEZİ
st.sidebar.markdown("### 🛠️ Oda Yönetim Merkezi")
admin_sifre = st.sidebar.text_input("Yönetici Şifresi:", type="password", placeholder="Ayarlar için girin...")

if admin_sifre == YONETICI_SIFRESI:
    st.sidebar.success("⚡ Yönetici Yetkisi Aktif")
    if st.session_state["oda_kilitli_mi"]:
        st.sidebar.error("🔴 Şu an: ODA KİLİTLİ")
        if st.sidebar.button("🔓 Odayı Herkese Aç", use_container_width=True):
            st.session_state["oda_kilitli_mi"] = False
            st.rerun()
    else:
        st.sidebar.success("🟢 Şu an: HERKESE AÇIK")
        if st.sidebar.button("🔒 Odayı Herkese Kilitle", use_container_width=True):
            st.session_state["oda_kilitli_mi"] = True
            st.rerun()
else:
    if admin_sifre: st.sidebar.error("Hatalı Yönetici Şifresi!")

st.sidebar.divider()
st.sidebar.info("Bu menu oda kilit ayarlari için tasarlanmistir.")

# --- 🏢 DURUM KONTROLÜ VE İÇERİK ---

# 1. DURUM: ODA KİLİTLİYSE
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div class="kilit-uyari">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Analiz robotları ve sistem verileri şu an güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
    
    puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="📊 Toplam Giriş", value=st.session_state["ziyaret_sayaci"])
    with col2: st.metric(label="🔥 Toplam Oy", value=st.session_state["topham_oy_sayisi"])
    with col3: st.metric(label="⭐ Panel Puanı", value=f"{puan:.2f} / 5")

# 2. DURUM: ODA AÇIKSA (ASIL İÇERİK MOTORU)
else:
    if st.session_state["oda_kilitli_mi"]:
        st.warning("⚠️ Oda dışarıya kilitli fakat Yönetici olduğunuz için erişim sağladınız.")

    # Üst İstatistik Şeridi
    guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
    st.markdown(f'<div style="font-size: 0.95rem; color: #a5b4fc; margin-bottom: 20px; font-weight:bold;">⭐ Puan: {puan:.2f} | 🔥 Toplam Oy: {st.session_state["topham_oy_sayisi"]} | 🚪 Ziyaretçi: {st.session_state["ziyaret_sayaci"]} | 🕒 {guncel_an}</div>', unsafe_allow_html=True)

    # Canlı Piyasa Metrikleri
    try:
        bist = yf.Ticker("XU100.IS").history(period="1d")['Close'].iloc[-1]
        usd = yf.Ticker("TRY=X").history(period="1d")['Close'].iloc[-1]
        gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1] * 0.0321507466 / 3.42
        
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f'<div class="piyasa-kart"><span style="color:#00f2fe;font-weight:bold;">📈 BIST 100 CANLI</span><h2 style="color:#fff;margin:5px 0;">{bist:,.2f}</h2></div>', unsafe_allow_html=True)
        with m_col2:
            st.markdown(f'<div class="piyasa-kart"><span style="color:#ca8a04;font-weight:bold;">💵 DOLAR / TL</span><h2 style="color:#fff;margin:5px 0;">{usd:.4f} TL</h2></div>', unsafe_allow_html=True)
        with m_col3:
            st.markdown(f'<div class="piyasa-kart"><span style="color:#ff007f;font-weight:bold;">✨ GRAM ALTIN</span><h2 style="color:#fff;margin:5px 0;">{gold:,.2f} TL</h2></div>', unsafe_allow_html=True)
    except:
        pass

    st.write("")

    # Excel Okuma Motoru
    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: 
            df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except Exception as e:
            st.error(f"Excel okuma hatası: {e}")
    else:
        st.warning(f"⚠️ '{excel_yolu}' veri dosyası bulunamadı. Lütfen dizini kontrol edin.")

    def hızlı_canli_fiyat_bul(hisse_kodu):
        if hisse_kodu in st.session_state["fiyat_hafizasi"]:
            saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
            if time.time() - saved_time < 300: return saved_price
        try:
            ticker = yf.Ticker(f"{hisse_kodu}.IS")
            data = ticker.history(period="1d")
            if not data.empty and not pd.isna(data['Close'].iloc[-1]):
                fiyat = float(data['Close'].iloc[-1])
                st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
                return fiyat
        except: pass
        return 0.0

    def temiz_metin_al(val):
        if pd.isna(val): return ""
        return str(val).strip().upper()

    tablo_alsat = []
    tablo_al = []
    hisse_kodlari_listesi = []

    # ORİJİNAL KOD BLOKLARINA DÖNÜŞ (PARANTEZLERİ TABLODA TEMİZLER)
    if df_kaynak is not None:
        for idx in range(2, len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 22:
                    uv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 20])
                    wv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 22])
