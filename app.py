import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os
import sqlite3
from datetime import datetime

# ==========================================
# 0. KALICI VERİTABANI BAĞLANTISI (SQLite)
# (Sayfa yenilense bile sohbet ve kayıtlar asla silinmez)
# ==========================================
def veritabanini_hazirla():
    conn = sqlite3.connect("bta_kurumsal_veri.db", check_same_thread=False)
    cursor = conn.cursor()
    # Sohbet tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sohbet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            time TEXT,
            text TEXT
        )
    """)
    # Hissedar portföy tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hissedarlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT,
            hisse TEXT,
            maliyet REAL,
            adet INTEGER
        )
    """)
    conn.commit()
    conn.close()

veritabanini_hazirla()

def mesaj_ekle(user, time, text):
    conn = sqlite3.connect("bta_kurumsal_veri.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sohbet (user, time, text) VALUES (?, ?, ?)", (user, time, text))
    conn.commit()
    conn.close()

def mesajlari_getir():
    conn = sqlite3.connect("bta_kurumsal_veri.db")
    df = pd.read_sql_query("SELECT * FROM sohbet ORDER BY id DESC", conn)
    conn.close()
    return df.to_dict(orient="records")

def mesaj_sil(msg_id):
    conn = sqlite3.connect("bta_kurumsal_veri.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sohbet WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()

def hissedar_ekle(isim, hisse, maliyet, adet):
    conn = sqlite3.connect("bta_kurumsal_veri.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hissedarlar (isim, hisse, maliyet, adet) VALUES (?, ?, ?, ?)", (isim, hisse, maliyet, adet))
    conn.commit()
    conn.close()

def hissedarlari_getir():
    conn = sqlite3.connect("bta_kurumsal_veri.db")
    df = pd.read_sql_query("SELECT * FROM hissedarlar ORDER BY id DESC", conn)
    conn.close()
    return df.to_dict(orient="records")

def hissedar_sil(member_id):
    conn = sqlite3.connect("bta_kurumsal_veri.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM hissedarlar WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

# ==========================================
# 1. SAYFA VE PANEL AYARLARI
# ==========================================
st.set_page_config(
    page_title="BTA Algoritmik İşlem ve Analiz Portalı",
    page_icon="🧠",
    layout="wide"
)

# Global BTA Fiyat Referansı yedek değeri
if "global_bta_price" not in st.session_state:
    st.session_state["global_bta_price"] = 4100.0

# ==========================================
# GÜVENLİ VE HATA VERMEYEN SPK YASAL METNİ
# ==========================================
spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# ==========================================
# 2. SABİT SOL MENÜ (SIDEBAR) & GÜVENLİK
# ==========================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

# GİZLİ YÖNETİCİ GİRİŞİ (Şifre: BTA2026)
st.sidebar.subheader("🔒 Yönetici Alanı")
admin_pass = st.sidebar.text_input("Yönetici Şifresi:", type="password", help="Excel yönetimini, mesaj silmeyi ve kayıt düzenlemeyi açar.")
is_admin = (admin_pass == "BTA2026")

if is_admin:
    st.sidebar.success("⚡ Yönetici Yetkileri Aktif!")

# Otomatik Yenileme Ayarı (5 saniyede bir veri tazeleme)
auto_refresh = st.sidebar.checkbox("Otomatik Yenilemeyi Aktif Et", value=True)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Yenileme Sıklığı (Saniye)", 2, 60, 5)
    st_autorefresh(interval=refresh_interval * 1000, key="bta_refresh_counter")

# Sol menü tabanına SPK uyarısını çakıyoruz
st.sidebar.markdown("---")
st.sidebar.warning(spk_metni)

# Klasördeki mevcut Excel/Macro dosyalarını algılama
excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]

# ==========================================
# 3. ANA PANEL BAŞLIĞI & EN ÜST SPK UYARISI
# ==========================================
st.title("🧠 BTA Algoritmik İşlem ve Analiz Portalı")
st.warning(spk_metni)
st.markdown("---")

# Sekmeli Menü Tasarımı
tab_excel, tab_bta, tab_chat, tab_members = st.tabs([
    "📂 BTA Excel Veri Analizi", 
    "📈 KONYA Canlı Veri Odası", 
    "💬 Canlı Sohbet Odası",
    "👥 BTA Hissedarları Kayıt Listesi"
])

# ==========================================
# MODÜL 1: EXCEL & MAKRO VERİ İŞLEME (A, C, D SÜTUNLARI EKSİKSİZ VERİ GERİ GETİRME)
# ==========================================
with tab_excel:
    st.header("📂 Excel Veri İnceleme Merkezi")
    varsayilan_dosya = None
    if excel_dosyalari:
        hedef_dosyalar = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm')) and ("bta" in f.lower() or "nurican" in f.lower())]
        if list(hedef_dosyalar):
            varsayilan_dosya = list(hedef_dosyalar)[0]
        else:
            varsayilan_dosya = excel_dosyalari[0]

    secilen_dosya = varsayilan_dosya
    
    if is_admin:
        st.subheader("🛠️ Yönetici Excel Kontrolleri")
        dosya_kaynagi = st.radio("Dosya Kaynağı Seçin:", ["Klasördeki Dosyaları Kullan", "Yeni Dosya Yükle"])
        if dosya_kaynagi == "Klasördeki Dosyaları Kullan" and excel_dosyalari:
            secilen_dosya = st.selectbox("Analiz Edilecek Dosya:", excel_dosyalari, index=excel_dosyalari.index(varsayilan_dosya) if varsayilan_dosya in excel_dosyalari else 0)
        else:
            secilen_dosya = st.file_uploader("Bir Excel (.xlsx, .xlsm) dosyası yükleyin", type=["xlsx", "xlsm"])
        st.markdown("---")

    if secilen_dosya is not None:
        try:
            # Excel dosyasını sözlük hatası vermeden güvenle DataFrame olarak çekiyoruz
            df = pd.read_excel(secilen_dosya, sheet_name=0, engine='openpyxl')
            
            # Sütun isimlerinin başındaki ve sonundaki boşlukları temizleyerek algılamayı garanti ediyoruz
            df.columns = df.columns.astype(str).str.strip()
            
            # 🚀 İSTEK: Sadece A, C ve D sütunları gösterilecek (BTA HİSSE, BTA ALIM FİYATI, BTA PUAN)
            istenen_sutunlar = ["BTA HİSSE", "BTA ALIM FİYATI", "BTA PUAN"]
            mevcut_istenenler = [col for col in df.columns if col in istenen_sutunlar]
            
            if mevcut_istenenler:
                df_goster = df[mevcut_istenenler]
            else:
                df_goster = df
            
            # Kaybolan satırları ve fiyatları geri getirmek için hücre bazlı esnek temizleme mimarisi
            # Sadece 'BTA HİSSE' sütunu tamamen boş veya kelime olarak 'None' olan gereksiz satırlar elenir
            if "BTA HİSSE" in df_goster.columns:
                df_goster = df_goster[df_goster["BTA HİSSE"].notna()]
                df_goster = df_goster[df_goster["BTA HİSSE"].astype(str).str.strip() != ""]
                df_goster = df_goster[df_goster["BTA HİSSE"].astype(str).str.upper() != "NONE"]
                
                # KONYA satırındaki BTA ALIM FİYATI değerini otomatik çekip canlı odaya bağlama algoritması
                konya_satirlari = df_goster[df_goster["BTA HİSSE"].astype(str).str.upper().str.strip() == "KONYA"]
                if not konya_satirlari.empty and "BTA ALIM FİYATI" in df_goster.columns:
                    st.session_state["global_bta_price"] = float(konya_satirlari["BTA ALIM FİYATI"].iloc[0])
            
            # Tüm hisselerinizi, fiyatları ve puanları içeren temizlenmiş A, C, D tablosunu listeliyoruz
            st.dataframe(df_goster, use_container_width=True)
            
        except Exception as e:
            st.error(f"Excel verisi işlenirken bir hata oluştu: {e}")
    else:
        st.info("💡 Sistemde yüklü veya klasörde analiz edilecek Excel dosyası bulunamadı.")

# ==========================================
# MODÜL 2: KONYA CANLI TAKİP PANELİ
# ==========================================
with tab_bta:
    st.header("📈 KONYA Hisse Senedi Canlı Kar/Zarar Takip Paneli")
    bta_alim_fiyati = st.session_state["global_bta_price"]
    kurumsal_ticker = "KONYA.IS"
    try:
        hisse = yf.Ticker(kurumsal_ticker)
        tarihce = hisse.history(period="2d", interval="1d")
        if not tarihce.empty:
            guncel_fta_fiyati = tarihce['Close'].iloc[-1]
            gunluk_degisim_yuzde = hisse.info.get('regularMarketChangePercent', 0.0)
            if gunluk_degisim_yuzde == 0.0 and len(tarihce) > 1:
                onceki_kapanis = tarihce['Close'].iloc[-2]
                gunluk_degisim_yuzde = ((guncel_fta_fiyati - onceki_kapanis) / onceki_kapanis) * 100
            
            kar_zarar_tutari = guncel_fta_fiyati - bta_alim_fiyati
            kar_zarar_yuzdesi = (kar_zarar_tutari / bta_alim_fiyati) * 100
            
            if gunluk_degisim_yuzde >= 9.90 or kar_zarar_yuzdesi >= 9.0:
                st.balloons()
                st.snow()
                st.success("🚀 **ODADA KUTLAMALAR BAŞLASIN! KONYA HİSSESİ ANLIK OLARAK TAVAN OLDU VEYA +%9 KAR MARJINI AŞTI!** 🥳🎉")
            
            st.subheader("📊 Canlı Hesap Tablosu (Excel'den Otomatik Çekilen Referansla)")
