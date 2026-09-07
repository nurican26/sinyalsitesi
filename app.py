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

# --- YENİLENEN GERÇEKÇİ ALEVLİ VE BÜYÜTÜLMÜŞ BTA LOGO PANELİ ---
st.markdown('''
<style>
@keyframes rgbText {
    0% { color: #ff3333; }
    25% { color: #33ff33; }
    50% { color: #3333ff; }
    75% { color: #ffff33; }
    100% { color: #ff3333; }
}

@keyframes flicker {
    0%, 100% { transform: scale(1) rotate(-2deg); opacity: 0.9; filter: blur(2px); }
    20% { transform: scale(1.1) rotate(3deg); opacity: 1; filter: blur(1px); }
    40% { transform: scale(0.95) rotate(-1deg); opacity: 0.85; filter: blur(3px); }
    60% { transform: scale(1.15) rotate(2deg); opacity: 0.95; filter: blur(1px); }
    80% { transform: scale(1) rotate(-3deg); opacity: 0.9; filter: blur(2px); }
}

.bta-container {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 20px auto 35px auto;
    width: fit-content;
    position: relative;
    background: #0e1117;
    padding: 15px 70px;
    border-radius: 20px;
    overflow: visible;
}

.bta-logo-custom {
    font-family: 'Brush Script MT', 'cursive', sans-serif;
    font-size: 72px; /* Yazı boyutu ciddi oranda büyütüldü */
    font-weight: bold;
    animation: rgbText 8s infinite linear;
    letter-spacing: 6px;
    position: relative;
    z-index: 10;
    padding: 0 20px;
    text-shadow: 0 0 10px rgba(255,255,255,0.2);
}

/* Gerçekçi CSS Alev Katmanları */
.fire-effect {
    position: absolute;
    width: 60px;
    height: 60px;
    bottom: 25px;
    border-radius: 50% 0 50% 50%;
    transform: rotate(-45deg);
    animation: flicker 0.5s infinite alternate ease-in-out;
    z-index: 1;
}

.fire-left {
    left: 20px;
    background: radial-gradient(circle at 60% 60%, #ffdd00 20%, #ff5500 50%, #ff0000 80%);
    box-shadow: 0 0 30px #ff5500, 0 0 50px #ff0000, -10px -20px 40px rgba(255,68,0,0.5);
}

.fire-right {
    right: 20px;
    background: radial-gradient(circle at 60% 60%, #ffdd00 20%, #ff5500 50%, #ff0000 80%);
    box-shadow: 0 0 30px #ff5500, 0 0 50px #ff0000, 10px -20px 40px rgba(255,68,0,0.5);
}

/* İç çekirdek (Ateşin sıcak merkezi) */
.fire-core {
    position: absolute;
    width: 25px;
    height: 25px;
    background: #ffffff;
    border-radius: 50% 0 50% 50%;
    left: 15px;
    top: 15px;
    box-shadow: 0 0 15px #ffffff, 0 0 25px #ffdd00;
}
</style>

<div class="bta-container">
    <!-- Sol Ateş -->
    <div class="fire-effect fire-left">
        <div class="fire-core"></div>
    </div>
    
    <div class="bta-logo-custom">BTA</div>
    
    <!-- Sağ Ateş -->
    <div class="fire-effect fire-right">
        <div class="fire-core"></div>
    </div>
</div>
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
# 2. ESKİ PANELİNİZİN ORİJİNAL VERİ TABLOLARI VE MOTORU
# ===================================================================== #
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
        
        st.markdown('<p style="font-weight:bold; font-size:18px;">📈 BTA HİSSELERİ (ÜST PANEL)</p>', unsafe_allow_html=True)
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
        
        st.markdown('<p style="font-weight:bold; font-size:18px;">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</p>', unsafe_allow_html=True)
        if len(tablo_alsat) > 0:
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
            
        st.write("---")
        
        # --- BIST ANLIK ARAMA MOTORU ---
        st.markdown('<p style="font-weight:bold; font-size:18px;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper().unique().tolist()
            tum_hisseler = [h for h in tum_hisseler if h not in ["HİSSE", "HİSSELER", "NAN", "NONE", ""]]
            tum_hisseler.sort()
            
            if tum_hisseler:
                aranan_hisse = st.selectbox("Analiz etmek istediğiniz hisseyi seçin veya yazın:", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    with st.spinner(f"{aranan_hisse} verileri çekiliyor..."):
                        try:
                            h_detay = yf.Ticker(f"{aranan_hisse}.IS").history(period="2d")
                            if not h_detay.empty:
                                anlik_fiyat = float(h_detay['Close'].iloc[-1])
                                dunku_kapanis = float(h_detay['Close'].iloc[-2]) if len(h_detay) >= 2 else anlik_fiyat
                                gunluk_degisim = ((anlik_fiyat - dunku_kapanis) / dunku_kapanis) * 100
                                gunun_en_yuksek = float(h_detay['High'].iloc[-1])
                                gunun_en_dusuk = float(h_detay['Low'].iloc[-1])
                                
                                col1, col2, col3 = st.columns(3)
                                col1.metric(label="Fiyat (Gecikmeli) 💥", value=formatla_tl(anlik_fiyat), delta=f"%{gunluk_degisim:+.2f}")
                                col2.metric(label="Gün içi En Yüksek 📈", value=formatla_tl(gunun_en_yuksek))
                                col3.metric(label="Gün içi En Düşük 📉", value=formatla_tl(gunun_en_dusuk))
                            else:
                                st.warning(f"{aranan_hisse} koduna ait veri bulunamadı.")
                        except Exception as e:
                            st.error("Borsa verisi çekilirken bir hata oluştu.")
            else:
