import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# Google Fonts ve Gökkuşağı Gölgeli Gelişmiş CSS Stilleri
st.markdown('<style>@import url("https://googleapis.com"); .stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .bta-logo-konteyner {display: flex; justify-content: center; align-items: center; margin-top: 20px; margin-bottom: 25px;} .bta-logo {color: #ffffff !important; font-family: "Dancing Script", "Brush Script MT", cursive !important; font-weight: bold; font-size: 5.5rem; padding: 0px; background: none !important; box-shadow: none !important; letter-spacing: 14px; text-shadow: 0 0 10px #ff007f, 0 0 20px #ff00ff, 0 0 30px #00ffff, 0 0 40px #00ff00, 0 0 70px #ffff00, 0 0 80px #ff7f00, 0 0 100px #ff0000;} .gold-card {background: rgba(251, 191, 36, 0.1); border: 1px solid #fbbf24; border-radius: 10px; padding: 12px; text-align: center; box-shadow: 0 0 15px rgba(251, 191, 36, 0.2); margin-bottom: 15px;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;}</style>', unsafe_allow_html=True)

# Hafıza Kontrolleri
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}
if "altin_hafizasi" not in st.session_state: st.session_state["altin_hafizasi"] = {}
if "ziyaret_sayaci" not in st.session_state: st.session_state["ziyaret_sayaci"] = 0

if "ziyaret_edildi" not in st.session_state:
    st.session_state["ziyaret_sayaci"] += 1
    st.session_state["ziyaret_edildi"] = True

# 🌟 ÜST ORTA EL YAZISI VE GÖKKUŞAĞI GÖLGELİ BTA LOGOSU
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; text-align: center; margin-bottom: 20px;">🚪 <b>Ziyaret:</b> {st.session_state["ziyaret_sayaci"]} | 🕒 {guncel_an}</div>', unsafe_allow_html=True)

# 🪙 CANLI OTOMATİK ALTIN FİYAT MOTORU (Önbellekli ve Noktalı Format)
def canlı_altın_fiyatları_hesapla():
    anlik_zaman = time.time()
    if "vakit" in st.session_state["altin_hafizasi"]:
        if anlik_zaman - st.session_state["altin_hafizasi"]["vakit"] < 300: 
            return st.session_state["altin_hafizasi"]["fiyatlar"]
            
    try:
        ons_data = yf.Ticker("GC=F").history(period="1d")
        usd_data = yf.Ticker("USDTRY=X").history(period="1d")
        if not ons_data.empty and not usd_data.empty:
            ons = ons_data['Close'].iloc[-1]
            usd = usd_data['Close'].iloc[-1]
            gram_has = (ons / 31.1034768) * usd
            ceyrek = gram_has * 1.75 * 0.916 * 1.03 
            yarim = ceyrek * 2
            tam = ceyrek * 4
            
            fiyatlar = {"ceyrek": ceyrek, "yarim": yarim, "tam": tam}
            st.session_state["altin_hafizasi"] = {"vakit": anlik_zaman, "fiyatlar": fiyatlar}
            return fiyatlar
    except:
        pass
    return {"ceyrek": 0.0, "yarim": 0.0, "tam": 0.0}

altinlarlar = canlı_altın_fiyatları_hesapla()

# Fiyatları Türkçe standart formatına (Binlik nokta, Kuruş virgül) çeviren fonksiyon
def formatla_tl(deger):
    return "{:,.2f}".format(deger).replace(",", "X").replace(".", ",").replace("X", ".")

# Altın Fiyat Kartları Düzeni
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="gold-card"><span style="color:#fbbf24; font-weight:bold; font-size:1.1rem;">🟡 ÇEYREK ALTIN</span><br><span style="font-size:1.5rem; font-weight:bold; color:#fff;">{formatla_tl(altinlarlar["ceyrek"])} TL</span></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="gold-card"><span style="color:#fbbf24; font-weight:bold; font-size:1.1rem;">🟠 YARIM ALTIN</span><br><span style="font-size:1.5rem; font-weight:bold; color:#fff;">{formatla_tl(altinlarlar["yarim"])} TL</span></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="gold-card"><span style="color:#fbbf24; font-weight:bold; font-size:1.1rem;">👑 TAM ALTIN</span><br><span style="font-size:1.5rem; font-weight:bold; color:#fff;">{formatla_tl(altinlarlar["tam"])} TL</span></div>', unsafe_allow_html=True)

# Excel Okuma
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except Exception as e:
        st.error(f"Excel okuma hatası: {e}")

# Fiyat Motoru
def hızlı_canli_fiyat_bul(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - saved_time < 300: 
            return saved_price
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            fiyat = float(data['Close'].iloc[-1])
            st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
            return fiyat
    except:
        pass
    return 0.0

def temiz_metin_al(val):
    if pd.isna(val): return ""
    return str(val).strip().upper()

tablo_alsat = []
tablo_al = []

if df_kaynak is not None:
    for idx in range(2, len(df_kaynak)):
        try:
            if len(df_kaynak.columns) > 22:
                uv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 20])
                wv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 22])
                t_degeri = temiz_metin_al(df_kaynak.iloc[idx, 19])
                
                if uv_degeri and uv_degeri not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                    hisse_ara = re.findall(r'[A-Z]+', uv_degeri)
                    if hisse_ara:
                        hisse = str(hisse_ara[0]) # Liste parantezlerini temizleyen kritik ayar
                        canli_fiyat = hızlı_canli_fiyat_bul(hisse)
                        puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                        bta_puan = puan_bul if puan_bul else (t_degeri if t_degeri else uv_degeri)
                        tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{formatla_tl(canli_fiyat)} TL" if canli_fiyat > 0 else "Yükleniyor..."})
                
                if wv_degeri and wv_degeri not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                    hisse_ara = re.findall(r'[A-Z]+', wv_degeri)
                    if hisse_ara:
                        hisse = str(hisse_ara[0]) # Liste parantezlerini temizleyen kritik ayar
                        canli_fiyat = hızlı_canli_fiyat_bul(hisse)
                        puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                        bta_puan = puan_bul if puan_bul else (t_degeri if t_degeri else uv_degeri)
                        if hisse not in st.session_state["ozel_takip_kutusu"] and canli_fiyat > 0:
                            st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": guncel_an}
                        tablo_al.append({"Hisse Kodu 🚀": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{formatla_tl(canli_fiyat)} TL" if canli_fiyat > 0 else "Yükleniyor..."})
        except:
            pass

st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
if tablo_alsat: st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
else: st.write("🔒 Aktif AL SAT sinyali taranıyor...")

st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
if tablo_al: st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
else: st.write("🔒 Aktif BTA sinyali taranıyor...")

if st.session_state["ozel_takip_kutusu"]:
    st.markdown("#### 🌟 Özel Takip Havuzu 💰")
    tk_list = []
    for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
        cfiy = hızlı_canli_fiyat_bul(hisse)
        if cfiy == 0.0: cfiy = bilge["kayit_fiyati"]
        tk_list.append({"Hisse Kodu 🗝️": hisse, "Havuz Maliyeti": f"{formatla_tl(bilge['kayit_fiyati'])} TL", "Anlık Güncel": f"{formatla_tl(cfiy)} TL"})
    if tk_list:
        st.dataframe(pd.DataFrame(tk_list), use_container_width=True, hide_index=True)
        if st.button("🗑️ Havuzu Temizle", use_container_width=True):
            st.session_state["ozel_takip_kutusu"] = {}
            st.rerun()

# ✉️ YÖNETİCİYE NOT BIRAKMA ALANI (Sorunsuz Aktif)
MESAJ_DOSYASI = "gelen_mesajlar.txt"
st.write("---")
st.subheader("✉️ Yöneticiye Not Bırak")
kullanici_mesaji = st.text_area("Mesajınızı veya geri bildiriminizi buraya yazabilirsiniz:", placeholder="Mesajınız...", key="not_birak_alani")
if st.button("Gönder 📩"):
    if kullanici_mesaji.strip():
        try:
            with open(MESAJ_DOSYASI, "a", encoding="utf-8") as f:
                f.write(f"[{guncel_an}] - {kullanici_mesaji.strip()}\n")
