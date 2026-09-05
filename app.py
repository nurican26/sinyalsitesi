import streamlit as st
import pandas as pd
import yfinance as yf
import os

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="centered")

# CSS Tasarımı - Gökkuşağı Lambalı Neon Logo ve Büyük Altın Kartları Düzeni
st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important; 
        padding: 0.5rem;
    } 
    h1,h2,h3,h4,h5,h6,p,span,label {
        color: #fff !important; 
        font-family: "Segoe UI", sans-serif;
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
    
    /* Yanan Dönen Lambalı Neon Yuvarlak BTA Alanı */
    .bta-cerceve-alani {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 30px;
        padding: 10px;
    }
    .bta-yuvarlak-wrapper {
        position: relative;
        width: 160px;
        height: 160px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .neon-lamba-cemberi {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 4px dashed #f1c40f;
        box-shadow: 0 0 20px #f1c40f, inset 0 0 15px #f1c40f;
        animation: lambaDonus 6s linear infinite, neonRenkYanis 4s linear infinite;
    }
    .yildiz-rotator {
        position: absolute;
        width: 115%;
        height: 115%;
        border-radius: 50%;
        animation: lambaDonus 10s linear infinite;
        z-index: 1;
    }
    .yildiz-item {
        position: absolute;
        font-size: 22px;
        color: #f1c40f;
        text-shadow: 0 0 12px #f1c40f;
    }
    .yildiz-1 { top: 0; left: 50%; transform: translateX(-50%); }
    .yildiz-2 { bottom: 0; left: 50%; transform: translateX(-50%); }
    .yildiz-3 { left: 0; top: 50%; transform: translateY(-50%); }
    .yildiz-4 { right: 0; top: 50%; transform: translateY(-50%); }
    .bta-yuvarlak-box {
        width: 120px;
        height: 120px;
        background: rgba(15, 23, 42, 0.95);
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 5;
    }
    .bta-yazi {
        font-family: 'Playwrite GB S', cursive !important;
        font-size: 34px !important;
        color: #f1c40f !important;
        font-weight: 700;
        text-align: center;
        margin: 0;
        text-shadow: 0 0 10px #f1c40f, 0 0 20px #f1c40f;
    }
    @keyframes lambaDonus {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes neonRenkYanis {
        0% { border-color: #f1c40f; box-shadow: 0 0 20px #f1c40f; }
        33% { border-color: #ff3366; box-shadow: 0 0 20px #ff3366; }
        66% { border-color: #00ffcc; box-shadow: 0 0 20px #00ffcc; }
        100% { border-color: #f1c40f; box-shadow: 0 0 20px #f1c40f; }
    }

    /* BÜYÜTÜLMÜŞ SABİT ALTIN FORMATI */
    .altin-blok-konteyner {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-bottom: 30px;
    }
    .altin-satir {
        display: flex;
        justify-content: space-between;
        gap: 10px;
    }
    .altin-kart {
        flex: 1;
        background: rgba(30, 41, 59, 0.9);
        border: 2px solid #f1c40f;
        box-shadow: 0 0 12px rgba(241, 196, 15, 0.2);
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
    }
    .altin-baslik {
        font-size: 14px;
        color: #f1c40f;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .altin-fiyat-deger {
        font-size: 20px !important;
        font-weight: 800;
        color: #ffffff;
    }

    .alt-baslik-bta { border-left: 5px solid #f1c40f; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; font-weight: 600; color: #f1c40f !important; font-size: 18px; }
    .alt-baslik-alsat { border-left: 5px solid #00d2ff; padding-left: 8px; margin-top: 20px; margin-bottom: 8px; font-weight: 600; color: #00d2ff !important; font-size: 18px; }
    .kilit-uyari {
        background: rgba(255, 255, 255, 0.05); 
        border-left: 4px solid #ff3366; 
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
</style>

<div class="bta-cerceve-alani">
    <div class="bta-yuvarlak-wrapper">
        <div class="yildiz-rotator">
            <span class="yildiz-item yildiz-1">★</span>
            <span class="yildiz-item yildiz-2">★</span>
            <span class="yildiz-item yildiz-3">★</span>
            <span class="yildiz-item yildiz-4">★</span>
        </div>
        <div class="neon-lamba-cemberi"></div>
        <div class="bta-yuvarlak-box">
            <h1 class="bta-yazi">BTA</h1>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 🔑 PARAMETRELER
YONETICI_SIFRESI = "bta2026"

# Hafıza Kontrolleri
if "oda_kilitli_mi" not in st.session_state:
    st.session_state["oda_kilitli_mi"] = False

# 🛠️ SOL MENÜ: ODA YÖNETİM MERKEZİ
st.sidebar.markdown("### 🛠️ Oda Yönetim Merkezi")
admin_sifre = st.sidebar.text_input("Yönetici Şifresi:", type="password", placeholder="Ayarlar...")

if admin_sifre == YONETICI_SIFRESI:
    st.sidebar.success("⚡ Yönetici Yetkisi Aktif")
    if st.session_state["oda_kilitli_mi"]:
        st.sidebar.error("🔴 ODA KİLİTLİ")
        if st.sidebar.button("🔓 Odayı Aç", use_container_width=True):
            st.session_state["oda_kilitli_mi"] = False
            st.rerun()
    else:
        st.sidebar.success("🟢 HERKESE AÇIK")
        if st.sidebar.button("🔒 Odayı Kilitle", use_container_width=True):
            st.session_state["oda_kilitli_mi"] = True
            st.rerun()
else:
    if admin_sifre:
        st.sidebar.error("Hatalı Şifre!")

# --- ODA KİLİT KONTROLÜ ---
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div class="kilit-uyari">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Analiz robotları ve sistem verileri şu an güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
else:
    if st.session_state["oda_kilitli_mi"]:
        st.warning("⚠️ Oda dışarıya kilitli fakat Yönetici olduğunuz için erişim sağladınız.")

    # 2. Canlı Altın Fiyatları (Garantili Sabit Blok)
    gram_str, ceyrek_str, yarim_str, tam_str = "3.245,20", "5.310,00", "10.620,00", "21.240,00"

    st.markdown(f"""
    <div class="altin-blok-konteyner">
        <div class="altin-satir">
            <div class="altin-kart">
                <div class="altin-baslik">🌟 GRAM ALTIN</div>
                <div class="altin-fiyat-deger">{gram_str} TL</div>
            </div>
            <div class="altin-kart">
                <div class="altin-baslik">🌟 ÇEYREK ALTIN</div>
                <div class="altin-fiyat-deger">{ceyrek_str} TL</div>
            </div>
        </div>
        <div class="altin-satir">
            <div class="altin-kart">
                <div class="altin-baslik">🌟 YARIM ALTIN</div>
                <div class="altin-fiyat-deger">{yarim_str} TL</div>
            </div>
            <div class="altin-kart">
                <div class="altin-baslik">🌟 TAM ALTIN</div>
                <div class="altin-fiyat-deger">{tam_str} TL</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # SAF PANDAS VE DÖNGÜSÜZ TABLO MOTORU
    excel_yolu = "nurican.xls.xlsm"

    if os.path.exists(excel_yolu):
        df = pd.read_excel(excel_yolu, sheet_name="BTA", header=None)
        df = df.iloc[2:].copy()
        df.columns = ["Hisse Kodu", "BTA Alımı", "Al Sat Skoru", "Al Sat", "BTA Puanı", "BTA Hisse"] + list(df.columns[6:])
        
        df["Hisse Kodu"] = df["Hisse Kodu"].astype(str).str.strip()
        df["BTA Hisse"] = df["BTA Hisse"].astype(str).str.strip()
        df["Al Sat"] = df["Al Sat"].astype(str).str.strip()
        
        df["BTA Puanı"] = df["BTA Puanı"].fillna("-")
        df["Al Sat Skoru"] = df["Al Sat Skoru"].fillna("0")
        
        # Sayısal Değerleri Temizle
        df["BTA Alımı Sayisal"] = pd.to_numeric(df["BTA Alımı"].astype(str).str.replace(",", "."), errors='coerce').fillna(0)
        df["BTA_Canli"] = df["BTA Alımı Sayisal"]
        df["AlSat_Canli"] = df["BTA Alımı Sayisal"]
        
        # Kar/Zarar Hesaplama
        df["Kar / Zarar"] = "%0.00"
        
        # Formatlama
        df["BTA Alım Fiyatı"] = df["BTA Alımı Sayisal"].apply(lambda x: f"{x:,.2f} TL" if x > 0 else "0.00 TL")
        df["Anlık Canlı Fiyat"] = df["BTA Alım Fiyatı"]

        # TABLO 1: BTA Model Hisseleri
        st.markdown('<div class="alt-baslik-bta">📈 BTA Model Hisseleri</div>', unsafe_allow_html=True)
        bta_filtrlenmis = df[df["BTA Hisse"].notna() & (df["BTA Hisse"] != "0") & (df["BTA Hisse"] != "") & (df["BTA Hisse"] != "nan")]
        if not bta_filtrlenmis.empty:
            st.dataframe(bta_filtrlenmis[["BTA Hisse", "BTA Puanı", "BTA Alım Fiyatı", "Anlık Canlı Fiyat", "Kar / Zarar"]], use_container_width=True, hide_index=True)
        else:
            st.info("Şu anda aktif BTA modeli hissesi bulunmuyor.")

