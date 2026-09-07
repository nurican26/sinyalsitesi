import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
from streamlit_autorefresh import st_autorefresh

# ===================================================================== #
# 1. SAYFA YAPILANDIRMASI VE BORSA TASARIMI (CSS)
# ===================================================================== #
st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
/* Deep Gece Mavisi Borsa Arka Planı ve Grafik Çizgileri */
.stApp {
    background-color: #0b111e !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%),
        linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px !important;
}

/* Veri Tabloları, Kartlar ve Form Alanları */
div[data-testid="stMetric"], div[data-testid="stForm"] {
    background-color: #121d33 !important;
    border: 1px solid #1e2e4d !important;
    border-radius: 12px !important;
    padding: 15px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
}

/* Giriş Kutuları ve Seçim Alanları */
input, textarea, select, div[data-baseweb="select"] {
    background-color: #090f1a !important;
    color: #00ffcc !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
}

/* Buton Tasarımları */
.stButton>button {
    background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important;
    color: #ffffff !important;
    border: 1px solid #00ffcc !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 10px rgba(0, 255, 204, 0.2) !important;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #0d9488 0%, #00ffcc 100%) !important;
    color: #0b111e !important;
    box-shadow: 0 0 20px rgba(0, 255, 204, 0.6) !important;
    transform: scale(1.02);
}

/* Tablo Verilerinin Telefonda Büyük ve Net Görünmesi İçin Ek CSS */
.borsa-tablo {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 18px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #121d33;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}
.borsa-tablo th {
    background-color: #1e2e4d;
    color: #00ffcc;
    text-align: left;
    padding: 14px 18px;
    font-weight: 600;
    font-size: 16px;
    border-bottom: 2px solid #1e3a5f;
}
.borsa-tablo td {
    padding: 14px 18px;
    color: #ffffff;
    border-bottom: 1px solid #1e2e4d;
    font-weight: bold;
}
.borsa-tablo tr:last-child td {
    border-bottom: none;
}
.pozitif-degisim {
    color: #00ff66 !important;
    font-weight: bold;
    font-size: 19px;
}
.negatif-degisim {
    color: #ff3344 !important;
    font-weight: bold;
    font-size: 19px;
}
</style>
''', unsafe_allow_html=True)

# Sohbeti ve verileri 5 saniyede bir otomatik eşitler
st_autorefresh(interval=5 * 1000, key="bta_sohbet_anlik_senkronize")

# --- IŞIKLI, GÖLGELİ VE KAYAN BTA LOGOSU ---
st.markdown('''
<style>
@keyframes neon-glow {
    0%, 100% { text-shadow: 0 0 10px #ff0055, 0 0 20px #ff0055, 0 0 40px #ff0055; }
    50% { text-shadow: 0 0 20px #00ffcc, 0 0 40px #00ffcc, 0 0 60px #00ffcc; }
}
.neon-marquee {
    font-size: 45px;
    font-weight: bold;
    font-family: 'Arial Black', sans-serif;
    color: #ffffff;
    animation: neon-glow 3s infinite alternate;
    white-space: nowrap;
    margin: 10px 0;
}
</style>
<marquee scrollamount="8" behavior="scroll" direction="left">
    <span class="neon-marquee">✨ BTA ALGORİTMİK İŞLEM MERKEZİ ✨</span>
</marquee>
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

def formatla_tl(deger):
    try:
        f_deger = float(deger)
        ingiliz_stil = f"{f_deger:,.2f}"
        tr_stil = ingiliz_stil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{tr_stil} TL"
    except:
        return str(deger)

# ===================================================================== #
# 2. ORİJİNAL VERİ TABLOLARI VE MOTORU
# ===================================================================== #
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUAN 🔢</th><th>BTA HİSSE 📈</th><th>BTA ALIM 📥</th><th>GÜNCEL FİYAT 💥</th><th>KAR / ZARAR 📊</th></tr>'
        veri_var_mi = False
        
        for idx in range(min(10, len(df))):
            try:
                ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
                alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                puan_d = df.iloc[idx, 3]
                
                if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                    veri_var_mi = True
                    p_temiz = f"{float(puan_d):.2f}" if hasattr(puan_d, '__float__') or isinstance(puan_d, (int, float)) else str(puan_d).strip()
                    
                    c_fiyat = 0.0
                    try:
                        h_bta = yf.Ticker(f"{ha}.IS")
                        h_veri = h_bta.history(period="1d", timeout=2)
                        c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                    except:
                        c_fiyat = 0.0
                    
                    try:
                        maliyet = float(alim_c.replace(",", "."))
                    except:
                        maliyet = 0.0
                    
                    if maliyet > 0 and c_fiyat > 0:
                        degisim_oran = ((c_fiyat - maliyet) / maliyet) * 100
                        if degisim_oran >= 0:
                            kz_str = f'<span class="pozitif-degisim">▲ %{degisim_oran:.2f}</span>'
                        else:
                            kz_str = f'<span class="negatif-degisim">▼ %{degisim_oran:.2f}</span>'
                    else:
                        kz_str = "<span>-</span>"
                    
                    fiyat_gosterim = formatla_tl(c_fiyat) if c_fiyat > 0 else "Bağlanıyor..."
                    maliyet_gosterim = formatla_tl(maliyet) if maliyet > 0 else alim_c
                    
                    tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet_gosterim}</td><td>{fiyat_gosterim}</td><td>{kz_str}</td></tr>'
            except:
                continue
        
        tablo_html += '</table>'
        
        st.markdown('<p style="font-size:20px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi:
            st.markdown(tablo_html, unsafe_allow_html=True)
        
        st.write("")

        # DONMALARI ÖNLEMEK İÇİN ASLA BLOKE OLMAYAN GÜVENLİ BORSA ARAMA MOTORU
        st.markdown('<p style="font-size:20px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist()
            tum_hisseler = [h for h in tum_hisseler if h not in ["HİSSE", "HİSSELER", "NAN", "NONE", ""]]
            tum_hisseler.sort()
            
            if len(tum_hisseler) > 0:
                aranan_hisse = st.selectbox("Analiz etmek istediğiniz hisseyi seçin ", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    # Alt panellerin donmasını önlemek için tüm arama işlemi koruyucu zırh içine alındı
                    try:
                        h_detay = yf.Ticker(f"{aranan_hisse}.IS")
                        h_detay_veri = h_detay.history(period="2d", timeout=2) # En fazla 2 saniye bekler, takılmaz!
                        if len(h_detay_veri) >= 2:
                            anlik_fiyat = float(h_detay_veri['Close'].iloc[-1])
                            dunku_kapanis = float(h_detay_veri['Close'].iloc[-2])
                            gunluk_degisim = ((anlik_fiyat - dunku_kapanis) / dunku_kapanis) * 100
                            gunun_en_yuksek = float(h_detay_veri['High'].iloc[-1])
                            gunun_en_dusuk = float(h_detay_veri['Low'].iloc[-1])
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric(label="Fiyat (Gecikmeli) 💥", value=formatla_tl(anlik_fiyat), delta=f"%{gunluk_degisim:+.2f}")
                            col2.metric(label="Gün içi En Yüksek 📈", value=formatla_tl(gunun_en_yuksek))
                            col3.metric(label="Gün içi En Düşük 📉", value=formatla_tl(gunun_en_dusuk))
                    except:
                        st.warning("Seçilen hissenin anlık borsa verisine şu an ulaşılamıyor, lütfen az sonra tekrar deneyin.")
            else:
                st.warning("Excel dosyasının E sütununda geçerli bir hisse listesi bulunamadı.")
        else:
            st.error("Excel dosyasında E sütunu bulunamadı!")
            
    except:
