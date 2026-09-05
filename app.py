import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# CSS stilleri ve Göz Alıcı Kayan Yazı Animasyonu
st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; margin-top: 30px; margin-bottom: 20px; color: #fca5a5 !important; font-size: 0.95rem; text-align: justify; line-height: 1.5;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.05); border: 1px solid #eab308; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;} .haber-kutusu {background: rgba(255, 255, 255, 0.03); border-left: 4px solid #10b981; padding: 12px; border-radius: 6px; margin-bottom: 10px;} .tv-kutusu {background: rgba(255, 255, 255, 0.03); border-left: 4px solid #3b82f6; padding: 12px; border-radius: 6px; margin-bottom: 10px;}</style>', unsafe_allow_html=True)

# Google Fonts'tan El Yazısı Fontunu Çekiyoruz
st.markdown('<link href="https://googleapis.com" rel="stylesheet">', unsafe_allow_html=True)

# Hafıza Sabitleme
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}


# 🌟 YENİ NESİL LOGO: ÇERÇEVE ETRAFINDA DÖNEN YILDIZLAR VE HAFİF KAYAN/SALLANAN KÜÇÜK ÇERÇEVE
st.markdown("""
<style>
@keyframes neon-isik {
    0% { 
        box-shadow: 0 0 12px #ff007f, inset 0 0 12px #ff007f; 
        border-color: #ff007f; 
    }
    50% { 
        box-shadow: 0 0 20px #00f0ff, inset 0 0 20px #00f0ff; 
        border-color: #00f0ff; 
    }
    100% { 
        box-shadow: 0 0 12px #ff007f, inset 0 0 12px #ff007f; 
        border-color: #ff007f; 
    }
}
/* Çerçevenin kendi ekseninde hafifçe dalgalanarak kayması (Sallanma efekti) */
@keyframes cerceve-kayma {
    0% { transform: translate(0, 0) rotate(0deg); }
    25% { transform: translate(4px, -4px) rotate(1deg); }
    50% { transform: translate(-2px, 4px) rotate(-1deg); }
    75% { transform: translate(-4px, -2px) rotate(0.5deg); }
    100% { transform: translate(0, 0) rotate(0deg); }
}
/* Yıldızların çerçevenin tam etrafında yuvarlak çizerek dönmesi */
@keyframes yildiz-yolculuk {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.logo-merkezleyici {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin: 35px 0;
    height: 170px;
}
.logo-ust-konteyner {
    position: relative;
    width: 140px;  /* İstediğin gibi boyut küçültüldü */
    height: 140px;
    animation: cerceve-kayma 5s infinite ease-in-out; /* Küçülen çerçeveye kayma efekti */
}
.bta-neon-yuvarlak-logo {
    background: transparent !important;
    border: 3.5px solid #ff007f !important;
    border-radius: 50% !important;
    width: 100% !important;
    height: 100% !important;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: neon-isik 2.5s infinite alternate;
    box-sizing: border-box;
    position: absolute;
    top: 0;
    left: 0;
}
.logo-yazi {
    font-size: 2.8rem !important; /* Küçülen çerçeveye tam oturan font boyutu */
    font-weight: bold !important;
    font-family: 'Caveat', cursive, sans-serif !important;
    background: linear-gradient(45deg, #ff007f, #ffaa00, #00f0ff);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    text-shadow: 0 0 10px rgba(255, 0, 127, 0.5);
    margin: 0 !important;
    padding: 0 !important;
}
/* Yıldızların çerçeve dışındaki dönüş yörüngesi */
.yildiz-yorungesi {
    position: absolute;
    top: -15px;
    left: -15px;
    width: 170px;
    height: 170px;
    animation: yildiz-yolculuk 6s infinite linear; /* Dönüş hızı ayarı */
    pointer-events: none;
}
.tek-yildiz {
    position: absolute;
    font-size: 1.4rem !important;
    color: #ffaa00 !important;
    text-shadow: 0 0 8px #ffaa00, 0 0 15px #ff007f;
}
/* Yıldızları çerçevenin etrafına dairesel olarak dağıtıyoruz */
.y1 { top: 0; left: 50%; transform: translateX(-50%); }
.y2 { bottom: 0; left: 50%; transform: translateX(-50%); }
.y3 { top: 50%; left: 0; transform: translateY(-50%); }
.y4 { top: 50%; right: 0; transform: translateY(-50%); }
</style>
<div class="logo-merkezleyici">
    <div class="logo-ust-konteyner">
        <!-- Çerçevenin etrafında fır fır dönen yıldızlar -->
        <div class="yildiz-yorungesi">
            <div class="tek-yildiz y1">✦</div>
            <div class="tek-yildiz y2">✦</div>
            <div class="tek-yildiz y3">✦</div>
            <div class="tek-yildiz y4">✦</div>
        </div>
        <!-- Küçültülmüş ve parlayan yuvarlak çerçeve -->
        <div class="bta-neon-yuvarlak-logo">
            <div class="logo-yazi">BTA</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# 💥 FİYAT VE ALTIN MOTORLARI
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

def canli_altin_fiyatlarini_hesapla():
    try:
        ons_ticker = yf.Ticker("GC=F").history(period="5d")
        usd_ticker = yf.Ticker("USDTRY=X").history(period="5d")
        if not ons_ticker.empty and not usd_ticker.empty:
            ons_fiyat = float(ons_ticker['Close'].iloc[-1])
            usd_fiyat = float(usd_ticker['Close'].iloc[-1])
            if ons_fiyat > 500 and usd_fiyat > 5:
                saf_gram = (ons_fiyat / 31.10347) * usd_fiyat
                ceyrek_fiyat = saf_gram * 1.635
                return saf_gram, ceyrek_fiyat, ceyrek_fiyat * 2, ceyrek_fiyat * 4
    except: pass
    return 3020.50, 4950.00, 9900.00, 19800.00 

# 🟢 VERİLER VE TABLOLAR DOĞRUDAN YÜKLENİR
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px;">🕒 {guncel_an}</div>', unsafe_allow_html=True)

# ALTIN PANELİ
st.markdown("#### 🟡 Canlı Altın Fiyatları")
p_gram, p_ceyrek, p_yarim, p_tam = canli_altin_fiyatlarini_hesapla()
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="piyasa-kutusu">🔱 GRAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_gram:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
c2.markdown(f'<div class="piyasa-kutusu">🪙 ÇEYREK ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_ceyrek:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
c3.markdown(f'<div class="piyasa-kutusu">🥈 YARIM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_yarim:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
c4.markdown(f'<div class="piyasa-kutusu">🥇 TAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_tam:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
st.write("")

# 🔍 ARKA PLANDA EXCEL VERİSİNİ OKUMA
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except: pass

tablo_alsat, tablo_al = [], []
if df_kaynak is not None:
    for idx in range(2, len(df_kaynak)):
        try:
            if len(df_kaynak.columns) > 22:
                uv = str(df_kaynak.iloc[idx, 20]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 20]) else ""
                wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 22]) else ""
                t_deg = str(df_kaynak.iloc[idx, 19]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 19]) else ""
                
                if uv and uv not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                    h_ara = re.findall(r'[A-Z]+', uv)
                    if h_ara:
                        hisse = str(h_ara).strip()
                        cfiy = hızlı_canli_fiyat_bul(hisse)
                        p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv)
                        bta_puan = p_bul if p_bul else t_deg
                        tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
                        
                if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                    h_ara = re.findall(r'[A-Z]+', wv)
                    if h_ara:
                        hisse = str(h_ara).strip()
                        cfiy = hızlı_canli_fiyat_bul(hisse)
