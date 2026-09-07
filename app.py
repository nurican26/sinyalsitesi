import streamlit as st 
import pandas as pd 
import datetime 
import yfinance as yf 
import os 
import time 
import requests 
from bs4 import BeautifulSoup 
from streamlit_autorefresh import st_autorefresh 

# ===================================================================== 
# 1. SAYFA YAPILANDIRMASI VE OTOMATİK YENİLEYİCİ (Mevcut yapınız korundu) 
# ===================================================================== 
st.set_page_config(page_title="BTA Merkez", layout="wide") 

# --- 🎨 KIRMIZIDAN YEŞİLE KADEMELİ ARKA PANEL VE STYLES ---
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #7a0000 0%, #003d19 100%) !important;
            background-attachment: fixed !important;
        }
        header, [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        /* Yazıların koyu arka planda tamamen okunabilir kalması için */
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #ffffff !important;
        }
        
        /* Canlı Üst Finans Paneli (Ticker) Tasarımı */
        .live-ticker-container {
            background: rgba(0, 0, 0, 0.65);
            border-bottom: 2px solid #ffdd57;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            text-align: center;
        }
        .ticker-item {
            padding: 5px 15px;
            font-family: 'Courier New', Courier, monospace;
        }
        .ticker-label {
            font-size: 13px;
            color: #ccc;
            font-weight: bold;
            display: block;
            margin-bottom: 3px;
        }
        .ticker-value {
            font-size: 18px;
            color: #ffdd57;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# 10 saniyede bir veya ihtiyacınıza göre yenilenen ana tetikleyici 
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici") 

# ===================================================================== 
# CANLI ÜST VERİ PANELİ MOTORU (BIST 100 & ALTIN FİYATLARI)
# ===================================================================== 
def formatla_tr_stil(deger):
    try:
        f_deger = float(deger)
        ingiliz_stil = f"{f_deger:,.2f}"
        tr_stil = ingiliz_stil.replace(",", "X").replace(".", ",").replace("X", ".")
        return tr_stil
    except:
        return str(deger)

# Canlı verilerin Yahoo Finance üzerinden çekilmesi
try:
    bist_data = yf.Ticker("^XU100").history(period="1d")
    bist_100 = bist_data['Close'].iloc[-1] if not bist_data.empty else 14109.75
    
    ons_data = yf.Ticker("GC=F").history(period="1d")
    ons_fiyat = ons_data['Close'].iloc[-1] if not ons_data.empty else 2500.0
    
    try:
        usd_data = yf.Ticker("TRY=X").history(period="1d")
        usd_try = usd_data['Close'].iloc[-1] if not usd_data.empty else 34.20
    except:
        usd_try = 34.20
        
    gram_altin = (ons_fiyat / 31.10347) * usd_try
    ceyrek_altin = gram_altin * 1.635
    yarim_altin = gram_altin * 3.27
    tam_altin = gram_altin * 6.54
except:
    bist_100 = 14109.75
    gram_altin = 6839.47
    ceyrek_altin = 11184.17
    yarim_altin = 22368.34
    tam_altin = 44459.00

st.markdown(f"""
    <div class="live-ticker-container">
        <div class="ticker-item">
            <span class="ticker-label">📊 BIST 100</span>
            <span class="ticker-value">{formatla_tr_stil(bist_100)}</span>
        </div>
        <div class="ticker-item">
            <span class="ticker-label">🟡 GRAM ALTIN</span>
            <span class="ticker-value">{formatla_tr_stil(gram_altin)} TL</span>
        </div>
        <div class="ticker-item">
            <span class="ticker-label">🪙 ÇEYREK ALTIN</span>
            <span class="ticker-value">{formatla_tr_stil(ceyrek_altin)} TL</span>
        </div>
        <div class="ticker-item">
            <span class="ticker-label">🥈 YARIM ALTIN</span>
            <span class="ticker-value">{formatla_tr_stil(yarim_altin)} TL</span>
        </div>
        <div class="ticker-item">
            <span class="ticker-label">👑 TAM ALTIN</span>
            <span class="ticker-value">{formatla_tr_stil(tam_altin)} TL</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- HAREKETLİ BTA LOGOSU VE STYLES --- 
st.markdown('''
<div style="font-size:42px; font-weight:bold; text-align:center; color:#ffdd57; 
animation: pulse 2s infinite; margin-bottom:10px;">
BTA
</div>
<style>
@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}
</style>
''', unsafe_allow_html=True) 

excel_yolu = "nurican.xls.xlsm" 

# --- GÜVENLİ SAYAÇ MİMARİSİ --- 
if "toplam_sayac" not in st.session_state: 
    st.session_state["toplam_sayac"] = 1450 
if "gunluk_sayac" not in st.session_state: 
    st.session_state["gunluk_sayac"] = 120 

st.session_state["toplam_sayac"] += 1 
st.session_state["gunluk_sayac"] += 1 

bugun = datetime.date.today().strftime("%Y-%m-%d") 
if "son_giris_tarihi" not in st.session_state: 
    st.session_state["son_giris_tarihi"] = bugun 
if st.session_state["son_giris_tarihi"] != bugun: 
    st.session_state["gunluk_sayac"] = 1 
    st.session_state["son_giris_tarihi"] = bugun 

anlik_oda = (int(time.time()) % 5) + 3 
st.header("📊 BTA ALGORİTMİK HİSSE PANELİ") 

def formatla_tl(deger): 
    try: 
        f_deger = float(deger) 
        ingiliz_stil = f"{f_deger:,.2f}" 
        tr_stil = ingiliz_stil.replace(",", "X").replace(".", ",").replace("X", ".") 
        return f"{tr_stil} TL" 
    except: 
        return str(deger) 

# ===================================================================== 
# 2. ESKİ PANELİNİZİN ORİJİNAL VERİ TABLOLARI VE MOTORU 
# ===================================================================== 
if os.path.exists(excel_yolu): 
    try: 
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl") 
        
        # --- ÜST PANEL (BTA HİSSELERİ) --- 
        tablo_bta = [] 
        for idx in range(min(10, len(df))): 
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else "" 
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else "" 
            puan_d = df.iloc[idx, 3] 
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]: 
                p_temiz = f"{float(puan_d):.2f}" if hasattr(puan_d, '__float__') or isinstance(puan_d, (int, float)) else str(puan_d).strip() 
                c_fiyat = 0.0 
                try: 
                    h_bta = yf.Ticker(f"{ha}.IS").history(period="1d") 
                    if not h_bta.empty: 
                        c_fiyat = float(h_bta['Close'].iloc[-1]) 
                except: 
                    pass 
                try: 
                    maliyet = float(alim_c.replace(",", ".")) 
                except: 
                    maliyet = 0.0 
                kz_str = f"%{((c_fiyat - maliyet) / maliyet) * 100:+.2f}" if maliyet > 0 and c_fiyat > 0 else "-" 
                tablo_bta.append({ 
                    "BTA PUAN 🔢": p_temiz, 
                    "BTA HİSSE 📈": ha, 
                    "BTA ALIM 📥": formatla_tl(maliyet) if maliyet > 0 else alim_c, 
                    "GÜNCEL FİYAT 💥": formatla_tl(c_fiyat) if c_fiyat > 0 else "Yükleniyor...", 
                    "KAR / ZARAR 📊": kz_str 
                }) 
        st.markdown('<p style="font-size:32px; font-weight:bold; text-align:left; margin:10px 0;">📈 BTA HİSSELERİ (ÜST PANEL)</p>', unsafe_allow_html=True) 
        if len(tablo_bta) > 0: 
            st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True) 
        st.write("") 

        # --- ALT PANEL (GÜNLÜK AL SAT HİSSELERİ) --- 
        tablo_alsat = [] 
        for idx in range(min(10, len(df))): 
            hb = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else "" 
            if hb != "" and hb not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]: 
                as_fiyat = 0.0 
                as_deg = 0.0 
                try: 
                    h_as = yf.Ticker(f"{hb}.IS").history(period="2d") 
                    if not h_as.empty: 
                        as_fiyat = float(h_as['Close'].iloc[-1]) 
                        as_prev = float(h_as['Close'].iloc[-2]) if len(h_as) >= 2 else as_fiyat 
                        as_deg = ((as_fiyat - as_prev) / as_prev) * 100 
                except: 
                    pass 
                tablo_alsat.append({ 
                    "GÜNLÜK AL SAT HİSSELERİ ⚡": hb, 
                    "GECİKMELİ VERİ 📊": formatla_tl(as_fiyat) if as_fiyat > 0 else "Yükleniyor...", 
                    "YÜKSELİŞ ORANI 📈": f"%{as_deg:+.2f}" if as_fiyat > 0 else "-" 
                }) 
        st.markdown('<p style="font-size:32px; font-weight:bold; text-align:left; margin:10px 0;">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</p>', unsafe_allow_html=True) 
        if len(tablo_alsat) > 0: 
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True) 
        st.write("---") 

        # --- BIST ANLIK ARAMA MOTORU --- 
        st.markdown('<p style="font-size:32px; font-weight:bold; text-align:left; margin:10px 0;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True) 
        if len(df.columns) >= 5: 
            tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist() 
            tum_hisseler = [h for h in tum_hisseler if h not in ["HİSSE", "HİSSELER", "NAN", "NONE", ""]] 
            tum_hisseler.sort() 
            
            aranan_hisse = st.selectbox("Analiz etmek istediğiniz hisseyi seçin veya yazın:", ["Seçiniz..."] + tum_hisseler) if len(tum_hisseler) > 0 else "Seçiniz..." 
            
