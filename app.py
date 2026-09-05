import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
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
    /* EL YAZILI, BİTİŞİK VE SAĞDAN SOLA YAVAŞÇA KAYAN GÖKKUŞAĞI BTA YAZISI */
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
    div.stButton > button {
        background-color: transparent; 
        color: #45f3ff; 
        border: 2px solid #45f3ff; 
        box-shadow: 0 0 10px #45f3ff; 
        border-radius: 8px; 
        transition: 0.3s;
    } 
    div.stButton > button:hover {
        background-color: #45f3ff; 
        color: #111; 
        box-shadow: 0 0 20px #45f3ff;
    }
    .spk-kutusu {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 🔑 PARAMETRELER
YONETICI_SIFRESI = "bta2026"

# Hafıza Kontrolleri
if "oda_kilitli_mi" not in st.session_state: st.session_state["oda_kilitli_mi"] = False
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}
if "sohbet_gecmisi" not in st.session_state: st.session_state["sohbet_gecmisi"] = []

# BTA LOGO ALANI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# --- ⚠️ SPK YASAL UYARI ALANI (SAYFA BAŞINDA SABİT) ---
st.markdown("""
<div class="spk-kutusu">
    <h4 style="color:#ef4444 !important; margin-top:0;">⚠️ SPK YASAL UYARI</h4>
    <p style="font-size:0.9rem; color:#cbd5e1 !important; margin-bottom:0;">
        Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. 
        Yatırım danışmanlığı hizmeti, yetkili kuruluşlar tarafından kişilerin risk ve getiri tercihleri 
        dikkate alınarak kişiye özel sunulmaktadır. Burada yer alan bilgilere dayanılarak yatırım kararı 
        verilmesi beklentilerinize uygun sonuçlar doğurmayabilir.
    </p>
</div>
""", unsafe_allow_html=True)

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


# --- GÜNCEL ALTIN FİYATLARI FONKSİYONU ---
def canli_altin_fiyatlari():
    try:
        ons_ticker = yf.Ticker("GC=F")
        usd_kur_data = yf.download("TRY=X", period="1d", progress=False)
        ons_data = ons_ticker.history(period="1d")
        
        ons_fiyat = float(ons_data['Close'].iloc[-1])
        usd_kur = float(usd_kur_data['Close'].iloc[-1])
        
        gram_altin = (ons_fiyat / 31.1034768) * usd_kur
        
        altin_data = {
            "Altın Türü 🪙": ["Gram Altın", "Çeyrek Altın (1.75g)", "Yarım Altın (3.50g)", "Tam Altın (7.01g)"],
            "Güncel Fiyat (TL) 💰": [
                f"{round(gram_altin, 2):,}".replace(",", "."),
                f"{round(gram_altin * 1.75, 2):,}".replace(",", "."),
                f"{round(gram_altin * 3.50, 2):,}".replace(",", "."),
                f"{round(gram_altin * 7.01, 2):,}".replace(",", ".")
            ]
        }
        return pd.DataFrame(altin_data)
    except:
        return pd.DataFrame({"Durum": ["Altın fiyatları şu an yüklenemedi. Daha sonra tekrar deneyin."]})


# --- 🏢 DURUM KONTROLÜ VE İÇERİK ---
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div class="kilit-uyari">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Analiz robotları ve sistem verileri şu an güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
else:
    if st.session_state["oda_kilitli_mi"]:
        st.warning("⚠️ Oda dışarıya kilitli fakat Yönetici olduğunuz için erişim sağladınız.")

    # =========================================================================
    # ⚡ YENİ NESİL ETKİLEŞİM PANELİ (ARAMA, ALTIN VE SOHBET SEKMELERİ)
    # =========================================================================
    sekme_arama, sekme_altin, sekme_sohbet = st.tabs(["🔎 BIST Arama Motoru", "🪙 Canlı Altın Takibi", "💬 Sohbet & Not Alanı"])
    
    with sekme_arama:
        st.markdown("### 🔎 BIST Hisse Arama")
        arama_kelimesi = st.text_input("Aratmak istediğiniz hisse kodunu yazın (Örn: THYAO):", "").strip().upper()
        
    with sekme_altin:
        st.markdown("### 🪙 Canlı Döviz ve Altın Piyasası")
        if st.button("🔄 Altın Fiyatlarını Güncelle"):
            st.toast("Altın fiyatları yenileniyor...", icon="🪙")
        df_altin = canli_altin_fiyatlari()
        st.table(df_altin)
        
    with sekme_sohbet:
        st.markdown("### 💬 Bilgi Paylaşım & Analiz Notları")
        sohbet_isim = st.text_input("Adınız:", value="Yatırımcı")
        sohbet_mesaj = st.text_input("Mesajınız:", placeholder="Analiz notunuzu veya sorunuzu yazın...")
        if st.button("✉️ Gönder"):
            if sohbet_mesaj.strip():
                zaman = datetime.datetime.now().strftime("%H:%M:%S")
                st.session_state["sohbet_gecmisi"].insert(0, f"[{zaman}] **{sohbet_isim}**: {sohbet_mesaj}")
                st.toast("Mesaj iletildi!", icon="💬")
        
        if st.session_state["sohbet_gecmisi"]:
            st.markdown("---")
            for msg in st.session_state["sohbet_gecmisi"][:10]:
                st.markdown(msg)

    st.markdown("---")

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

    # --- EN HIZLI VE SADE CANLI FİYAT MOTORU ---
    def hızlı_canli_fiyat_bul(hisse_kodu):
        if not hisse_kodu:
            return 0.0
        if hisse_kodu in st.session_state["fiyat_hafizasi"]:
            saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
            if time.time() - saved_time < 300:
                return saved_price
        try:
            hisse_data = yf.download(f"{hisse_kodu}.IS", period="1d", progress=False)
            if not hisse_data.empty:
