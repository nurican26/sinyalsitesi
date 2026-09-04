import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Yenilenen Işıklı/Gölgeli Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

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

/* ORTALANMIŞ, EL YAZISI, PARLAK NEON IŞIKLI VE ALTI DERİN GÖLGELİ BTA */
.bta-logo-konteyner {
    display: flex; 
    justify-content: center; 
    align-items: center; 
    margin-top: 25px; 
    margin-bottom: 35px;
    width: 100%;
    background: transparent !important;
} 
.bta-logo {
    font-family: "Brush Script MT", "Comic Sans MS", cursive, sans-serif !important; 
    font-weight: bold !important; 
    font-size: 5.5rem !important; 
    color: #00f0ff !important; 
    display: inline-block; 
    text-align: center; 
    letter-spacing: 3px;
    position: relative;
    text-shadow: 
        0 0 10px #00f0ff,
        0 0 20px #00f0ff,
        0 0 30px #00f0ff,
        4px 10px 12px rgba(0, 0, 0, 0.9);
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

for k in ["kisitli_liste", "ziyaret_sayaci"]:
    if k not in st.session_state: st.session_state[k] = 0 if k == "ziyaret_sayaci" else []

# Giriş sayısı sayacı
st.session_state["ziyaret_sayaci"] += 1

# BTA LOGO ALANI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# CANLI FİYAT MOTORU
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

# GİRİŞ SAYISI GÖSTERGESİ
st.markdown(f'<div style="font-size: 1rem; color: #a5f3fc; margin-bottom: 20px; font-weight: bold; text-align: center;">🚪 Giriş Sayısı: {st.session_state["ziyaret_sayaci"]}</div>', unsafe_allow_html=True)

df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except: 
        pass

tablo_alsat, tablo_al = [], []
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")

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
        except: 
            pass

# 🟡 TABLO 1: DÖNEMSEL AL SAT SİNYALLERİ
st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
if tablo_alsat: 
    st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
else: 
    st.write("🔒 Aktif AL SAT sinyali taranıyor...")

# 🟢 TABLO 2: BTA SİNYAL MERKEZİ
st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
if tablo_al: 
    st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
else: 
    st.write("🔒 Aktif AL sinyali taranıyor...")
