import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. SAYFA YAPILANDIRMASI VE OTOMATİK YENİLEYİCİ
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

# 10 saniyede bir veya ihtiyacınıza göre yenilenen ana tetikleyici
st_autorefresh(interval=10 * 1000, key="bta_merkezi_yenileyici")

# --- HAREKETLİ BTA LOGOSU VE GELİŞMİŞ BÜYÜK YAZI TİPLERİ (CSS) ---
st.markdown('''
<style>
    /* BTA Logo Animasyonu */
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.05); opacity: 1; text-shadow: 0 0 15px rgba(255,215,0,0.8); }
        100% { transform: scale(1); opacity: 0.9; }
    }
    .bta-logo {
        font-size: 55px !important;
        font-weight: 900 !important;
        text-align: center;
        background: linear-gradient(45deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 3s infinite ease-in-out;
        margin-bottom: 20px;
    }
    
    /* Gelişmiş Borsa Tablo Tasarımı ve Büyük Rakamlar */
    .borsa-tablo {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .borsa-tablo th {
        background-color: #1E1E1E;
        color: #AEAEAE;
        padding: 14px;
        text-align: left;
        font-size: 16px;
        border-bottom: 2px solid #333;
    }
    .borsa-tablo td {
        padding: 16px;
        border-bottom: 1px solid #2A2A2A;
        font-size: 20px !important; /* RAKAMLARI BÜYÜTEN AYAR */
        font-weight: 600;
        color: #E0E0E0;
    }
    .borsa-tablo tr:hover {
        background-color: #262626;
    }
    
    /* Hisse Kodları İçin Belirgin Stil */
    .hisse-kod {
        font-size: 22px !important;
        font-weight: bold !important;
        color: #FFFFFF !important;
    }
    
    /* Borsa Renk Kodları */
    .yukselis {
        color: #00E676 !important; /* Parlak Borsa Yeşili */
        font-weight: bold;
    }
    .dusus {
        color: #FF1744 !important; /* Parlak Borsa Kırmızısı */
        font-weight: bold;
    }
    .notr {
        color: #B0BEC5 !important;
        font-weight: bold;
    }
    
    /* Panel Başlıkları */
    .ust-baslik {
        font-size: 26px !important;
        font-weight: bold;
        color: #FFD700;
        border-left: 5px solid #FFD700;
        padding-left: 10px;
        margin-top: 25px;
    }
    .alt-baslik {
        font-size: 26px !important;
        font-weight: bold;
        color: #00E5FF;
        border-left: 5px solid #00E5FF;
        padding-left: 10px;
        margin-top: 25px;
    }
</style>
<div class="bta-logo">BTA</div>
''', unsafe_allow_html=True)

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

# ===================================================================== #
# 2. PANELİNİZİN VERİ TABLOLARI VE MOTORU                               #
# ===================================================================== #
df = None
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
    except Exception as e:
        st.error("Excel verileri yüklenirken bir sorun oluştu.")
else:
    st.error(f"Belirtilen Excel dosyası bulunamadı: {excel_yolu}")

if df is not None:
    # --- ÜST PANEL (BTA HİSSELERİ) ---
    html_bta = '''
    <table class="borsa-tablo">
        <thead>
            <tr>
                <th>BTA PUAN 🔢</th>
                <th>BTA HİSSE 📈</th>
                <th>BTA ALIM 📥</th>
                <th>GÜNCEL FİYAT 💥</th>
                <th>KAR / ZARAR 📊</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    has_bta_data = False
    for idx in range(min(10, len(df))):
        ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
        alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
        puan_d = df.iloc[idx, 3]
        
        if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
            has_bta_data = True
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
            
            # Borsa usulü dinamik ok ve renk sınıfı belirleme
            if maliyet > 0 and c_fiyat > 0:
                oran = ((c_fiyat - maliyet) / maliyet) * 100
                if oran > 0:
                    kz_str = f'<span class="yukselis">▲ %{oran:+.2f}</span>'
                elif oran < 0:
                    kz_str = f'<span class="dusus">▼ %{oran:+.2f}</span>'
                else:
                    kz_str = '<span class="notr">▬ %0,00</span>'
            else:
                kz_str = '<span class="notr">-</span>'
            
            guncel_fiyat_str = formatla_tl(c_fiyat) if c_fiyat > 0 else "Yükleniyor..."
            
            html_bta += f'''
            <tr>
                <td>{p_temiz}</td>
                <td class="hisse-kod">{ha}</td>
                <td>{formatla_tl(maliyet) if maliyet > 0 else alim_c}</td>
                <td>{guncel_fiyat_str}</td>
                <td>{kz_str}</td>
            </tr>
            '''
    
    html_bta += "</tbody></table>"
    
    st.markdown('<p class="ust-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</p>', unsafe_allow_html=True)
    if has_bta_data:
        # Kodun ham metin olarak kalmasını önleyen kritik düzeltme:
        st.markdown(html_bta, unsafe_allow_html=True)
    st.write("")
    
    # --- ALT PANEL (GÜNLÜK AL SAT HİSSELERİ) ---
    html_alsat = '''
    <table class="borsa-tablo">
        <thead>
            <tr>
                <th>GÜNLÜK AL SAT HİSSELERİ ⚡</th>
                <th>GECİKMELİ VERİ 📊</th>
                <th>YÜKSELİŞ ORANI 📈</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    has_alsat_data = False
    for idx in range(min(10, len(df))):
        hb = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
        if hb != "" and hb not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
            has_alsat_data = True
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
            
            # Borsa usulü günlük değişim okları
            if as_fiyat > 0:
                if as_deg > 0:
                    degisim_str = f'<span class="yukselis">▲ %{as_deg:+.2f}</span>'
                elif as_deg < 0:
                    degisim_str = f'<span class="dusus">▼ %{as_deg:+.2f}</span>'
                else:
                    degisim_str = '<span class="notr">▬ %0,00</span>'
            else:
                degisim_str = '<span class="notr">-</span>'
            
            gecikmeli_veri_str = formatla_tl(as_fiyat) if as_fiyat > 0 else "Yükleniyor..."
            
            html_alsat += f'''
            <tr>
                <td class="hisse-kod">{hb}</td>
                <td>{gecikmeli_veri_str}</td>
                <td>{degisim_str}</td>
            </tr>
            '''
            
    html_alsat += "</tbody></table>"
    
    st.markdown('<p class="alt-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</p>', unsafe_allow_html=True)
    if has_alsat_data:
        st.markdown(html_alsat, unsafe_allow_html=True)
        
    st.write("---")
    
    # --- BIST ANLIK ARAMA MOTORU ---
    st.markdown('<p class="ust-baslik">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
    
    if len(df.columns) >= 5:
        tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist()
        tum_hisseler = [h for h in tum_hisseler if h not in ["HİSSE", "HİSSELER", "NAN", "NONE", ""]]
        tum_hisseler.sort()
        
        if tum_hisseler:
            aranan_hisse = st.selectbox("Analiz etmek istediğiniz hisseyi seçin veya yazın:", ["Seçiniz..."] + tum_hisseler)
            
