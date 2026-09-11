import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import requests
from io import BytesIO
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# 1. SAYFA AYARLARI VE TASARIM
st.set_page_config(page_title="BTA Merkez", layout="wide")

css_kodu = """
<style>
.stApp { background-color: #0b111e !important; background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; }
.bta-ana-logo { text-align: center; font-family: 'Brush Script MT', cursive, sans-serif !important; font-weight: bold; font-size: 65px; color: #00ffcc; margin: 5px 0 !important; text-shadow: 0 0 10px #00ffcc, 0 0 20px #1e90ff, 0 0 35px #0d9488; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }
.ist-kutu { background-color: #121d33; border: 1px solid #1e3a5f; border-radius: 8px; padding: 10px; text-align: center; color: white; height: 100%; }
</style>
"""
st.markdown(css_kodu, unsafe_allow_html=True)

# 5 saniyede bir sayfayı otomatik tetikler ve yeniler
st_autorefresh(interval=5 * 1000, key="bta_canli_motoru")

# 2. SİZİN GİTHUB HESABINIZDAKİ CANLI EXCEL LİNKİ
excel_github_url = "https://githubusercontent.com"

# 3. ÜST PANEL İSTATİSTİKLERİ
if "ziyaret" not in st.session_state:
    st.session_state["ziyaret"] = 215
    st.session_state["toplam_yildiz"] = 420.0
    st.session_state["oy_sayisi"] = 100

st.markdown('<h1 class="bta-ana-logo">BTA MERKEZ</h1>', unsafe_allow_html=True)

# TRADINGVIEW CANLI GRAFİK
bist_mini_widget = '<div style="width:100%; max-width:450px; margin:auto;"><iframe src="https://tradingview.com" width="100%" height="100" frameborder="0" allowtransparency="true" scrolling="no"></iframe></div>'
components.html(bist_mini_widget, height=105)

mevcut_puan = round(st.session_state["toplam_yildiz"] / st.session_state["oy_sayisi"], 1)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="ist-kutu"><span>👁️ Toplam Ziyaret</span><br><b>{st.session_state["ziyaret"]} Kez</b></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="ist-kutu"><span>⭐ Platform Puanı</span><br><b>{mevcut_puan} / 5</b></div>', unsafe_allow_html=True)
with col3:
    yildiz = st.feedback("stars", key="bta_stars_system")
    if yildiz is not None and f"oy_{yildiz}" not in st.session_state:
        st.session_state["toplam_yildiz"] += (yildiz + 1)
        st.session_state["oy_sayisi"] += 1
        st.session_state[f"oy_{yildiz}"] = True
        st.rerun()

st.write("---")

# 4. GİTHUB'DAN EXCEL OKUMA VE DİNAMİK TETİKLEME MOTORU
tablo_rows = ""
gecmis_rows = ""
try:
    # Önbelleği (cache) kırmak için linkin sonuna anlık zaman ekliyoruz
    response = requests.get(excel_github_url + "?t=" + str(datetime.datetime.now().timestamp()), timeout=5)
    if response.status_code == 200:
        df = pd.read_excel(BytesIO(response.content), sheet_name=0, engine="openpyxl")
        satir_sayisi = 0
        
        for idx in range(len(df)):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", ""]:
                satir_sayisi += 1
                p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                
                # Canlı fiyat çekimi
                c_fiyat = 0.0
                try:
                    c_fiyat = float(yf.Ticker(f"{ha}.IS").history(period="1d")['Close'].iloc[-1])
                except:
                    pass
                
                maliyet = float(alim_c.replace(",", ".")) if alim_c.replace(",", ".").replace(".", "", 1).isdigit() else 0.0
                kz_html = "<span>-</span>"
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    kz_html = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                
                # İlk 10 satırı ana tabloya bas
                if satir_sayisi <= 10:
                    tablo_rows += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_html}</td></tr>'
                
                # Raporlama Defteri satırı oluştur
                bugun_str = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")
                gecmis_rows += f'<tr><td>{bugun_str}</td><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_html}</td></tr>'
except Exception as e:
    pass

# CANLI TABLO GÖSTERİMİ
st.markdown('<p style="font-size:16px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE</p>', unsafe_allow_html=True)
if tablo_rows != "":
    st.markdown(f'<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>{tablo_rows}</table>', unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align:center; padding:30px; color:#b2c3d9; border:1px dashed #1e3a5f; border-radius:10px;">🔍 Excel dosyasından aktif veriler taranıyor...</div>', unsafe_allow_html=True)

# GEÇMİŞ KAYITLAR (NOT DEFTERİ)
st.write("---")
st.markdown('<p style="font-size:16px; font-weight:bold; color:#1E90FF;">📝 GEÇMİŞ ANALİZ KAYIT LAZIM (NOT DEFTERİ)</p>', unsafe_allow_html=True)
if gecmis_rows != "":
    st.markdown(f'<table class="borsa-tablo"><tr><th>KAYIT TARİHİ</th><th>BTA PUANI</th><th>HİSSE</th><th>ALGORİTMİK FİYAT</th><th>ANLIK FİYAT</th><th>O GÜNKÜ KÂR/ZARAR</th></tr>{gecmis_rows}</table>', unsafe_allow_html=True)
else:
    st.info("Henüz kayıt bulunmuyor.")
