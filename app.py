import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="BTA Merkez", layout="wide")

st.markdown('''
<style>
.stApp { background-color: #0b111e !important; background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; }
div[data-testid="stMetric"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }
input, textarea, select { background-color: #090f1a !important; color: #00ffcc !important; border: 1px solid #1e3a5f !important; border-radius: 6px !important; }
.stButton>button { background: linear-gradient(135deg, #111827 0%, #0d9488 100%) !important; color: #fff !important; border: 1px solid #00ffcc !important; border-radius: 6px !important; font-weight: bold !important; font-size: 14px !important; }
.borsa-tablo { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.borsa-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.borsa-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }

/* Kayan Yazı (Marquee) Tasarımı */
.kayan-bilgi-bandi {
    background: linear-gradient(90deg, #121d33 0%, #1e2e4d 50%, #121d33 100%);
    border-bottom: 2px solid #1e3a5f;
    padding: 8px 0;
    margin-bottom: 15px;
    font-family: sans-serif;
    font-size: 16px;
    font-weight: bold;
}
.pozitif { color: #00ff66; }
.negatif { color: #ff3344; }
.notr { color: #ffffff; }
</style>
''', unsafe_allow_html=True)

st_autorefresh(interval=5 * 1000, key="bta_anlik_senkronize_motoru")

excel_yolu = "nurican.xls.xlsm"
db_notlar = "bta_hisse_notlari_db.csv"

if not os.path.exists(db_notlar):
    pd.DataFrame(columns=["id", "tarih", "hisse", "not", "hedef_fiyat"]).to_csv(db_notlar, index=False)

# Değişim yönlerini hesaplamak için yardımcı fonksiyon
def fiyat_ve_yon_getir(ticker_kod):
    try:
        ticker = yf.Ticker(ticker_kod)
        hist = ticker.history(period="2d", timeout=2)
        if len(hist) >= 2:
            guncel = float(hist['Close'].iloc[-1])
            onceki = float(hist['Close'].iloc[-2])
            degisim = guncel - onceki
            if degisim > 0:
                return guncel, '<span class="pozitif">🟢 ▲</span>'
            elif degisim < 0:
                return guncel, '<span class="negatif">🔴 ▼</span>'
        elif len(hist) == 1:
            return float(hist['Close'].iloc[-1]), '<span class="notr">▪</span>'
    except:
        pass
    return 0.0, '<span class="notr">▪</span>'

# Canlı verileri ve yön oklarını çekiyoruz
bist_f, bist_ok = fiyat_ve_yon_getir("XU100.IS")
ons_f, ons_ok = fiyat_ve_yon_getir("GC=F")
usd_f, usd_ok = fiyat_ve_yon_getir("TRY=X")
eur_f, eur_ok = fiyat_ve_yon_getir("EURTRY=X")

# Gram altın hesaplaması ve yön tayini
gram_f = (ons_f / 31.1034768) * usd_f if usd_f > 0 else 0.0
gram_ok = usd_ok if (usd_ok == ons_ok) else (usd_ok if usd_ok != '<span class="notr">▪</span>' else ons_ok)

# Üst Kayan Yazı HTML İçeriği
marquee_html = f'''
<div class="kayan-bilgi-bandi">
    <marquee behavior="scroll" direction="left" scrollamount="6">
        <span>BIST 100: {bist_f:,.2f} {bist_ok}</span> &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;
        <span>GRAM ALTIN: {gram_f:,.2f} TL {gram_ok}</span> &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;
        <span>ÇEYREK ALTIN: {gram_f * 1.63:,.2f} TL {gram_ok}</span> &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;
        <span>YARIM ALTIN: {gram_f * 3.26:,.2f} TL {gram_ok}</span> &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;
        <span>USD/TRY: {usd_f:,.2f} TL {usd_ok}</span> &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;
        <span>EUR/TRY: {eur_f:,.2f} TL {eur_ok}</span>
    </marquee>
</div>
'''
st.markdown(marquee_html, unsafe_allow_html=True)

# Başlık kayan yazının altına taşındı
st.markdown('<h1 style="text-align:center; color:#00ffcc; font-family:\'Brush Script MT\', cursive, sans-serif; font-size:42px; margin-top:5px; margin-bottom:5px;">BTA</h1>', unsafe_allow_html=True)

st.write("---")
tum_hisseler = [] 
veri_var_mi = False

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        tablo_html = '<table class="borsa-tablo"><tr><th>BTA PUANI</th><th>HİSSE</th><th> ALGORİTMİK FİYATI</th><th>FİYAT</th><th>K/Z</th></tr>'
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                veri_var_mi = True
                p_temiz = f"{float(puan_d):.2f}" if isinstance(puan_d, (int, float)) else str(puan_d).strip()
                c_fiyat = 0.0
                try:
                    h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                    c_fiyat = float(h_veri['Close'].iloc[-1]) if len(h_veri) > 0 else 0.0
                except:
                    pass
                alim_c_temiz = alim_c.replace(",", ".")
                maliyet = float(alim_c_temiz) if alim_c_temiz.replace(".", "", 1).isdigit() else 0.0
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>' if or_dg >= 0 else f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                else:
                    kz_str = "<span>-</span>"
                tablo_html += f'<tr><td>{p_temiz}</td><td>{ha}</td><td>{maliyet:,.2f} TL</td><td>{c_fiyat:,.2f} TL</td><td>{kz_str}</td></tr>'
        tablo_html += '</table>'
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        if veri_var_mi: 
            st.markdown(tablo_html, unsafe_allow_html=True)
        if len(df.columns) >= 5:
            ham_liste = df.iloc[:, 4].dropna().unique()
            tum_hisseler = sorted([str(h).strip().upper() for h in ham_liste if str(h).strip() != ""])
    except:
        pass
else:
    st.error("Excel bulunamadı.")

st.write("---")
st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
if len(tum_hisseler) > 0:
    aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler, key="arama_motoru_select")
    if aranan_hisse != "Seçiniz...":
        try:
            h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="1d", timeout=2)
            if len(h_detay_veri) > 0:
                st.metric("Güncel Fiyat", f"{float(h_detay_veri['Close'].iloc[-1]):,.2f} TL")
        except:
            pass

st.write("---")
st.markdown('<p style="font-size:18px; font-weight:bold; color:#00ffcc;">🗒️Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti, yetkili kuruluşlar tarafından kişilerin risk ve getiri tercihleri dikkate alınarak kişiye özel sunulmaktadır.Burada yer alan yorum ve tavsiyeler ise genel niteliktedir. Bu tavsiyeler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir.</p>', unsafe_allow_html=True)
col_not1, col_not2 = st.columns(2)

with col_not2:
    st.markdown('<div style="color:#fff; font-size:14px; font-weight:bold;">Odadaki Tüm Kayıtlı Notlar</div>', unsafe_allow_html=True)
    # Sağ sütundaki tüm eski liste ve şifre kod bloğu tamamen temizlendi.
