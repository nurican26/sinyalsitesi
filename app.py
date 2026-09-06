import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
import requests
from streamlit_autorefresh import st_autorefresh

# Sayfa Yapılandırması
st.set_page_config(page_title="Canlı Hisse Takip Programı", layout="wide")

# 🔄 CANLI FİYAT VE ANIMASYON KİLİDİ: Sayfa her 10 saniyede bir otomatik yenilenir
st_autorefresh(interval=10 * 1000, key="hisse_canli_yenileyici")

# Her yenilemede animasyonu baştan oynatmak için zaman damgası
anim_id = int(time.time())

# 🔥 FIREBASE REALTIME DATABASE AYARLARI
FIREBASE_URL = "https://SİZİN_PROJE_://firebaseio.com"

# --- GÜVENLİ YARDIMCI FONKSİYONLAR ---
def güvenli_mesaj_çek(url):
    üye_mesajları = [{"kullanici": "Sistem", "mesaj": "Canlı sohbet odasına hoş geldiniz! 🚀", "zaman": datetime.datetime.now().strftime("%H:%M")}]
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json():
            liste = [v for v in r.json().values()]
            üye_mesajları = sorted(liste, key=lambda x: x.get('timestamp', 0))[-30:]
    except:
        pass
    return üye_mesajları

def güvenli_mesaj_gönder(url, ad, msg):
    try:
        an = datetime.datetime.now()
        veri = {"kullanici": ad, "mesaj": msg, "zaman": an.strftime("%H:%M"), "timestamp": int(an.timestamp())}
        requests.post(url, json=veri, timeout=3)
    except:
        pass

def yfinance_fiyat_al(kod):
    try:
        t = yf.Ticker(f"{kod}.IS")
        h = t.history(period="1d")
        if not h.empty:
            return float(h['Close'].iloc[-1])
    except:
        pass
    return 0.0

def yfinance_alsat_al(kod):
    try:
        t = yf.Ticker(f"{kod}.IS")
        h = t.history(period="2d")
        if not h.empty and len(h) >= 2:
            son = float(h['Close'].iloc[-1])
            önce = float(h['Close'].iloc[-2])
            oran = ((son - önce) / önce) * 100
            return son, oran
        elif not h.empty:
            son = float(h['Close'].iloc[-1])
            return son, 0.0
    except:
        pass
    return 0.0, 0.0

def puan_temizle(p):
    if pd.isna(p) or str(p).strip().lower() in ["nan", "none", ""]: return ""
    try: return f"{float(p):.2f}"
    except: return str(p).strip()

def maliyet_temizle(m):
    if pd.isna(m) or str(m).strip().lower() in ["nan", "none", ""]: return 0.0
    try: return float(str(m).replace(",", "."))
    except: return 0.0

def kar_zarar_hesapla(maliyet, canli):
    if maliyet > 0 and canli > 0:
        return f"%{(((canli - maliyet) / maliyet) * 100):+.2f}"
    return "-"
# -------------------------------------------------------------------------

# 📥 Firebase'den Verileri Çek
canli_mesajlar = güvenli_mesaj_çek(FIREBASE_URL)

# 🖥️ SOL MENÜ (SIDEBAR) - CANLI SOHBET ODASI ALANI
with st.sidebar:
    st.markdown('<div class="sohbet-baslik">💬 BTA CANLI SOHBET ODASI</div>', unsafe_allow_html=True)
    sohbet_html = '<div class="sohbet-kutusu">'
    for m in canli_mesajlar:
        if m.get("kullanici") == "Sistem":
            sohbet_html += f'<div class="mesaj-satiri mesaj-sistem">🤖 <b>{m.get("kullanici")}:</b> {m.get("mesaj")}<span class="mesaj-zaman">{m.get("zaman")}</span></div>'
        else:
            sohbet_html += f'<div class="mesaj-satiri">👤 <span class="mesaj-yetkili">{m.get("kullanici")}:</span> {m.get("mesaj")}<span class="mesaj-zaman">{m.get("zaman")}</span></div>'
    sohbet_html += '</div>'
    st.markdown(sohbet_html, unsafe_allow_html=True)
    
    with st.form(key="sohbet_formu", clear_on_submit=True):
        takma_ad = st.text_input("Takma Adınız (Rumuz):", value="Yatırımcı", max_chars=15)
        yeni_mesaj = st.text_input("Mesajınız:", max_chars=100, placeholder="Hisseler hakkında konuşun...")
        gonder_butonu = st.form_submit_form_button("Gönder 📩")
        if gonder_butonu and yeni_mesaj.strip():
            güvenli_mesaj_gönder(FIREBASE_URL, takma_ad.strip(), yeni_mesaj.strip())
            st.rerun()

# Şık Neon Tasarım, Gökkuşağı Çember ve Yazı CSS Kodları
st.markdown(f'''
<style>
    .stApp {{background: #0f172a!important; padding: 0.5rem;}} 
    h1,h2,h3,h4,h5,h6,p,span,label {{color: #fff!important;}} 
    .stDataFrame {{width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}} 
    .alsat-baslik {{background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .al-baslik {{background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .spk-kutusu {{background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; color: #fca5a5 !important; font-size: 0.95rem;}}
    .sohbet-baslik {{background: linear-gradient(90deg, #0284c7 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 10px; color:#fff; font-size:1.1rem; text-align:center;}}
    .sohbet-kutusu {{background-color: #1e293b; border: 1px solid #38bdf8; border-radius: 8px; padding: 10px; max-height: 350px; overflow-y: auto; margin-bottom: 10px;}}
    .mesaj-satiri {{margin-bottom: 8px; padding: 6px; border-radius: 4px; background-color: #334155; font-size: 0.9rem;}}
    .mesaj-sistem {{background-color: rgba(14, 165, 233, 0.2); border-left: 3px solid #0ea5e9;}}
    .mesaj-zaman {{font-size: 0.75rem; color: #94a3b8; float: right; margin-top: 2px;}}
    .mesaj-yetkili {{color: #38bdf8 !important; font-weight: bold;}}
    .logo-konteyner {{ display: flex; justify-content: center; align-items: center; padding: 20px 0; margin-bottom: 10px; }}
    .cember-animasyon-{anim_id} {{
        width: 120px; height: 120px; border: 4px solid #fff; border-radius: 50%; display: flex; justify-content: center; align-items: center; background: transparent; position: relative; overflow: hidden;
        animation: gokkusagiCember 4s linear infinite, yukardanDus 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }}
    .bta-yazi-{anim_id} {{
        font-family: 'Caveat', 'Segoe UI', cursive, sans-serif; font-size: 3.2rem; font-weight: bold; margin: 0; padding: 0; z-index: 2;
        background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block;
        filter: drop-shadow(0px 2px 8px rgba(255,255,255,0.3)); animation: soldanYavascaKay 1.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }}
    @keyframes gokkusagiCember {{
        0% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
        14% {{ border-color: #ff7f00; box-shadow: 0 0 15px #ff7f00, inset 0 0 15px #ff7f00; }}
        28% {{ border-color: #ffff00; box-shadow: 0 0 15px #ffff00, inset 0 0 15px #ffff00; }}
        42% {{ border-color: #00ff00; box-shadow: 0 0 15px #00ff00, inset 0 0 15px #00ff00; }}
        56% {{ border-color: #00ffff; box-shadow: 0 0 15px #00ffff, inset 0 0 15px #00ffff; }}
        70% {{ border-color: #0000ff; box-shadow: 0 0 15px #0000ff, inset 0 0 15px #0000ff; }}
        84% {{ border-color: #8b00ff; box-shadow: 0 0 15px #8b00ff, inset 0 0 15px #8b00ff; }}
        100% {{ border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }}
    }}
    @keyframes yukardanDus {{ 0% {{ transform: translateY(-200px) scale(0.3); opacity: 0; }} 70% {{ transform: translateY(10px) scale(1.05); opacity: 1; }} 100% {{ transform: translateY(0) scale(1); opacity: 1; }} }}
    @keyframes soldanYavascaKay {{ 0% {{ transform: translateX(-140px); opacity: 0; }} 30% {{ opacity: 0.5; }} 100% {{ transform: translateX(0); opacity: 1; }} }}
</style>''', unsafe_allow_html=True)

# LOGO EKRAN ÇIKTISI
st.markdown(f'''<div class="logo-konteyner"><div class="cember-animasyon-{anim_id}"><span class="bta-yazi-{anim_id}">BTA</span></div></div>''', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        st.markdown("#### 🔍 BİST Canlı Fiyat Arama Motoru")
        
        hisse_havuzu = []
        if len(df.columns) >= 5:
            e_sutunu_temiz = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper()
            hisse_havuzu = [h for h in e_sutunu_temiz if h not in ["", "NAN", "NONE", "HİSSE", "BTA HİSSE"]]
            hisse_havuzu = sorted(list(set(hisse_havuzu)))
        
        secilen_hisse = st.selectbox("Canlı verisini görmek istediğiniz hisseyi seçin:", ["Seçiniz..."] + hisse_havuzu)
        
        if secilen_hisse != "Seçiniz...":
            fiyat_s, oran_s = yfinance_alsat_al(secilen_hisse)
            if fiyat_s > 0:
                st.success(f"📈 **{secilen_hisse}** Anlık Canlı Fiyatı: **{fiyat_s:.2f} TL** | Günlük Değişim: **%{oran_s:+.2f}**")
            else:
                st.warning("Seçilen hisse için canlı veri şu an çekilemedi.")
        
        st.write("---")

        tablo_bta = []
        tablo_alsat = []
        sinir = min(10, len(df))
        
        for idx in range(sinir):
            hisse_a = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]

            # Üst Panel İşlemleri
            if hisse_a and hisse_a not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                p_temiz = puan_temizle(puan_d)
                c_fiyat = yfinance_fiyat_al(hisse_a)
                maliyet = maliyet_temizle(alim_c)
                kz_str = kar_zarar_hesapla(maliyet, c_fiyat)

                tablo_bta.append({
                    "BTA PUAN 🔢": p_temiz, 
                    "BTA HİSSE 📈": hisse_a,
                    "BTA ALIM 📥": f"{maliyet:.2f} TL" if maliyet > 0 else alim_c,
