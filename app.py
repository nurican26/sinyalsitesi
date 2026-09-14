import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os
import sqlite3
from datetime import datetime

# ==========================================
# 0. KALICI VERİTABANI BAĞLANTISI (SQLite)
# ==========================================
def veritabanini_hazirla():
    conn = sqlite3.connect("bta_kurumsal_veri.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sohbet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            time TEXT,
            text TEXT
        )
    """)
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

admin_pass = st.sidebar.text_input("Yönetici Şifresi:", type="password", help="Excel yönetimini, mesaj silmeyi ve kayıt düzenlemeyi açar.")
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

# ==========================================
# 3. ANA PANEL BAŞLIĞI & EN ÜST SPK UYARISI
# ==========================================
st.title("🧠 BTA Algoritmik İşlem ve Analiz Portalı")
st.warning(spk_metni)
st.markdown("---")

tab_excel, tab_bta, tab_chat, tab_members = st.tabs([
    "📂 BTA Excel Veri Analizi", 
    "📈 KONYA Canlı Veri Odası", 
    "💬 Canlı Sohbet Odası",
    "👥 BTA Hissedarları Kayıt Listesi"
])

# ==========================================
# MODÜL 1: EXCEL & MAKRO VERİ İŞLEME (A, C, D KOLONLARI)
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
            df = pd.read_excel(secilen_dosya, sheet_name=0, engine='openpyxl')
            df.columns = df.columns.astype(str).str.strip()
            
            istenen_sutunlar = ["BTA HİSSE", "BTA ALIM FİYATI", "BTA PUAN"]
            mevcut_istenenler = [col for col in df.columns if col in istenen_sutunlar]
            
            if mevcut_istenenler:
                df_goster = df[mevcut_istenenler]
            else:
                df_goster = df
            
            df_goster = df_goster.dropna(how='all')
            
            if "BTA HİSSE" in df_goster.columns and "BTA ALIM FİYATI" in df_goster.columns:
                konya_satirlari = df_goster[df_goster["BTA HİSSE"].astype(str).str.upper().str.strip() == "KONYA"]
                if not konya_satirlari.empty:
                    st.session_state["global_bta_price"] = float(konya_satirlari["BTA ALIM FİYATI"].iloc[0])
            
            st.dataframe(df_goster, use_container_width=True)
            
        except Exception as e:
            st.error(f"Excel verisi işlenirken bir hata oluştu: {e}")
else:
    st.info("💡 Sistemde yüklü veya klasörde analiz edilecek Excel dosyası bulunamadı.")

# ==========================================
# MODÜL 2: KONYA CANLI TAKİP PANELİ (GÜVENLİ VE HİZALANMIŞ SÜRÜM)
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
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Anlık Canlı FTA Fiyatı", f"{guncel_fta_fiyati:.2f} TL", f"{gunluk_degisim_yuzde:.2f}% (Günlük)")
            c2.metric("Excel'den Gelen Otomatik Alım Fiyatı", f"{bta_alim_fiyati:.2f} TL")
            
            if kar_zarar_tutari >= 0:
                c3.metric("Net Kar/Zarar Durumu (TL)", f"+{kar_zarar_tutari:.2f} TL")
                c4.metric("Toplam Kar Oranınız", f"+% {kar_zarar_yuzdesi:.2f}")
            else:
                c3.metric("Net Kar/Zarar Durumu (TL)", f"{kar_zarar_tutari:.2f} TL")
                c4.metric("Toplam Zarar Oranınız", f"% {kar_zarar_yuzdesi:.2f}")
                
            st.subheader("📊 KONYA - Gün İçi Canlı Fiyat Grafik Trendi")
            st.line_chart(tarihce['Close'])
        else:
            st.warning("Borsa İstanbul canlı veri sunucularından anlık KONYA verisi şu an alınamadı.")
            
    except Exception as borsa_hatasi:
        st.error(f"Canlı takip motorunda teknik bir aksaklık oluştu: {borsa_hatasi}")

# ==========================================
# MODÜL 3: CANLI SOHBET ODASI
# ==========================================
with tab_chat:
    st.header("💬 BTA Genel Canlı Sohbet Odası")
    st.write("Sohbet odası veritabanı desteklidir, yenilendiğinde mesajlar asla kaybolmaz.")
