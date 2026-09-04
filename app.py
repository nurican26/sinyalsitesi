import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.1); border: 1px solid #dc2626; padding: 8px; border-radius: 6px; margin-top: 25px; margin-bottom: 10px; color: #fca5a5 !important; font-size: 0.8rem; text-align: justify;} .bta-logo-konteyner {display: flex; justify-content: center; align-items: center; margin-top: 25px; margin-bottom: 35px; width: 100%;} .bta-logo {font-family: "Brush Script MT", "Comic Sans MS", cursive, sans-serif !important; font-weight: bold; font-size: 5rem; padding: 10px 50px; background: transparent; background-image: linear-gradient(45deg, #ff007f, #ff00ff, #8b00ff, #0000ff, #00ffff, #00ff00, #ffff00, #ff7f00, #ff0000); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 20px rgba(255, 0, 255, 0.6), 0 0 40px rgba(0, 255, 255, 0.4), 4px 4px 10px rgba(0, 0, 0, 0.8); display: inline-block; text-align: center; letter-spacing: 5px;} .kilit-uyari {background: rgba(255, 255, 255, 0.05); border-left: 4px solid #ca8a04; padding: 15px; border-radius: 6px; margin-bottom: 20px; font-size: 1.1rem;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;}</style>', unsafe_allow_html=True)

# 🔑 GÜVENLİ ÇİFT ŞİFRE PARAMETRELERİ
ZIYARETCI_SIFRESI = "bta3015"         # Müşteri Girişi
YONETICI_SIFRESI = "3015"             # Yönetici Girişi

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
if "girilen_sifre" not in st.session_state: st.session_state["girilen_sifre"] = ""

for k in ["kisitli_liste", "ziyaret_sayaci"]:
    if k not in st.session_state: st.session_state[k] = 0 if k == "ziyaret_sayaci" else []

# Giriş sayısı artırımı
st.session_state["ziyaret_sayaci"] += 1

# BTA LOGO ALANI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# 🛠️ ERİŞİM KONTROL MANTIĞI
erisim_izni = False
if mevcut_kilit == "Açık" or st.session_state["girilen_sifre"] == ZIYARETCI_SIFRESI or st.session_state["girilen_sifre"] == YONETICI_SIFRESI:
    erisim_izni = True

# 🔐 GİRİŞ PANELİ (Yalnızca erişim izni YOKSA görünür, şifre doğruysa tamamen KAPANIR)
if not erisim_izni:
    st.markdown("### 🔐 Erişim Paneli")
    gecici_sifre = st.text_input("Sinyal listesini açmak veya yönetici ayarlarını yönetmek için şifrenizi giriniz:", type="password", placeholder="Şifrenizi yazıp Enter'a basın...")
    if gecici_sifre:
        st.session_state["girilen_sifre"] = gecici_sifre
        st.rerun()
    st.warning("⚠️ Bu içeriği görebilmek için geçerli bir erişim şifresi girmeniz gerekmektedir.")

# 💥 CANLI FİYAT MOTORU
@st.cache_data(ttl=300)
def hızlı_canli_fiyat_bul(hisse_kodu):
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            return float(data['Close'].iloc[-1])
    except: pass
    return 0.0

# 🟢 2. BLOK: GİRİŞ YAPILDIYSA İÇERİK YÜKLENİR
if erisim_izni:
    is_admin = (st.session_state["girilen_sifre"] == YONETICI_SIFRESI)
    
    # Üst Bilgi Barı ve Oturumu Kapat Butonu
    col_bilgi, col_cikis = st.columns([4, 1])
    with col_bilgi:
        st.markdown(f'<div style="font-size: 1rem; color: #a5f3fc; font-weight: bold; padding-top: 5px;">🚪 Giriş Sayısı: {st.session_state["ziyaret_sayaci"]}</div>', unsafe_allow_html=True)
    with col_cikis:
        if st.button("🔒 Oturumu Kapat", use_container_width=True):
            st.session_state["girilen_sifre"] = ""
            st.rerun()

    # 👑 Sadece Yönetici Giriş Yaptıysa Gösterilecek Alan
    if is_admin:
        st.info(f"👑 **Yönetici Kontrol Paneli** | Sitenin Mevcut Durumu: **{mevcut_kilit}**")
        col_ac, col_kilitle = st.columns(2)
        if col_ac.button("🔓 HERKESE AÇ (Şifre Sorma)"):
            with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Açık")
            st.rerun()
        if col_kilitle.button("🔒 SİTEYİ KİLİTLE (Herkes Şifre Girsin)"):
            with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Kilitli")
            st.rerun()

    # Verileri Excel'den Çekme Adımı
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
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', wv)
                            bta_puan = p_bul[0] if p_bul else t_deg
                            if hisse not in st.session_state["ozel_takip_kutusu"] and cfiy > 0:
                                st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                            tablo_al.append({"Hisse Kodu 🚀": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
            except: pass

    # Tablo Gösterimleri
    st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
    if tablo_alsat: 
        st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
    else: 
        st.info("🔒 Aktif AL SAT sinyali taranıyor...")

    st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
    if tablo_al: 
        st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
    else: 
        st.info("🔒 Aktif AL sinyali taranıyor...")

    # 📈 DİNAMİK ÖZEL TAKİP LİSTESİ (KÂR / ZARAR HESAPLAYICI)
    st.markdown('<div class="al-baslik">🎯 BTA ÖZEL TAKİP VE PERFORMANS</div>', unsafe_allow_html=True)
    if st.session_state["ozel_takip_kutusu"]:
        takip_verileri = []
        for h_kod, bilgi in list(st.session_state["ozel_takip_kutusu"].items()):
            guncel_fiyat = hızlı_canli_fiyat_bul(h_kod)
            if guncel_fiyat > 0:
                degisim = ((guncel_fiyat - bilgi["kayit_fiyati"]) / bilgi["kayit_fiyati"]) * 100
                takip_verileri.append({
                    "Hisse 📌": h_kod,
                    "Giriş Fiyatı": f"{bilgi['kayit_fiyati']:.2f} TL",
                    "Güncel Fiyat": f"{guncel_fiyat:.2f} TL",
                    "Performans (%)": f"{degisim:+.2f}%",
                    "Kayıt Tarihi": bilgi["kayit_zamani"]
                })
        if takip_verileri:
            st.dataframe(pd.DataFrame(takip_verileri), use_container_width=True, hide_index=True)
    else:
        st.write("Sinyal merkezine hisse düştüğünde performans takibi otomatik başlayacaktır.")

    # 💬 MESAJLAŞMA ALANI
    st.markdown("---")
    st.markdown("### ✉️ Yöneticiye Not / Mesaj Gönder")
    kullanici_mesaji = st.text_area("Sorularınızı veya geri bildirimlerinizi buraya yazabilirsiniz:", placeholder="Mesajınızı buraya yazın...")
    if st.button("Mesajı İlet"):
        if kullanici_mesaji.strip():
            with open(MESAJ_DOSYASI, "a", encoding="utf-8") as f:
