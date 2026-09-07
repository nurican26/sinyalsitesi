import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# =====================================================================
# 1. SAYFA YAPILANDIRMASI VE OTOMATİK YENİLEYİCİ
# =====================================================================
st.set_page_config(page_title="BTA Merkez", layout="wide")

# 10 saniyede bir veya ihtiyacınıza göre yenilenen ana tetikleyici
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici")

# Arka plan rengini sabitlemek için en güvenli arka plan CSS'i
st.markdown('<style>.stApp { background-color: #0f1115 !important; }</style>', unsafe_allow_html=True)

# =====================================================================
# 2. İZOLE EDİLMİŞ ŞEFFAF BTA LOGO VE ANIMASYON PANELİ (GÜVENLİ MİMARİ)
# =====================================================================
logo_html = """
<div style="
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
">
    <!-- Merkezi Şeffaf Cam Panel -->
    <div style="
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 20px 40px;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(255, 255, 255, 0.01);
    ">
        <!-- Sol Taraf: El Yazısı, Gölgeli BTA Logosu -->
        <h1 style="
            font-family: 'Brush Script MT', 'Dancing Script', 'Segoe Script', cursive;
            font-size: 56px;
            font-weight: bold;
            background: linear-gradient(45deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(2px 4px 6px rgba(0, 0, 0, 0.7)) drop-shadow(0 0 12px rgba(0, 210, 255, 0.25));
            margin: 0;
            padding: 0;
            line-height: 1;
        ">BTA</h1>
        
        <!-- Sağ Taraf: Animasyonlu Borsa Kutusu -->
        <div style="
            display: flex;
            flex-direction: column;
            justify-content: center;
            border-left: 2px solid rgba(255, 255, 255, 0.1);
            padding-left: 25px;
        ">
            <div style="
                font-family: 'Courier New', monospace;
                font-size: 17px;
                color: #00e676;
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: bold;
                margin: 0 0 5px 0;
            ">
                BIST100 
                <span style="
                    display: inline-block;
                    animation: pulseArrow 2s infinite ease-in-out;
                ">▲</span> 
                <span style="font-size: 13px; font-weight: normal; color: #aaa;">%1.45</span>
            </div>
            
            <!-- Canlı Akan Grafik Çizgisi -->
            <svg style="width: 100px; height: 25px;" viewBox="0 0 100 30" fill="none" xmlns="http://w3.org">
                <path d="M0,25 Q15,5 30,20 T60,10 T90,5 L100,8" stroke="#00e676" stroke-width="2.5" stroke-linecap="round" 
                      style="stroke-dasharray: 100; stroke-dashoffset: 100; animation: drawLine 3s infinite linear;"/>
            </svg>
        </div>
    </div>
</div>

<style>
@keyframes pulseArrow {
    0%, 100% { transform: translateY(0); opacity: 0.8; }
    50% { transform: translateY(-3px); opacity: 1; filter: drop-shadow(0 0 3px #00e676); }
}
@keyframes drawLine {
    to { stroke-dashoffset: 0; }
}
</style>
"""

# HTML bileşenini güvenli bir şekilde ekrana basıyoruz
components.html(logo_html, height=140)

# --- 15 DAKİKA GECİKMELİ VERİ UYARISI VE YASAL UYARI ---
st.markdown('<p style="color:#ffaa00; font-weight:bold; margin-top:20px;">⚠ Dikkat: Panel üzerindeki borsa verileri borsa kuralları gereği en az 15 dakika gecikmeli olarak yansıtılmaktadır.</p>', unsafe_allow_html=True)
st.markdown('<p style="color:#777; font-size:12px;">⚠ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Belirtilen hisseler algoritma çıktısı olup tavsiye niteliği taşımaz.</p>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

# --- GÜVENLİ SAYAÇ MİMARİSİ ---
if "toplam_sayac" not in st.session_state:
    st.session_state["toplam_sayac"] = 1450
if "gunluk_sayac" not in st.session_state:
    st.session_state["gunluk_sayac"] = 120

# Her sayfa yenilendiğinde sayaçları artır
st.session_state["toplam_sayac"] += 1
st.session_state["gunluk_sayac"] += 1

# Günlük sayacın 24 saatte bir sıfırlanması kontrolü
bugun = datetime.date.today().strftime("%Y-%m-%d")
if "son_giris_tarihi" not in st.session_state:
    st.session_state["son_giris_tarihi"] = bugun

if st.session_state["son_giris_tarihi"] != bugun:
    st.session_state["gunluk_sayac"] = 1
    st.session_state["son_giris_tarihi"] = bugun

# Anlık odadaki kişi sayısı dinamik simülasyonu
anlik_oda = (int(time.time()) % 5) + 3

st.header("📊 BTA ALGORİTMİK HİSSE PANELİ")

# Sayıları TR formatına çevirme fonksiyonu
def formatla_tl(deger):
    try:
        f_deger = float(deger)
        ingiliz_stil = f"{f_deger:,.2f}"
        tr_stil = ingiliz_stil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{tr_stil} TL"
    except:
        return str(deger)

# =====================================================================
# 3. VERİ TABLOLARI VE MOTORU
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
        
        st.markdown('<p style="font-weight:bold; font-size:18px; color:#4facfe;">📈 BTA HİSSELERİ (ÜST PANEL)</p>', unsafe_allow_html=True)
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
        
        st.markdown('<p style="font-weight:bold; font-size:18px; color:#00f2fe;">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</p>', unsafe_allow_html=True)
        if len(tablo_alsat) > 0:
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
        st.write("---")
        
        # --- BIST ANLIK ARAMA MOTORU ---
        st.markdown('<p style="font-weight:bold; font-size:18px; color:#aaa;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist()
            tum_hisseler = [h for h in tum_hisseler if h not in ["HİSSE", "HİSSELER", "NAN", "NONE", ""]]
            tum_hisseler.sort()
            
            if tum_hisseler:
                aranan_hisse = st.selectbox("Analiz etmek istediğiniz hisseyi seçin veya yazın:", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
