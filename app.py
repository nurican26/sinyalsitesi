import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# Şık Neon CSS Tasarımı
st.markdown("""
<style>
    @import url('https://googleapis.com');

    @keyframes rainbowNeon {
        0% { color: #ff007f !important; text-shadow: 0 0 15px #ff007f, 0 0 30px #ff007f; }
        25% { color: #00f2fe !important; text-shadow: 0 0 15px #00f2fe, 0 0 30px #00f2fe; }
        50% { color: #10b981 !important; text-shadow: 0 0 15px #10b981, 0 0 30px #10b981; }
        75% { color: #a855f7 !important; text-shadow: 0 0 15px #a855f7, 0 0 30px #a855f7; }
        100% { color: #ff007f !important; text-shadow: 0 0 15px #ff007f, 0 0 30px #ff007f; }
    }

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

# Önbellek Bellek Yapıları
if "oda_kilitli_mi" not in st.session_state:
    st.session_state["oda_kilitli_mi"] = False
if "sohbet_gecmisi" not in st.session_state:
    st.session_state["sohbet_gecmisi"] = []

# Logo Alanı
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# --- ⚠️ SPK YASAL UYARI BÖLÜMÜ ---
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

# 🛠️ SOL YAN MENÜ: YÖNETİCİ PANELİ
st.sidebar.markdown("### 🛠️ Oda Yönetim Merkezi")
admin_sifre = st.sidebar.text_input("Yönetici Şifresi:", type="password", placeholder="Şifre girin...")

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
    if admin_sifre:
        st.sidebar.error("Hatalı Yönetici Şifresi!")

# --- CANLI ALTIN HESAPLAMA MOTORU ---
def canli_altin_fiyatlari_al():
    try:
        altin_veri = yf.download(["GC=F", "TRY=X"], period="1d", progress=False)['Close']
        ons_fiyat = float(altin_veri["GC=F"].dropna().iloc[-1])
        usd_kur = float(altin_veri["TRY=X"].dropna().iloc[-1])
        gram_altin = (ons_fiyat / 31.1034768) * usd_kur
        
        return pd.DataFrame({
            "Altın Türü 🪙": ["Gram Altın", "Çeyrek Altın (1.75g)", "Yarım Altın (3.50g)", "Tam Altın (7.01g)"],
            "Güncel Fiyat (TL) 💰": [
                f"{round(gram_altin, 2):,}".replace(",", "."),
                f"{round(gram_altin * 1.75, 2):,}".replace(",", "."),
                f"{round(gram_altin * 3.50, 2):,}".replace(",", "."),
                f"{round(gram_altin * 7.01, 2):,}".replace(",", ".")
            ]
        })
    except:
        return pd.DataFrame({"Durum": ["Altın fiyatları geçici olarak yüklenemedi."]})

# ODA KİLİT KONTROLÜ
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div class="kilit-uyari">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Sistem verileri güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
else:
    if st.session_state["oda_kilitli_mi"]:
        st.warning("⚠️ Oda dışarıya kilitli fakat Yönetici olduğunuz için içeriyi görüyorsunuz.")

    # =========================================================================
    # TAB PANEL SİSTEMİ (ARAMA, ALTIN VE SOHBET)
    # =========================================================================
    sekme_arama, sekme_altin, sekme_sohbet = st.tabs(["🔎 BIST Arama Motoru", "🪙 Canlı Altın Takibi", "💬 Sohbet & Not Alanı"])
    
    with sekme_arama:
        st.markdown("### 🔎 BIST Hisse Arama")
        arama_kelimesi = st.text_input("Aratmak istediğiniz hisse kodunu girin (Örn: THYAO):", "").strip().upper()
        
    with sekme_altin:
        st.markdown("### 🪙 Canlı Döviz ve Altın Piyasası")
        if st.button("🔄 Fiyatları Güncelle"):
            st.toast("Fiyatlar yenileniyor...", icon="🪙")
        st.table(canli_altin_fiyatlari_al())
        
    with sekme_sohbet:
        st.markdown("### 💬 Bilgi Paylaşım & Analiz Notları")
        sohbet_isim = st.text_input("Adınız:", value="Yatırımcı")
        sohbet_mesaj = st.text_input("Mesajınız:", placeholder="Analiz notunuzu buraya yazın...")
        if st.button("✉️ Gönder") and sohbet_mesaj.strip():
            zaman = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state["sohbet_gecmisi"].insert(0, f"[{zaman}] **{sohbet_isim}**: {sohbet_mesaj}")
            st.toast("Mesaj iletildi!", icon="💬")
        
        if st.session_state["sohbet_gecmisi"]:
            st.markdown("---")
            for msg in st.session_state["sohbet_gecmisi"][:10]:
                st.markdown(msg)

    st.markdown("---")

    # =========================================================================
    # YENİ NESİL TOPLU VERİ İŞLEME MOTORU (SIFIR HATA VE YÜKSEK HIZ)
    # =========================================================================
    excel_yolu = "nurican.xls.xlsm"
    
    if os.path.exists(excel_yolu):
        try:
            df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
            
            raw_rows = []
            toplu_kodlar = []
            
            # 1. Excel Satırlarını tara ve benzersiz hisse listesini hafızaya topla
            for idx in range(2, len(df_kaynak)):
                if len(df_kaynak.columns) > 22:
                    uv = str(df_kaynak.iloc[idx, 20]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 20]) else ""
                    wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 22]) else ""
                    t_puan = str(df_kaynak.iloc[idx, 19]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 19]) else "0.0"
                    
                    raw_rows.append({"uv": uv, "wv": wv, "t_puan": t_puan})
                    if uv and uv not in ["NAN", "NONE", "AL_SAT SİNYALİ"]: 
                        toplu_kodlar.append(f"{uv}.IS")
                    if wv and wv not in ["NAN", "NONE", "W_SÜTUNU"]: 
                        toplu_kodlar.append(f"{wv}.IS")
            
            # 2. Tüm internet fiyatlarını tek bir saniyede tek parça indir
            toplu_kodlar = list(set(toplu_kodlar))
            fiyat_sozlugu = {}
            
            if toplu_kodlar:
                try:
