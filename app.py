import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os
from datetime import datetime

# ==========================================
# 1. SAYFA, PANEL VE ÖZEL GÖRSEL TEMA AYARLARI
# ==========================================
st.set_page_config(
    page_title="BTA Algoritmik İşlem ve Analiz Portালী",
    page_icon="🧠",
    layout="wide"
)

# Arka Plan ve Neon Çizgiler için Özel CSS Tasarımı
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle, #0e1118 0%, #05070a 100%) !important;
        color: #ffffff !important;
    }
    .bta-header-box {
        background: linear-gradient(135deg, #151b26 0%, #0a0f18 100%) !important;
        padding: 20px; 
        border-radius: 15px; 
        border: 2px solid #00f2fe !important;
        box-shadow: 0px 0px 20px #00f2fe, inset 0px 0px 15px rgba(0, 242, 254, 0.2);
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
    }
    .bta-marquee-text {
        font-family: 'Pacifico', cursive !important; 
        font-size: 40px !important; 
        color: #fffb00 !important; 
        text-shadow: 0 0 10px #fffb00, 0 0 20px #ff6c00 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #111622 !important;
        border: 1px solid #1f293d !important;
        border-radius: 8px 8px 0px 0px !important;
        padding: 10px 20px !important;
        color: #8892b0 !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #162235 !important;
        color: #00f2fe !important;
        border-color: #00f2fe !important;
        border-bottom: 2px solid #00f2fe !important;
    }
    </style>
    <link rel="preconnect" href="https://googleapis.com">
    <link rel="preconnect" href="https://gstatic.com" crossorigin>
    <link href="https://googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True
)

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"user": "Sistem", "time": "12:00:00", "text": "BTA Algoritmik Canlı Sohbet Odasına Hoş Geldiniz!"}
    ]

if "bta_members_list" not in st.session_state:
    st.session_state["bta_members_list"] = [
        {"id": 8888, "Hissedar Adı": "Nurican Bey", "Sahip Olduğu BTA Hissesi": "KONYA.IS", "Hisse Maliyeti (TL)": 4100.0, "Adet": 10}
    ]

spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

st.sidebar.header("⚙️ Sistem Kontrolleri")
st.sidebar.subheader("🔒 Yönetici Alanı")
admin_pass = st.sidebar.text_input("Yönetici Şifresi:", type="password")
is_admin = (admin_pass == "BTA2026")

if is_admin:
    st.sidebar.success("⚡ Yönetici Yetkileri Aktif!")

auto_refresh = st.sidebar.checkbox("Otomatik Yenilemeyi Aktif Et", value=True)
if auto_refresh:
    st_autorefresh(interval=5000, key="bta_refresh_counter")

st.sidebar.markdown("---")
st.sidebar.warning(spk_metni)

excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]

st.markdown(
    """
    <div class="bta-header-box">
        <marquee behavior="alternate" scrollamount="4">
            <span class="bta-marquee-text">
                ⚡ 🧠 BTA Algoritmik İşlem ve Analiz Portalı 🧠 ⚡
            </span>
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

st.warning(spk_metni)
st.markdown("---")

tab_excel, tab_bta, tab_chat, tab_members = st.tabs([
    "📂 BTA Excel Veri Analizi", 
    "📈 KONYA Canlı Veri Odası", 
    "💬 Canlı Sohbet Odası",
    "👥 BTA Hissedarları Kayıt Listesi"
])

# ==========================================
# MODÜL 1: EXCEL VERİ İNCELEME
# ==========================================
with tab_excel:
    st.header("📂 Excel Veri İnceleme Merkezi")
    
    secilen_dosya = None
    if excel_dosyalari:
        secilen_dosya = excel_dosyalari

    if is_admin:
        st.subheader("🛠️ Yönetici Excel Kontrolleri")
        dosya_kaynagi = st.radio("Dosya Kaynağı Seçin:", ["Klasördeki Dosyaları Kullan", "Yeni Dosya Yükle"])
        if dosya_kaynagi == "Klasördeki Dosyaları Kullan" and excel_dosyalari:
            secilen_dosya = st.selectbox("Analiz Edilecek Dosya:", excel_dosyalari)
        else:
            secilen_dosya = st.file_uploader("Bir Excel (.xlsx, .xlsm) dosyası yükleyin", type=["xlsx", "xlsm"])
        st.markdown("---")

    if secilen_dosya is not None:
        try:
            excel_obj = pd.ExcelFile(secilen_dosya, engine='openpyxl')
            sayfa_isimleri = excel_obj.sheet_names
            aktif_sayfa = sayfa_isimleri
            if is_admin and len(sayfa_isimleri) > 1:
                aktif_sayfa = st.selectbox("Görüntülenecek Sayfa (Yönetici):", sayfa_isimleri)
                
            df_orjinal = pd.read_excel(secilen_dosya, sheet_name=aktif_sayfa, engine='openpyxl')
            
            # NOKTA ATIŞI A, C VE D SÜTUNLARINI SEÇME MANTIĞI
            hedef_sutunlar = ["BTA HİSSE", "BTA ALIM FİYATI", "BTA PUANI"]
            mevcut_sutunlar = [col for col in hedef_sutunlar if col in df_orjinal.columns]
            
            if mevcut_sutunlar:
                df_goster = df_orjinal[mevcut_sutunlar]
            else:
                # İsim eşleşmesi yoksa Excel'in 0, 2 ve 3. indeksli sütunlarını çek
                indeksler = [0, 2, 3]
                gecerli_indeksler = [i for i in indeksler if i < len(df_orjinal.columns)]
                df_goster = df_orjinal.iloc[:, gecerli_indeksler]
            
            # Boşlukları ve None ifadelerini tamamen temizleme
            df_goster = df_goster.fillna("")
            df_goster = df_goster.astype(str).replace(["None", "NaN", "nan", "NaT", "nat"], "")
            
            arama_kelimesi = st.text_input("Tablo içinde dinamik filtreleme yapın:", value="")
            if arama_kelimesi:
                filtre_mask = df_goster.apply(lambda x: x.str.contains(arama_kelimesi, case=False)).any(axis=1)
                gosterilecek_df = df_goster[filtre_mask]
            else:
                gosterilecek_df = df_goster
                
            st.dataframe(gosterilecek_df, use_container_width=True)
        except Exception as e:
            st.error(f"Excel verisi işlenirken bir hata oluştu: {e}")
    else:
        st.info("💡 Sistemde yüklü veya klasörde analiz edilecek Excel dosyası bulunamadı.")

# ==========================================
# MODÜL 2: KONYA CANLI TAKİP
# ==========================================
with tab_bta:
    st.header("📈 KONYA Hisse Senedi Canlı Kar/Zarar Takip Paneli")
    kurumsal_ticker = "KONYA.IS"
    bta_alim_fiyati = 4100.00 
    
    tarihce = pd.DataFrame()
    gunluk_degisim_yuzde = 0.0
    guncel_fta_fiyati = 0.0
    canli_veri_hatasi = False
    
    try:
        hisse = yf.Ticker(kurumsal_ticker)
        tarihce = hisse.history(period="2d", interval="1d")
        if not tarihce.empty:
            guncel_fta_fiyati = tarihce['Close'].iloc[-1]
            gunluk_degisim_yuzde = hisse.info.get('regularMarketChangePercent', 0.0)
    except Exception as e:
        canli_veri_hatasi = True

    if canli_veri_hatasi:
        st.error("Canlı takip motorunda teknik bir aksaklık oluştu veya sunucuya erişilemedi.")
    elif tarihce.empty:
        st.warning("Borsa İstanbul canlı veri sunucularından anlık KONYA verisi şu an alınamadı.")
    else:
        if gunluk_degisim_yuzde == 0.0 and len(tarihce) > 1:
            onceki_kapanis = tarihce['Close'].iloc[-2]
            gunluk_degisim_yuzde = ((guncel_fta_fiyati - onceki_kapanis) / onceki_kapanis) * 100
        
        kar_zarar_tutari = guncel_fta_fiyati - bta_alim_fiyati
        kar_zarar_yuzdesi = (kar_zarar_tutari / bta_alim_fiyati) * 100
        
        if gunluk_degisim_yuzde >= 9.90 or kar_zarar_yuzdesi >= 9.0:
            st.balloons()
            st.snow()
            st.success("🚀 **ODADA KUTLAMALAR BAŞLASIN! KONYA HİSSESİ ANLIK OLARAK TAVAN OLDU VEYA +%9 KAR MARJINI AŞTI!** 🥳🎉")
            
        st.subheader("📊 Canlı Hesap Tablosu ve Portföy Durumu")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Anlık Canlı FTA Fiyatı", f"{guncel_fta_fiyati:.2f} TL", f"{gunluk_degisim_yuzde:.2f}% (Günlük)")
        c2.metric("Sizin Alım Maliyetiniz", f"{bta_alim_fiyati:.2f} TL")
        
        if kar_zarar_tutari >= 0:
            c3.metric("Net Kar/Zarar Durumu (TL)", f"+{kar_zarar_tutari:.2f} TL")
            c4.metric("Toplam Kar Oranınız", f"+% {kar_zarar_yuzdesi:.2f}")
        else:
            c3.metric("Net Kar/Zarar Durumu (TL)", f"{kar_zarar_tutari:.2f} TL")
            c4.metric("Toplam Zarar Oranınız", f"% {kar_zarar_yuzdesi:.2f}")

# ==========================================
# MODÜL 3: CANLI SOHBET ODASI
# ==========================================
with tab_chat:
    st.header("💬 BTA Genel Canlı Sohbet Odası")
    nickname = st.text_input("Sohbet Takma Adınız:", value="Hissedar", key="chat_nick")
    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_input("Mesajınızı yazın:")
