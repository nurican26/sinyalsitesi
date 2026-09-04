import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .altan-baslik {background: linear-gradient(90deg, #b45309 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.1); border: 1px solid #dc2626; padding: 8px; border-radius: 6px; margin-top: 25px; margin-bottom: 10px; color: #fca5a5 !important; font-size: 0.8rem; text-align: justify;} .bta-logo-konteyner {display: flex; justify-content: center; align-items: center; margin-top: 25px; margin-bottom: 35px; width: 100%;} .bta-logo {font-family: "Brush Script MT", "Comic Sans MS", cursive, sans-serif !important; font-weight: bold; font-size: 5rem; padding: 10px 50px; background: transparent; background-image: linear-gradient(45deg, #ff007f, #ff00ff, #8b00ff, #0000ff, #00ffff, #00ff00, #ffff00, #ff7f00, #ff0000); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 20px rgba(255, 0, 255, 0.6), 0 0 40px rgba(0, 255, 255, 0.4), 4px 4px 10px rgba(0, 0, 0, 0.8); display: inline-block; text-align: center; letter-spacing: 5px;} .kilit-uyari {background: rgba(255, 255, 255, 0.05); border-left: 4px solid #ca8a04; padding: 15px; border-radius: 6px; margin-bottom: 20px; font-size: 1.1rem;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;}</style>', unsafe_allow_html=True)

# 🔑 GÜVENLİ ÇİFT ŞİFRE PARAMETRELERİ
ZIYARETCI_SIFRESI = "bta3015"         # Sadece hisseleri görme yetkisi
YONETICI_SIFRESI = "3015"             # Kilitleyip açma (Yönetici) yetkisi

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
if "giris_yapildi" not in st.session_state: st.session_state["giris_yapildi"] = False
if "kullanici_rolu" not in st.session_state: st.session_state["kullanici_rolu"] = None

for k in ["kisitli_liste", "ziyaret_sayaci"]:
    if k not in st.session_state: st.session_state[k] = 0 if k == "ziyaret_sayaci" else []

# Giriş sayısı artırımı
st.session_state["ziyaret_sayaci"] += 1

# BTA LOGO ALANI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# 🛡️ ERİŞİM KONTROL MANTIĞI & SİLİKLEŞEN / GİZLENEN ŞİFRE PANELİ
erisim_izni = False

if mevcut_kilit == "Açık":
    erisim_izni = True
    st.session_state["giris_yapildi"] = True
    st.session_state["kullanici_rolu"] = "Misafir (Şifresiz Mod)"
elif st.session_state["giris_yapildi"]:
    erisim_izni = True
else:
    st.markdown("### 🔐 Erişim Paneli")
    girilen_sifre = st.text_input("Sinyal listesini açmak için şifrenizi giriniz:", type="password", placeholder="Şifrenizi yazıp Enter'a basın...")
    
    if girilen_sifre == ZIYARETCI_SIFRESI:
        st.session_state["giris_yapildi"] = True
        st.session_state["kullanici_rolu"] = "Üye"
        st.rerun()
    elif girilen_sifre == YONETICI_SIFRESI:
        st.session_state["giris_yapildi"] = True
        st.session_state["kullanici_rolu"] = "Yönetici"
        st.rerun()
    elif girilen_sifre != "":
        st.error("⚠️ Hatalı şifre girdiniz. Lütfen tekrar deneyiniz.")

# Üye Girişi Olduğunda Üst Bar Bilgilendirmesi
if st.session_state["giris_yapildi"]:
    col_profil, col_cikis = st.columns(2)
    col_profil.markdown(f'🟢 **Oturum Açık:** {st.session_state["kullanici_rolu"]} | 🚪 **Giriş Sayısı:** {st.session_state["ziyaret_sayaci"]}')
    if col_cikis.button("Çıkış Yap"):
        st.session_state["giris_yapildi"] = False
        st.session_state["kullanici_rolu"] = None
        st.rerun()

# 🎛️ BAĞIMSIZ YÖNETİCİ ODASI (Yalnızca Yöneticiye görünür)
if st.session_state["kullanici_rolu"] == "Yönetici":
    st.info(f"👑 **Yönetici Ayarları Paneli** | Sitenin Mevcut Durumu: **{mevcut_kilit}**")
    col_ac, col_kilitle = st.columns(2)
    if col_ac.button("🔓 HERKESE AÇ (Şifre Sorma)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Açık")
        st.rerun()
    if col_kilitle.button("🔒 SİTEYİ KİLİTLE (Herkes Şifre Girsin)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Kilitli")
        st.rerun()

# 💥 CANLI VERİ MOTORLARI
def hızlı_canli_fiyat_bul(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - saved_time < 300: return saved_price
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            fiyat = float(data['Close'].iloc[-1])
            st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
            return fiyat
    except: pass
    return 0.0

def tl_formatla(deger):
    """Sayıları Türk Lirası cinsinden binlik ayracı nokta olacak şekilde formatlar."""
    return f"{deger:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"

def altin_fiyatlarini_getir():
    """Canlı Ons ve Dolar kuru üzerinden fiziki altın fiyatlarını hesaplar."""
    try:
        ons_data = yf.Ticker("GC=F").history(period="1d")
        usd_data = yf.Ticker("USDTRY=X").history(period="1d")
        if not ons_data.empty and not usd_data.empty:
            ons = ons_data['Close'].iloc[-1]
            usd = usd_data['Close'].iloc[-1]
            
            # Hesaplama Parametreleri
            gram = (ons / 31.1034768) * usd
            ceyrek = gram * 1.605
            yarim = gram * 3.21
            tam = gram * 6.42
            return gram, ceyrek, yarim, tam
    except: pass
    return 3000.0, 4950.0, 9900.0, 19800.0

# 🟢 İÇERİK BLOKLARI (ERİŞİM İZNİ VARSA)
if erisim_izni:
    st.markdown("---")
    
    # 🪙 CANLI ALTIN FİYATLARI PANELİ
    st.markdown('<div class="altan-baslik">🏆 CANLI ALTIN FİYATLARI (TL)</div>', unsafe_allow_html=True)
    g_altin, c_altin, y_altin, t_altin = altin_fiyatlarini_getir()
    
    altin_col1, altin_col2, altin_col3, altin_col4 = st.columns(4)
    altin_col1.metric("Gram Altın", tl_formatla(g_altin))
    altin_col2.metric("Çeyrek Altın", tl_formatla(c_altin))
    altin_col3.metric("Yarım Altın", tl_formatla(y_altin))
    altin_col4.metric("Tam Altın", tl_formatla(t_altin))
    
    st.markdown("---")

    # 🔍 BORSA TÜM HİSSE ARAMA MOTORU
    st.markdown("### 🔎 BIST Tüm Hisse Arama Motoru")
    arama_kodu = st.text_input("Aramak istediğiniz hisse kodunu yazın (Örn: THYAO, EREGL, ASELS):", "").strip().upper()
    
    if arama_kodu:
        canli_ara_fiyat = hızlı_canli_fiyat_bul(arama_kodu)
        if canli_ara_fiyat > 0:
            st.success(f"📈 **{arama_kodu}** Anlık Hisse Fiyatı: **{tl_formatla(canli_ara_fiyat)}**")
            
            # TradingView Canlı Grafik Entegrasyonu
            st.markdown(f"#### 📊 {arama_kodu} Canlı Teknik Analiz Grafiği")
            tradingview_kod = f"""
            <div style="height:400px;">
            <iframe src="https://tradingview.com{arama_kodu}&interval=D&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=%5B%5D&theme=dark&style=1&timezone=Europe%2FIstanbul&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=tr" style="width: 100%; height: 100%; border: none;"></iframe>
            </div>
            """
            st.components.v1.html(tradingview_kod, height=400)
        else:
            st.error(f"❌ {arama_kodu} koduna ait canlı veri bulunamadı. Lütfen kodu doğru girdiğinizden emin olun.")

    st.markdown("---")

    # EXCEL'DEN VERİ OKUMA VE TABLOLAR
    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: 
            df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except: 
            pass

    tablo_alsat, tablo_al = [], []
    guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")

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
