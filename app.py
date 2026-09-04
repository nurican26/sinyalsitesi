import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.1); border: 1px solid #dc2626; padding: 8px; border-radius: 6px; margin-top: 25px; margin-bottom: 10px; color: #fca5a5 !important; font-size: 0.8rem; text-align: justify;} .bta-logo-konteyner {display: flex; justify-content: center; align-items: center; margin-top: 25px; margin-bottom: 35px; width: 100%;} .bta-logo {font-family: "Brush Script MT", "Comic Sans MS", cursive, sans-serif !important; font-weight: bold; font-size: 5rem; padding: 10px 50px; background: transparent; background-image: linear-gradient(45deg, #ff007f, #ff00ff, #8b00ff, #0000ff, #00ffff, #00ff00, #ffff00, #ff7f00, #ff0000); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 20px rgba(255, 0, 255, 0.6), 0 0 40px rgba(0, 255, 255, 0.4), 4px 4px 10px rgba(0, 0, 0, 0.8); display: inline-block; text-align: center; letter-spacing: 5px;} .kilit-uyari {background: rgba(255, 255, 255, 0.05); border-left: 4px solid #ca8a04; padding: 15px; border-radius: 6px; margin-bottom: 20px; font-size: 1.1rem;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .altin-kartlari {display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap;} .altin-kutusu {background: rgba(255, 255, 255, 0.05); padding: 12px 20px; border-radius: 8px; border: 1px solid #eab308; min-width: 150px; text-align: center;}</style>', unsafe_allow_html=True)

# 🔑 GÜVENLİ ÇİFT ŞİFRE PARAMETRELERİ
ZIYARETCI_SIFRESI = "bta3015"         # Sadece hisseleri görme yetkisi
YONETICI_SIFRESI = "3015"     # Kilitleyip açma (Yönetici) yetkisi

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
if "altin_hafizasi" not in st.session_state: st.session_state["altin_hafizasi"] = {"Gram": 0.0, "Çeyrek": 0.0, "Yarım": 0.0, "Tam": 0.0, "son_guncelleme": 0}

for k in ["kisitli_liste", "ziyaret_sayaci"]:
    if k not in st.session_state: st.session_state[k] = 0 if k == "ziyaret_sayaci" else []

# Giriş sayısı her etkileşimde hızlıca yükselmesi için kısıtlama kaldırıldı
st.session_state["ziyaret_sayaci"] += 1

# BTA LOGO ALANI (ORTALANMIŞ, GÖKKUŞAĞI, EL YAZISI, IŞIKLI VE GÖLGELİ)
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# ⚡ ARKA PLANDA KASMAYAN ALTIN FİYAT MOTORU
def arka_plan_altin_guncelle():
    su_an = time.time()
    if su_an - st.session_state["altin_hafizasi"]["son_guncelleme"] > 300: # 5 dakikada bir günceller
        try:
            gold_ticker = yf.Ticker("GC=F")
            usdtry_ticker = yf.Ticker("TRY=X")
            gold_data = gold_ticker.history(period="1d")
            usdtry_data = usdtry_ticker.history(period="1d")
            if not gold_data.empty and not usdtry_data.empty:
                ons_fiyat = float(gold_data['Close'].iloc[-1])
                usd_tl = float(usdtry_data['Close'].iloc[-1])
                gram_altin = (ons_fiyat / 31.1034768) * usd_tl
                st.session_state["altin_hafizasi"] = {
                    "Gram": round(gram_altin, 2),
                    "Çeyrek": round(gram_altin * 1.63, 2),
                    "Yarım": round(gram_altin * 3.26, 2),
                    "Tam": round(gram_altin * 6.51, 2),
                    "son_guncelleme": su_an
                }
        except: pass

arka_plan_altin_guncelle()

# 🔐 ERİŞİM KONTROL MANTIĞI VE PANEL GİZLEME
erisim_izni = False
if "giris_durumu" not in st.session_state:
    st.session_state["giris_durumu"] = False

if mevcut_kilit == "Açık":
    erisim_izni = True
else:
    if not st.session_state["giris_durumu"]:
        st.markdown("### 🔐 Erişim Paneli")
        girilen_sifre = st.text_input("Sinyal listesini açmak veya yönetici ayarlarını yönetmek için şifrenizi giriniz:", type="password", placeholder="Şifrenizi yazıp Enter'a basın...")
        
        if girilen_sifre == ZIYARETCI_SIFRESI or girilen_sifre == YONETICI_SIFRESI:
            st.session_state["giris_durumu"] = True
            st.session_state["girilen_aktif_sifre"] = girilen_sifre
            st.rerun()
        elif girilen_sifre != "":
            st.warning("⚠️ Bu içeriği görebilmek için geçerli bir erişim şifresi girmeniz gerekmektedir.")
    else:
        erisim_izni = True

# 🎛️ BAĞIMSIZ YÖNETİCİ ODASI (Yalnızca şifre girerken görünür, giriş yapılınca kaybolur)
if not st.session_state["giris_durumu"] and 'girilen_sifre' in locals() and girilen_sifre == YONETICI_SIFRESI:
    st.info(f"👑 **Yönetici Girişi Başarılı.** Sitenin Mevcut Durumu: **{mevcut_kilit}**")
    col_ac, col_kilitle = st.columns(2)
    if col_ac.button("🔓 HERKESE AÇ (Şifre Sorma)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Açık")
        st.rerun()
    if col_kilitle.button("🔒 SİTEYİ KİLİTLE (Herkes Şifre Girsin)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Kilitli")
        st.rerun()

# 💥 CANLI FİYAT MOTORU
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

# 🟢 1. BLOK: ERİŞİM İZNİ VARSA SİTE DETAYLARI VE HİSSELER SORUNSUZ YÜKLENİR
if erisim_izni:
    # Canlı Altın Kartları Ekranın Başına Yerleşir
    altin_verisi = st.session_state["altin_hafizasi"]
    if altin_verisi["Gram"] > 0:
        st.markdown(f"""
        <div class="altin-kartlari">
            <div class="altin-kutusu">🪙 <b>Gram Altın</b><br><span style='color:#eab308; font-size:1.2rem;'>{altin_verisi['Gram']} TL</span></div>
            <div class="altin-kutusu">🪙 <b>Çeyrek Altın</b><br><span style='color:#eab308; font-size:1.2rem;'>{altin_verisi['Çeyrek']} TL</span></div>
            <div class="altin-kutusu">🪙 <b>Yarım Altın</b><br><span style='color:#eab308; font-size:1.2rem;'>{altin_verisi['Yarım']} TL</span></div>
            <div class="altin-kutusu">🪙 <b>Tam Altın</b><br><span style='color:#eab308; font-size:1.2rem;'>{altin_verisi['Tam']} TL</span></div>
        </div>
        """, unsafe_allow_html=True)

    # Sadece Giriş Sayısı Bırakıldı (Puan, Oy, Tarih/Saat tamamen temizlendi)
    st.markdown(f'<div style="font-size: 1rem; color: #a5f3fc; margin-bottom: 20px; font-weight: bold;">🚪 Giriş Sayısı: {st.session_state["ziyaret_sayaci"]}</div>', unsafe_allow_html=True)

    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except: pass

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
                            hisse = str(h_ara[0])
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv)
                            bta_puan = p_bul[0] if p_bul else t_deg
                            tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
                            
                    if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                        h_ara = re.findall(r'[A-Z]+', wv)
                        if h_ara:
                            hisse = str(h_ara[0])
                            cfiy = hızlı_canli_fiyat_bul(hisse)
