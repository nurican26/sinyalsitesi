import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# CSS Güncellemesi: Şifre alanları kaldırıldı, BTA yazısı el yazısı, ortalanmış ve parlak neon yapıldı
st.markdown('''
<style>
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
.spk-kutusu {
    background-color: rgba(220, 38, 38, 0.1); 
    border: 1px solid #dc2626; 
    padding: 8px; 
    border-radius: 6px; 
    margin-top: 25px; 
    margin-bottom: 10px; 
    color: #fca5a5 !important; 
    font-size: 0.8rem; 
    text-align: justify;
} 

/* 🌟 YENİ ORTALANMIŞ, EL YAZISI VE IŞIKLI BTA LOGO ALANI */
.bta-logo-konteyner {
    display: flex; 
    justify-content: center; 
    align-items: center; 
    margin-top: 20px; 
    margin-bottom: 35px;
    width: 100%;
} 
.bta-logo-yazi {
    font-family: "Brush Script MT", "Comic Sans MS", cursive, sans-serif !important; 
    font-size: 4.5rem !important; 
    font-weight: bold !important; 
    color: #ffffff !important;
    text-align: center;
    /* Parlak Işık ve Gölgelendirme Efekti (Neon) */
    text-shadow: 
        0 0 5px #fff,
        0 0 10px #fff,
        0 0 20px #10b981,
        0 0 30px #10b981,
        0 0 40px #10b981,
        0 0 55px #10b981;
    animation: bta-parlama 2s ease-in-out infinite alternate;
}

@keyframes bta-parlama {
  from {
    text-shadow: 0 0 10px #fff, 0 0 20px #10b981, 0 0 30px #10b981;
  }
  to {
    text-shadow: 0 0 15px #fff, 0 0 25px #10b981, 0 0 40px #10b981, 0 0 55px #10b981;
  }
}

div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
    font-size: 1.25rem !important; 
    font-weight: bold !important; 
    color: #ffffff !important;
}
</style>
''', unsafe_allow_html=True)

# Hafıza Kontrolleri
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

for k in ["kisitli_liste", "ziyaret_sayaci", "topham_oy_sayisi", "topham_yildiz_puani", "is_counted"]:
    if k not in st.session_state: st.session_state[k] = 0 if "sayaci" in k or "sayisi" in k or "puani" in k else ([] if k == "kisitli_liste" else False)

if not st.session_state["is_counted"]:
    st.session_state["ziyaret_sayaci"] += 1
    st.session_state["is_counted"] = True

# 🌟 YENİ ORTALANMIŞ VE PARLAK BTA BAŞLIĞI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo-yazi">BTA</div></div>', unsafe_allow_html=True)

# 💥 CANLI FİYAT MOTORU
def hızlı_canli_fiyat_bul(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - saved_time < 300:  # 5 Dakika Önbellek (Cache)
            return saved_price
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            fiyat = float(data['Close'].iloc[-1])
            st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
            return fiyat
    except: pass
    return 0.0

# 🟢 ŞİFRESİZ DOĞRUDAN ERİŞİM (Eski şifre blokları tamamen kaldırıldı)
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px; text-align: center;">⭐ <b>Puan:</b> {puan:.2f} | 🔥 <b>Oy:</b> {st.session_state["topham_oy_sayisi"]} | 🚪 <b>Giriş:</b> {st.session_state["ziyaret_sayaci"]} | 🕒 {guncel_an}</div>', unsafe_allow_html=True)

df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except: 
        st.error("Excel dosyası okunurken hata oluştu. Lütfen formatı kontrol edin.")

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
                        hisse = str(h_ara[0])
                        cfiy = hızlı_canli_fiyat_bul(hisse)
                        p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv)
                        bta_puan = p_bul[0] if p_bul else t_deg
                        tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
                        
                if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                    h_ara = re.findall(r'[A-Z]+', wv)
                    if h_ara:
                        hisse = str(h_ara[0])
                        cfiy = hızlı_canli_fiyat_bul(hisse)
                        p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', wv)
                        bta_puan = p_bul[0] if p_bul else t_deg
                        if hisse not in st.session_state["ozel_takip_kutusu"] and cfiy > 0:
                            st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                        tablo_al.append({"Hisse Kodu 🚀": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
        except: pass

st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
if tablo_alsat: 
    st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
else: 
    st.write("🔒 Aktif AL SAT sinyali taranıyor...")

# Kodun kalan (Al sinyalleri tablosu, alt kısım ve grafik) bölümlerini bu yapının altına ekleyebilirsiniz.
