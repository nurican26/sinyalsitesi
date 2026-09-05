import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# CSS Tasarımı - Sağdan Sola Yavaşça Akan El Yazılı Gökkuşağı Neon BTA Logosu
st.markdown("""
<style>
    @import url('https://googleapis.com');

    /* Gökkuşağı Renk Değişim Animasyonu */
    @keyframes rainbowNeon {
        0% { color: #ff007f !important; text-shadow: 0 0 15px #ff007f, 0 0 30px #ff007f; }
        25% { color: #00f2fe !important; text-shadow: 0 0 15px #00f2fe, 0 0 30px #00f2fe; }
        50% { color: #10b981 !important; text-shadow: 0 0 15px #10b981, 0 0 30px #10b981; }
        75% { color: #a855f7 !important; text-shadow: 0 0 15px #a855f7, 0 0 30px #a855f7; }
        100% { color: #ff007f !important; text-shadow: 0 0 15px #ff007f, 0 0 30px #ff007f; }
    }

    /* Sağdan Sola Yavaş Kayma Animasyonu */
    @keyframes marquee {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; 
        padding: 0.5rem;
    } 
    h1,h2,h3,h4,h5,h6,p,span,label {
        color: #fff!important; 
        font-family: "Segoe UI", sans-serif;
    } 
    input {
        color: #000!important; 
        background-color: #fff!important;
    } 
    .stDataFrame {
        width: 100% !important; 
        border: 1px solid #10b981 !important; 
        border-radius: 8px;
    } 
    div.block-container {
        padding-top: 1rem; 
        padding-bottom: 0.5rem;
    } 
    .alsat-baslik {
        background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); 
        padding: 8px; 
        border-radius: 5px; 
        font-weight: bold; 
        margin-bottom: 5px;
    } 
    .al-baslik {
        background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); 
        padding: 8px; 
        border-radius: 5px; 
        font-weight: bold; 
        margin-bottom: 5px;
    } 
    /* Yavaşça Kayan Logo Konteyneri */
    .bta-logo-konteyner {
        width: 100%;
        overflow: hidden; 
        white-space: nowrap;
        margin-top: 10px; 
        margin-bottom: 25px;
        padding: 10px 0;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
    } 
    /* EL YAZILI, BİTİŞİK VE SAĞDAN SOLA YAVAŞÇA KAYAN GÖKKUŞAĞI BTA YAZISI */
    .bta-logo {
        display: inline-block;
        font-family: 'Alex Brush', cursive !important; 
        font-style: italic !important;
        font-weight: normal !important; 
        font-size: 6rem; 
        letter-spacing: 0px; 
        padding-left: 100%; 
        animation: marquee 25s infinite linear, rainbowNeon 8s infinite linear; 
    } 
    .kilit-uyari {
        background: rgba(255, 255, 255, 0.05); 
        border-left: 4px solid #ca8a04; 
        padding: 15px; 
        border-radius: 6px; 
        margin-bottom: 20px; 
        font-size: 1.1rem;
    } 
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        font-size: 1.25rem !important; 
        font-weight: bold !important; 
        color: #ffffff !important;
    } 
    div.stButton > button {
        background-color: transparent; 
        color: #45f3ff; 
        border: 2px solid #45f3ff; 
        box-shadow: 0 0 10px #45f3ff; 
        border-radius: 8px; 
        transition: 0.3s;
    } 
    div.stButton > button:hover {
        background-color: #45f3ff; 
        color: #111; 
        box-shadow: 0 0 20px #45f3ff;
    }
    .piyasa-kutusu {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #3b82f6;
        text-align: center;
        margin-bottom: 10px;
    }
    .spk-kutusu {
        background: rgba(231, 76, 60, 0.1);
        border-left: 5px solid #e74c3c;
        padding: 15px;
        border-radius: 6px;
        margin-top: 40px;
        font-size: 0.85rem;
        color: #cccccc !important;
    }
</style>
""", unsafe_allow_html=True)

# 🔑 PARAMETRELER
YONETICI_SIFRESI = "bta2026"

# Hafıza Kontrolleri
if "oda_kilitli_mi" not in st.session_state: st.session_state["oda_kilitli_mi"] = False
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}
if "sohbet_gecmisi" not in st.session_state: st.session_state["sohbet_gecmisi"] = []

# BTA LOGO ALANI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# 🛠️ SOL MENÜ: ODA YÖNETİM MERKEZİ
st.sidebar.markdown("### 🛠️ Oda Yönetim Merkezi")
admin_sifre = st.sidebar.text_input("Yönetici Şifresi:", type="password", placeholder="Ayarlar için girin...", key="admin_sifre_input_bta")

if admin_sifre == YONETICI_SIFRESI:
    st.sidebar.success("⚡ Yönetici Yetkisi Aktif")
    if st.session_state["oda_kilitli_mi"]:
        st.sidebar.error("🔴 Şu an: ODA KİLİTLİ")
        if st.sidebar.button("🔓 Odayı Herkese Aç", use_container_width=True, key="oda_ac_btn_bta"):
            st.session_state["oda_kilitli_mi"] = False
            st.rerun()
    else:
        st.sidebar.success("🟢 Şu an: HERKESE AÇIK")
        if st.sidebar.button("🔒 Odayı Herkese Kilitle", use_container_width=True, key="oda_kilit_btn_bta"):
            st.session_state["oda_kilitli_mi"] = True
            st.rerun()
else:
    if admin_sifre: st.sidebar.error("Hatalı Yönetici Şifresi!")

# --- 🏢 DURUM KONTROLÜ VE İÇERİK ---
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div class="kilit-uyari">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Analiz robotları ve sistem verileri şu an güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
else:
    if st.session_state["oda_kilitli_mi"]:
        st.warning("⚠️ Oda dışarıya kilitli fakat Yönetici olduğunuz için erişim sağladınız.")

    # --- 📊 CANLI PİYASA TAKİP ALANI ---
    st.markdown("### 📊 Canlı Piyasa Takip Ekranı")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown('<div class="piyasa-kutusu"><h4>📉 BIST 100</h4><h2>14.012,42</h2><p style="color:#2ecc71!important; margin:0;">+%0.57</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="piyasa-kutusu"><h4>🟡 Gram Altın</h4><h2>6.857 TL</h2><p style="color:#e74c3c!important; margin:0;">-%1.30</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="piyasa-kutusu"><h4>🪙 Çeyrek Altın</h4><h2>11.246 TL</h2><p style="color:#e74c3c!important; margin:0;">-%0.74</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="piyasa-kutusu"><h4>🥈 Yarım Altın</h4><h2>22.492 TL</h2><p style="color:#e74c3c!important; margin:0;">-%0.74</p></div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="piyasa-kutusu"><h4>👑 Tam Altın</h4><h2>44.984 TL</h2><p style="color:#e74c3c!important; margin:0;">-%0.74</p></div>', unsafe_allow_html=True)

    # Excel Okuma
    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: 
            df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except Exception as e:
            st.error(f"Excel okuma hatası: {e}")
    else:
        st.warning(f"⚠️ '{excel_yolu}' veri dosyası bulunamadı. Lütfen dizini kontrol edin.")

    # Fiyat Motoru
    def hızlı_canli_fiyat_bul(hisse_kodu):
        if not hisse_kodu: return 0.0
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

    # 🎯 %100 SAF HİSSE KODU AYIRICI GÜVENLİ MOTOR
    def saf_hisse_kodu_bul(metin):
        kelimeler = re.findall(r'[A-Z]+', str(metin))
        for kelime in kelimeler:
            if kelime not in ["AL", "SAT", "NAN", "NONE", "SİNYALİ", "SİNYAL"]:
                return kelime
        return ""

    tablo_alsat = []
    tablo_al = []

    if df_kaynak is not None:
        for idx in range(2, len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 22:
                    uv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 20])
                    wv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 22])
                    t_degeri = temiz_metin_al(df_kaynak.iloc[idx, 19])
                    
                    # 🟡 DÖNEMSEL AL SAT SİNYALLERİ ANALİZİ
                    if uv_degeri and uv_degeri not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                        temiz_hisse = saf_hisse_kodu_bul(uv_degeri)
                        if temiz_hisse:
                            canli_fiyat = hızlı_canli_fiyat_bul(temiz_hisse)
                            puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                            bta_puan = puan_bul if puan_bul else (t_degeri if t_degeri else uv_degeri)
                            tablo_alsat.append({"Hisse Kodu 📈": temiz_hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."})
                    
                    # 🟢 BTA SİNYAL MERKEZİ ANALİZİ
                    if wv_degeri and wv_degeri not in ["NAN", "NONE", "AL", "SİNYALİ"]:
