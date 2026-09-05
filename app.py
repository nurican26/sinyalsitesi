import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# CSS Tasarımı - Sağdan Sola Yavaşça Akan Gökkuşağı Neon BTA Logosu ve Canlı Ekonomi Kartları
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
    /* Canlı Ekonomi Kart Tasarımları */
    .ekonomi-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.1);
        margin-bottom: 15px;
    }
    .ekonomi-baslik-kart {
        color: #00f2fe !important;
        font-weight: bold;
        font-size: 0.9rem;
        margin-bottom: 5px;
        letter-spacing: 1px;
    }
    .ekonomi-fiyat-kart {
        color: #ffffff !important;
        font-size: 1.35rem;
        font-weight: bold;
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
</style>
""", unsafe_allow_html=True)

# 🔑 PARAMETRELER
YONETICI_SIFRESI = "bta2026"

# Hafıza Kontrolleri
if "oda_kilitli_mi" not in st.session_state: st.session_state["oda_kilitli_mi"] = False
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

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

# --- 🏢 DURUM KONTROLÜ VE İÇERİK ---
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div class="kilit-uyari">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Analiz robotları ve sistem verileri şu an güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
else:
    if st.session_state["oda_kilitli_mi"]:
        st.warning("⚠️ Oda dışarıya kilitli fakat Yönetici olduğunuz için erişim sağladınız.")

    # --- 📊 CANLI EKONOMİ PANELİ (HER DAİM SABİT VE PARLAK) ---
    try:
        bist_veri = yf.Ticker("XU100.IS").history(period="1d")['Close'].iloc[-1]
        usd_veri = yf.Ticker("TRY=X").history(period="1d")['Close'].iloc[-1]
        eur_veri = yf.Ticker("EURTRY=X").history(period="1d")['Close'].iloc[-1]
        ons_gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        gram_altin_veri = (ons_gold / 31.1034768) * usd_veri
        
        col_b, col_u, col_e, col_a = st.columns(4)
        with col_b: st.markdown(f'<div class="ekonomi-box"><div class="ekonomi-baslik-kart">📈 BIST 100</div><div class="ekonomi-fiyat-kart">{bist_veri:,.2f}</div></div>', unsafe_allow_html=True)
        with col_u: st.markdown(f'<div class="ekonomi-box"><div class="ekonomi-baslik-kart">💵 DOLAR / TL</div><div class="ekonomi-fiyat-kart">{usd_veri:.4f} TL</div></div>', unsafe_allow_html=True)
        with col_e: st.markdown(f'<div class="ekonomi-box"><div class="ekonomi-baslik-kart">💶 EURO / TL</div><div class="ekonomi-fiyat-kart">{eur_veri:.4f} TL</div></div>', unsafe_allow_html=True)
        with col_a: st.markdown(f'<div class="ekonomi-box"><div class="ekonomi-baslik-kart">🟡 GRAM ALTIN</div><div class="ekonomi-fiyat-kart">{gram_altin_veri:.2f} TL</div></div>', unsafe_allow_html=True)
    except:
        pass

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
        temiz_kod = str(hisse_kodu).replace("[", "").replace("]", "").replace("'", "").replace('"', '').replace(" ", "").strip()
        if temiz_kod in st.session_state["fiyat_hafizasi"]:
            saved_time, saved_price = st.session_state["fiyat_hafizasi"][temiz_kod]
            if time.time() - saved_time < 300: return saved_price
        try:
            ticker = yf.Ticker(f"{temiz_kod}.IS")
            data = ticker.history(period="1d")
            if not data.empty and not pd.isna(data['Close'].iloc[-1]):
                fiyat = float(data['Close'].iloc[-1])
                st.session_state["fiyat_hafizasi"][temiz_kod] = (time.time(), fiyat)
                return fiyat
        except: pass
        return 0.0

    def temiz_metin_al(val):
        if pd.isna(val): return ""
        return str(val).strip().upper()

    tablo_alsat = []
    tablo_al = []

    if df_kaynak is not None:
        for idx in range(2, len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 22:
                    uv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 20])
                    wv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 22])
                    t_degeri = temiz_metin_al(df_kaynak.iloc[idx, 19])
                    
                    if uv_degeri and uv_degeri not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                        hisse_ara = re.findall(r'[A-Z]+', uv_degeri)
                        if hisse_ara:
                            hisse = str(hisse_ara).strip()
                            gosterim_ismi = hisse.replace("[", "").replace("]", "").replace("'", "").replace('"', '').replace(" ", "")
                            canli_fiyat = hızlı_canli_fiyat_bul(gosterim_ismi)
                            puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                            bta_puan = puan_bul if puan_bul else (t_degeri if t_degeri else uv_degeri)
                            tablo_alsat.append({"Hisse Kodu 📈": gosterim_ismi, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."})
                    
                    if wv_degeri and wv_degeri not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                        hisse_ara = re.findall(r'[A-Z]+', wv_degeri)
                        if hisse_ara:
                            hisse = str(hisse_ara).strip()
