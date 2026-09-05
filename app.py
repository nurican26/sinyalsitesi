import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# CSS Tasarımı - Sağdan Sola Yavaşça Akan El Yazılı Gökkuşağı Neon BTA Logosu
st.markdown("""
<style>
    @import url('https://googleapis.com');

    /* Gökkuşağı Renk Değişim Animasyonu */
    @keyframes rainbowNeon {
        0% { color: #ff007f !important; text-shadow: 0 0 15px #ff007f, 0 0 30px #ff007f; }
        25% { color: #00f2fe !important; text-shadow: 0 0 15px #00f2fe, 0 0 30px #00f2fe; }
        50% { color: #10b981 !important; text-shadow: 0 0 15px #10b981, 0 0 30px #10b981; }
        75% { color: #a855f7 !important; text-shadow: 0 0 15px #a855f7, 0 0 30px #a855f7; }
        100% { color: #ff007f !important; text-shadow: 0 0 15px #ff007f, 0 0 30px #ff007f; }
    }

    /* Sağdan Sola Yavaş Kayma Animasyonu */
    @keyframes marquee {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; 
        padding: 0.5rem;
    } 
    h1,h2,h3,h4,h5,h6,p,span,label {
        color: #fff!important; 
        font-family: "Segoe UI", sans-serif;
    } 
    input {
        color: #000!important; 
        background-color: #fff!important;
    } 
    .stDataFrame {
        width: 100% !important; 
        border: 1px solid #10b981 !important; 
        border-radius: 8px;
    } 
    div.block-container {
        padding-top: 1rem; 
        padding-bottom: 0.5rem;
    } 
    .alsat-baslik {
        background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); 
        padding: 8px; 
        border-radius: 5px; 
        font-weight: bold; 
        margin-bottom: 5px;
    } 
    .al-baslik {
        background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); 
        padding: 8px; 
        border-radius: 5px; 
        font-weight: bold; 
        margin-bottom: 5px;
    } 
    /* Yavaşça Kayan Logo Konteyneri */
    .bta-logo-konteyner {
        width: 100%;
        overflow: hidden; 
        white-space: nowrap;
        margin-top: 10px; 
        margin-bottom: 25px;
        padding: 10px 0;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
    } 
    .bta-logo {
        display: inline-block;
        font-family: 'Alex Brush', cursive !important; 
        font-style: italic !important;
        font-weight: normal !important; 
        font-size: 6rem; 
        letter-spacing: 0px; 
        padding-left: 100%; 
        animation: marquee 25s infinite linear, rainbowNeon 8s infinite linear; 
    } 
    .kilit-uyari {
        background: rgba(255, 255, 255, 0.05); 
        border-left: 4px solid #ca8a04; 
        padding: 15px; 
        border-radius: 6px; 
        margin-bottom: 20px; 
        font-size: 1.1rem;
    } 
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        font-size: 1.25rem !important; 
        font-weight: bold !important; 
        color: #ffffff !important;
    } 
</style>
""", unsafe_allow_html=True)

# 🔑 PARAMETRELER
YONETICI_SIFRESI = "bta2026"

# Hafıza Kontrolleri
if "oda_kilitli_mi" not in st.session_state: st.session_state["oda_kilitli_mi"] = False
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

# BTA LOGO ALANI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# 🛠️ SOL MENÜ: ODA YÖNETİM MERKEZİ
st.sidebar.markdown("### 🛠️ Oda Yönetim Merkezi")
admin_sifre = st.sidebar.text_input("Yönetici Şifresi:", type="password", placeholder="Ayarlar için girin...")

if admin_sifre == YONETICI_SIFRESI:
    st.sidebar.success("⚡ Yönetici Yetkisi Aktif")
    if st.session_state["oda_kilitli_mi"]:
        st.sidebar.error("🔴 Şu an: ODA KİLİTLİ")
        if st.sidebar.button("🔓 Odayı Herkese Aç", use_container_width=True):
            st.session_state["oda_kilitli_mi"] = False
            st.rerun()
    else:
        st.sidebar.success("🟢 Şu an: HERKESE AÇIK")
        if st.sidebar.button("🔒 Odayı Herkese Kilitle", use_container_width=True):
            st.session_state["oda_kilitli_mi"] = True
            st.rerun()
else:
    if admin_sifre: st.sidebar.error("Hatalı Yönetici Şifresi!")

# --- 🏢 DURUM KONTROLÜ VE İÇERİK ---
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div class="kilit-uyari">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Analiz robotları ve sistem verileri şu an güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
else:
    if st.session_state["oda_kilitli_mi"]:
        st.warning("⚠️ Oda dışarıya kilitli fakat Yönetici olduğunuz için erişim sağladınız.")

    # Excel Okuma
    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: 
            df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except Exception as e:
            st.error(f"Excel okuma hatası: {e}")
    else:
        st.warning(f"⚠️ '{excel_yolu}' veri dosyası bulunamadı. Lütfen dizini kontrol edin.")

    # Fiyat Motoru
    def hızlı_canli_fiyat_bul(hisse_kodu):
        if not hisse_kodu: return 0.0
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

    def temiz_metin_al(val):
        if pd.isna(val): return ""
        return str(val).strip().upper()

    # 🎯 %100 ETKİLİ METİN VE PARANTEZ TEMİZLEME MODÜLÜ
    def listeyi_sadece_hisse_yap(ham_metin):
        # Köşeli parantezleri, tırnakları, AL ve SAT kelimelerini tamamen imha eder
        ad = str(ham_metin).replace("[", "").replace("]", "").replace("'", "").replace('"', '').replace(" ", "")
        ad = ad.replace(",AL", "").replace(",SAT", "").replace(",_SAT", "").replace(",_AL", "")
        return ad.strip()

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
                            # 🎯 Yeni filtre motorunu devreye alıyoruz
                            temiz_isim = listeyi_sadece_hisse_yap(hisse_ara)
                            if temiz_isim:
                                canli_fiyat = hızlı_canli_fiyat_bul(temiz_isim)
                                puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                                bta_puan = puan_bul if puan_bul else (t_degeri if t_degeri else uv_degeri)
                                tablo_alsat.append({"Hisse Kodu 📈": temiz_isim, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."})
                    
                    if wv_degeri and wv_degeri not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                        hisse_ara = re.findall(r'[A-Z]+', wv_degeri)
                        if hisse_ara:
                            # 🎯 Yeni filtre motorunu devreye alıyoruz
                            temiz_isim = listeyi_sadece_hisse_yap(hisse_ara)
                            if temiz_isim:
                                canli_fiyat = hızlı_canli_fiyat_bul(temiz_isim)
                                puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                                bta_puan = puan_bul if puan_bul else (t_degeri if t_degeri else uv_degeri)
                                if temiz_isim not in st.session_state["ozel_takip_kutusu"] and canli_fiyat > 0:
                                    st.session_state["ozel_takip_kutusu"][temiz_isim] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")}
                                tablo_al.append({"Hisse Kodu 🚀": temiz_isim, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."})
            except:
                pass

    st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
    if tablo_alsat: st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
    else: st.write("🔒 Aktif sinyal taranıyor...")

    st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
    if tablo_al: st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
    else: st.write("🔒 Aktif sinyal taranıyor...")

    if st.session_state["ozel_takip_kutusu"]:
        st.markdown("#### 🌟 Özel Takip Havuzu 💰")
        tk_list = []
        for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
            cfiy = hızlı_canli_fiyat_bul(hisse)
            if cfiy == 0.0: cfiy = bilge["kayit_fiyati"]
