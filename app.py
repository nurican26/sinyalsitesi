import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('<style>@import url("https://googleapis.com"); .stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.1); border: 1px solid #dc2626; padding: 8px; border-radius: 6px; margin-top: 25px; margin-bottom: 10px; color: #fca5a5 !important; font-size: 0.8rem; text-align: justify;} .bta-logo-konteyner {display: flex; justify-content: center; align-items: center; margin-top: 15px; margin-bottom: 25px; gap: 15px;} .bta-logo {font-family: "Caveat", cursive !important; font-size: 4.5rem !important; color: #10b981 !important; text-shadow: 0 0 10px #10b981, 0 0 20px #10b981, 0 0 40px #059669, 0 0 80px #059669; animation: glow 1.5s ease-in-out infinite alternate; text-align: center;} @keyframes glow { from { text-shadow: 0 0 10px #10b981, 0 0 20px #10b981, 0 0 30px #059669; } to { text-shadow: 0 0 15px #34d399, 0 0 30px #10b981, 0 0 50px #10b981, 0 0 70px #059669; } } .kilit-uyari {background: rgba(255, 255, 255, 0.05); border-left: 4px solid #ca8a04; padding: 15px; border-radius: 6px; margin-bottom: 20px; font-size: 1.1rem;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .altin-kart {background: linear-gradient(135deg, #1e1b4b 0%, #2e1065 100%); border: 1px solid #eab308; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 0 15px rgba(234, 179, 8, 0.2);}</style>', unsafe_allow_html=True)

# 🔑 GÜVENLİ ÇİFT ŞİFRE PARAMETRELERİ
ZIYARETCI_SIFRESI = "bta26"         # Sadece hisseleri görme yetkisi (5 Karakter yapıldı)
YONETICI_SIFRESI = "admin"         # Kilitleyip açma yetkisi (5 Karakter yapıldı)

MESAJ_DOSYASI = "gelen_mesajlar.txt"
DURUM_DOSYASI = "site_durumu.txt"

# 💾 Kalıcı Kilit Durumunu Dosyadan Okuma
if not os.path.exists(DURUM_DOSYASI):
    with open(DURUM_DOSYASI, "w", encoding="utf-8") as f:
        f.write("Açık")

with open(DURUM_DOSYASI, "r", encoding="utf-8") as f:
    mevcut_kilit = f.read().strip()

# Hafıza Kontrolleri
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

for k in ["kisitli_liste", "ziyaret_sayaci", "topham_oy_sayisi", "topham_yildiz_puani", "is_counted"]:
    if k not in st.session_state: st.session_state[k] = 0 if "sayaci" in k or "sayisi" in k or "puani" in k else ([] if k == "kisitli_liste" else False)

if not st.session_state["is_counted"]:
    st.session_state["ziyaret_sayaci"] += 1
    st.session_state["is_counted"] = True

# BTA LOGO ALANI (ORTALANMIŞ, EL YAZILI, CAVCAVLI IŞIKLI VE YANINDA LOGOLAR)
st.markdown('<div class="bta-logo-konteyner"><span style="font-size: 3rem;">🔥</span><div class="bta-logo">BTA</div><span style="font-size: 3rem;">🚀</span></div>', unsafe_allow_html=True)

# 🔐 ERİŞİM PANELİ (UFAK VE 5 KARAKTER SINIRLI)
st.markdown("<h3 style='text-align: center;'>🔐 Erişim Paneli</h3>", unsafe_allow_html=True)
p_col1, p_col2, p_col3 = st.columns([2, 1, 2])
with p_col2:
    girilen_sifre = st.text_input("Şifre:", type="password", placeholder="-----", max_chars=5, label_visibility="collapsed")

# 🎛️ BAĞIMSIZ YÖNETİCİ ODASI
is_admin = False
if girilen_sifre == YONETICI_SIFRESI:
    is_admin = True

if is_admin:
    st.info(f"👑 **Yönetici Girişi Başarılı.** Sitenin Mevcut Durumu: **{mevcut_kilit}**")
    col_ac, col_kilitle = st.columns(2)
    if col_ac.button("🔓 HERKESE AÇ (Şifre Sorma)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Açık")
        st.rerun()
    if col_kilitle.button("🔒 SİTEYİ KİLİTLE (Herkes Şifre Girsin)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Kilitli")
        st.rerun()

# 🛠️ ERİŞİM KONTROL MANTIĞI
erisim_izni = False
if mevcut_kilit == "Açık" or girilen_sifre == ZIYARETCI_SIFRESI or girilen_sifre == YONETICI_SIFRESI:
    erisim_izni = True
else:
    st.warning("⚠️ Bu içeriği görebilmek için geçerli bir erişim şifresi girmeniz gerekmektedir.")

# 💥 CANLI FİYAT MOTORU
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
    except: pass
    return 0.0

# 🟡 CANLI ALTIN FİYATLARI MOTORU (OTOMATİK GÜNCEL)
def canlı_altın_fiyatları_al():
    try:
        ons_gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        usd_try = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
        gram_altin = (ons_gold / 31.1034768) * usd_try
        ceyrek_altin = gram_altin * 1.605
        yarim_altin = gram_altin * 3.21
        return gram_altin, ceyrek_altin, yarim_altin
    except:
        return 0.0, 0.0, 0.0

# Altın Fiyat Paneli Gösterimi
st.markdown("### 📊 Güncel Altın Piyasası")
g_altin, c_altin, y_altin = canlı_altın_fiyatları_al()
altin_col1, altin_col2, altin_col3 = st.columns(3)
with altin_col1:
    st.markdown(f'<div class="altin-kart"><h4 style="color:#eab308!important;margin:0;">Gram Altın</h4><h2 style="margin:5px 0;">{g_altin:,.2f} TL</h2></div>', unsafe_allow_html=True)
with altin_col2:
    st.markdown(f'<div class="altin-kart"><h4 style="color:#eab308!important;margin:0;">Çeyrek Altın</h4><h2 style="margin:5px 0;">{c_altin:,.2f} TL</h2></div>', unsafe_allow_html=True)
with altin_col3:
    st.markdown(f'<div class="altin-kart"><h4 style="color:#eab308!important;margin:0;">Yarım Altın</h4><h2 style="margin:5px 0;">{y_altin:,.2f} TL</h2></div>', unsafe_allow_html=True)

# 🔍 BORSA TÜM HİSSELER ARAMA MOTORU
st.markdown("### 🔎 BIST Canlı Hisse Sorgulama")
arama_col1, arama_col2 = st.columns([1, 3])
with arama_col1:
    hisse_girdi = st.text_input("Hisse Kodu Girin (Örn: THYAO, SASA):", value="THYAO").strip().upper()
if hisse_girdi:
    anlik_fiyat = hızlı_canli_fiyat_bul(hisse_girdi)
    if anlik_fiyat > 0:
        with arama_col2:
            st.success(f"📈 **{hisse_girdi}** Güncel Hisse Fiyatı: **{anlik_fiyat:,.2f} TL** (Anlık Veri Güncellendi)")
    else:
        with arama_col2:
            st.error("Hisse verisi alınamadı. Lütfen kodu doğru girdiğinizden emin olun.")

st.markdown("---")

# 🟢 1. BLOK: ERİŞİM İZNİ VARSA SİTE DETAYLARI VE HİSSELER SORUNSUZ YÜKLENİR
if erisim_izni:
    guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
    st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px;">⭐ <b>Puan:</b> {puan:.2f} | 🔥 <b>Oy:</b> {st.session_state["topham_oy_sayisi"]} | 🚪 <b>Giriş:</b> {st.session_state["ziyaret_sayaci"]} | 🕒 {guncel_an}</div>', unsafe_allow_html=True)

    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: 
            df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except: 
            st.error("Excel dosyası okunurken hata oluştu. Lütfen formatı kontrol edin.")

    tablo_alsat, tablo_al = [], []
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
                            tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:,.2f} TL" if cfiy > 0 else "Yükleniyor..."})
                            
                    if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                        h_ara = re.findall(r'[A-Z]+', wv)
                        if h_ara:
                            hisse = str(h_ara[0])
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', wv)
