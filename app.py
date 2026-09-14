import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os
import json
from datetime import datetime

# ==========================================
# 1. SAYFA VE PANEL AYARLARI
# ==========================================
st.set_page_config(
    page_title="BTA Algoritmik İşlem ve Analiz Portalı",
    page_icon="🧠",
    layout="wide"
)

if "global_bta_price" not in st.session_state:
    st.session_state["global_bta_price"] = 4100.0

# SPK RESMİ YASAL UYARI METNİ
spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# ==========================================
# 🌌 TRADINGVIEW TARZI BORSA TERMİNALİ TEMASI (CSS ENJEKSİYONU)
# ==========================================
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0c0f14 !important;
        color: #d1d4dc !important;
    }
    .stApp {
        background-color: #0c0f14 !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #d1d4dc !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: #131722;
        padding: 8px;
        border-radius: 6px;
        border: 1px solid #2a2e39;
    }
    .stTabs [data-baseweb="tab"] {
        color: #787b86 !important;
        font-weight: 600;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        color: #2962ff !important;
        background-color: #1e222d;
        border-radius: 4px;
    }
    .borsa-kart {
        background-color: #131722;
        border: 1px solid #2a2e39;
        border-left: 4px solid #089981;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 %100 KALICI JSON PORTFÖY VERİTABANI MOTORU
# ==========================================
PORTFOY_DOSYASI = "bta_portfoy_hafiza.json"

if "bta_members_list" not in st.session_state:
    if os.path.exists(PORTFOY_DOSYASI):
        try:
            with open(PORTFOY_DOSYASI, "r", encoding="utf-8") as f:
                st.session_state["bta_members_list"] = json.load(f)
        except:
            st.session_state["bta_members_list"] = []
    else:
        st.session_state["bta_members_list"] = [
            {"id": 8888, "Hissedar Adı": "Nurican Bey", "Sahip Olduğu BTA Hissesi": "KONYA.IS", "Hisse Maliyeti (TL)": 4100.0, "Adet": 10}
        ]

if "begeniler" not in st.session_state:
    st.session_state["begeniler"] = 0
if "yildizlar" not in st.session_state:
    st.session_state["yildizlar"] = 5.0

# ==========================================
# 2. SABİT SOL MENÜ (SIDEBAR) & GÜVENLİK
# ==========================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

admin_pass = st.sidebar.text_input("Yönetici Şifresi:", type="password", help="Excel yönetimini ve silme araçlarını açar.")
is_admin = (admin_pass == "BTA2026")

if is_admin:
    st.sidebar.success("⚡ Yönetici Yetkileri Aktif!")

auto_refresh = st.sidebar.checkbox("Otomatik Yenilemeyi Aktif Et", value=True)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Yenileme Sıklığı (Saniye)", 2, 60, 5)
    st_autorefresh(interval=refresh_interval * 1000, key="bta_refresh_counter")

st.sidebar.markdown("---")
st.sidebar.warning(spk_metni)

excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]
varsayilan_dosya = None
if excel_dosyalari:
    hedef_dosyalar = [f for f in excel_dosyalari if "bta" in f.lower() or "nurican" in f.lower()]
    varsayilan_dosya = hedef_dosyalar if hedef_dosyalar else excel_dosyalari

# ==========================================
# 3. ANA PANEL BAŞLIĞI & EN ÜST SPK UYARISI
# ==========================================
st.title("🧠 BTA Algoritmik İşlem ve Analiz Portalı")
st.warning(spk_metni)
st.markdown("---")

tab_excel, tab_bta, tab_members = st.tabs([
    "📂 BTA Excel Veri Analizi", 
    "📈 KONYA Canlı Veri Odası", 
    "👥 BTA Hissedarları Kayıt Listesi"
])

# ==========================================
# MODÜL 1: EXCEL VERİ İŞLEME (A, C, D SÜTUNLARI TAM LİSTE)
# ==========================================
with tab_excel:
    st.header("📂 Excel Veri Inceleme Merkezi")
    secilen_dosya = varsayilan_dosya
    
    if is_admin:
        st.subheader("🛠️ Yönetici Excel Kontrolleri")
        dosya_kaynagi = st.radio("Dosya Kaynağı Seçin:", ["Klasördeki Dosyaları Kullan", "Yeni Dosya Yükle"])
        if dosya_kaynagi == "Klasördeki Dosyaları Kullan" and excel_dosyalari:
            secilen_dosya = st.selectbox("Analiz Edilecek Dosya:", excel_dosyalari, index=excel_dosyalari.index(varsayilan_dosya) if varsayilan_dosya in excel_dosyalari else 0)
        else:
            secilen_dosya = f = st.file_uploader("Bir Excel (.xlsx, .xlsm) dosyası yükleyin", type=["xlsx", "xlsm"])
        st.markdown("---")

    if secilen_dosya is not None:
        try:
            df = pd.read_excel(secilen_dosya, sheet_name=0, engine='openpyxl')
            df.columns = df.columns.astype(str).str.strip()
            
            istenan_sutunlar = ["BTA HİSSE", "BTA ALIM FİYATI", "BTA PUAN"]
            mevcut_istenenler = [col for col in df.columns if col in istenan_sutunlar]
            
            df_goster = df[mevcut_istenenler] if mevcut_istenenler else df
            df_goster = df_goster.dropna(how='all')
            
            if "BTA HİSSE" in df_goster.columns and "BTA ALIM FİYATI" in df_goster.columns:
                konya_satirlari = df_goster[df_goster["BTA HİSSE"].astype(str).str.upper().str.strip() == "KONYA"]
                if not konya_satirlari.empty:
                    st.session_state["global_bta_price"] = float(konya_satirlari["BTA ALIM FİYATI"].iloc)
            
            st.dataframe(df_goster, use_container_width=True)
        except Exception as e:
            st.error(f"Excel verisi işlenirken bir hata oluştu: {e}")
    else:
        st.info("💡 Sistemde analiz edilecek Excel dosyası bulunamadı.")

# ==========================================
# MODÜL 2: KONYA CANLI TAKİP PANELİ (15 DK GECİKME UYARISI EKLENDİ)
# ==========================================
with tab_bta:
    st.header("📈 KONYA Hisse Senedi Canlı Kar/Zarar Takip Paneli")
    bta_alim_fiyati = st.session_state["global_bta_price"]
    kurumsal_ticker = "KONYA.IS"
    
    guncel_fta_fiyati = bta_alim_fiyati
    gunluk_degisim_yuzde = 0.0
    borsa_verisi_tamam = False
    tarihce = pd.DataFrame()
    
    try:
        hisse = yf.Ticker(kurumsal_ticker)
        tarihce = hisse.history(period="2d", interval="1d")
        if not tarihce.empty:
            guncel_fta_fiyati = tarihce['Close'].iloc[-1]
            gunluk_degisim_yuzde = hisse.info.get('regularMarketChangePercent', 0.0)
            if gunluk_degisim_yuzde == 0.0 and len(tarihce) > 1:
                onceki_kapanis = tarihce['Close'].iloc[-2]
                gunluk_degisim_yuzde = ((guncel_fta_fiyati - onceki_kapanis) / onceki_kapanis) * 100
            borsa_verisi_tamam = True
    except:
        pass

    if borsa_verisi_tamam:
        kar_zarar_tutari = guncel_fta_fiyati - bta_alim_fiyati
        kar_zarar_yuzdesi = (kar_zarar_tutari / bta_alim_fiyati) * 100
        
        if gunluk_degisim_yuzde >= 9.90 or kar_zarar_yuzdesi >= 9.0:
            st.balloons()
            st.snow()
            st.success("🚀 **ODADA KUTLAMALAR BAŞLASIN! KONYA HİSSESİ ANLIK OLARAK TAVAN OLDU VEYA +%9 KAR MARJINI AŞTI!** 🥳🎉")
        
        st.subheader("📊 Canlı Hesap Tablosu")
        # 🔔 İSTEK: Borsa İstanbul yasal kuralları gereği 15 dakika gecikme ibaresi eklendi
        st.warning("⏱️ Borsa İstanbul (BIST) verileri yasal mevzuatlar gereği en az **15 dakika gecikmeli** olarak yansımaktadır.")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Anlık Canlı FTA Fiyatı", f"{guncel_fta_fiyati:.2f} TL", f"{gunluk_degisim_yuzde:.2f}% (Günlük)")
        c2.metric("Excel'den Gelen Otomatik Alım Fiyatı", f"{bta_alim_fiyati:.2f} TL")
        
        if kar_zarar_tutari >= 0:
            c3.metric("Net Kar/Zarar Durumu (TL)", f"+{kar_zarar_tutari:.2f} TL")
            c4.metric("Toplam Kar Oranınız", f"+% {kar_zarar_yuzdesi:.2f}")
        else:
            c3.metric("Net Kar/Zarar Durumu (TL)", f"{kar_zarar_tutari:.2f} TL")
            c4.metric("Toplam Zarar Oranınız", f"% {kar_zarar_yuzdesi:.2f}")
            
        st.markdown("---")
        st.subheader("⭐ Oda Değerlendirmesi & Topluluk Reaksiyonu")
        
        st.write(f"👍 Toplam Oda Beğenisi: **{st.session_state['begeniler']}**")
        if st.button("Portföyü Beğen 👍", key="like_btn"):
            st.session_state["begeniler"] += 1
            st.rerun()
            
        st.session_state["yildizlar"] = st.slider("Algoritmaya Yıldız Ver:", 1.0, 5.0, float(st.session_state["yildizlar"]), step=0.5)
                
        st.subheader("📊 KONYA - Gün İçi Canlı Fiyat Grafik Trendi")
        st.line_chart(tarihce['Close'])
    else:
        st.warning("⚠️ Borsa İstanbul canlı veri sunucularından anlık KONYA verisi şu an alınamadı.")

# ==========================================
