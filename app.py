import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os
import sqlite3
from datetime import datetime

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

# SPK RESMİ YASAL UYARI METNİ
spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# ==========================================
# 🌌 PRO BORSA TERMİNALİ TASARIMI (HATASI DÜZELTİLEN ALAN)
# ==========================================
st.markdown("""
<style>
    /* Ana Arka Plan ve Borsa Terminali Efekti */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Courier New', Courier, monospace;
    }
    /* Sekme Başlık Modifikasyonu */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #161b22;
        padding: 10px;
        border-radius: 8px;
        border-bottom: 2px solid #238636;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8b949e !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        color: #58a6ff !important;
        border-bottom-color: #58a6ff !important;
    }
    /* Borsa Giriş Kartları Tasarımı */
    .borsa-kart {
        background: linear-gradient(135deg, #1f242c 0%, #161b22 100%);
        border-left: 5px solid #238636;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 0. KALICI GÜVENLİ VERİ MOTORU (SQLite)
# ==========================================
def db_baglan():
    return sqlite3.connect("bta_pro_hafiza.db", check_same_thread=False)

def db_hazirla():
    conn = db_baglan()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS sohbet (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, time TEXT, text TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS hissedarlar (id INTEGER PRIMARY KEY AUTOINCREMENT, isim TEXT, hisse TEXT, maliyet REAL, adet INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS reaksiyon (id INTEGER PRIMARY KEY, begeni_sayisi INTEGER, yildiz_puani REAL)")
    cursor.execute("INSERT OR IGNORE INTO reaksiyon (id, begeni_sayisi, yildiz_puani) VALUES (1, 0, 5.0)")
    conn.commit()
    conn.close()

db_hazirla()

def db_mesaj_ekle(user, time, text):
    conn = db_baglan()
    conn.cursor().execute("INSERT INTO sohbet (user, time, text) VALUES (?, ?, ?)", (user, time, text))
    conn.commit()
    conn.close()

def db_mesajlari_getir():
    conn = db_baglan()
    df = pd.read_sql_query("SELECT * FROM sohbet ORDER BY id DESC LIMIT 40", conn)
    conn.close()
    return df.to_dict(orient="records")

def db_mesaj_sil(msg_id):
    conn = db_baglan()
    conn.cursor().execute("DELETE FROM sohbet WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()

def db_hissedar_ekle(isim, hisse, maliyet, adet):
    conn = db_baglan()
    conn.cursor().execute("INSERT INTO hissedarlar (isim, hisse, maliyet, adet) VALUES (?, ?, ?, ?)", (isim, hisse, maliyet, adet))
    conn.commit()
    conn.close()

def db_hissedarlari_getir():
    conn = db_baglan()
    df = pd.read_sql_query("SELECT * FROM hissedarlar ORDER BY id DESC", conn)
    conn.close()
    return df.to_dict(orient="records")

def db_hissedar_sil(member_id):
    conn = db_baglan()
    conn.cursor().execute("DELETE FROM hissedarlar WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

def reaksiyon_getir():
    conn = db_baglan()
    res = conn.cursor().execute("SELECT begeni_sayisi, yildiz_puani FROM reaksiyon WHERE id=1").fetchone()
    conn.close()
    return res if res else (0, 5.0)

def reaksiyon_guncelle(begeniler, yildizlar):
    conn = db_baglan()
    conn.cursor().execute("UPDATE reaksiyon SET begeni_sayisi=?, yildiz_puani=? WHERE id=1", (begeniler, yildizlar))
    conn.commit()
    conn.close()

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

tab_excel, tab_bta, tab_chat, tab_members = st.tabs([
    "📂 BTA Excel Veri Analizi", 
    "📈 KONYA Canlı Veri Odası", 
    "💬 Canlı Sohbet Odası",
    "👥 BTA Hissedarları Kayıt Listesi"
])

# ==========================================
# MODÜL 1: EXCEL VERİ İŞLEME (A, C, D KOLONLARI)
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
            secilen_dosya = st.file_uploader("Bir Excel (.xlsx, .xlsm) dosyası yükleyin", type=["xlsx", "xlsm"])
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
                    st.session_state["global_bta_price"] = float(konya_satirlari["BTA ALIM FİYATI"].iloc[0])
            
            st.dataframe(df_goster, use_container_width=True)
        except Exception as e:
            st.error(f"Excel verisi işlenirken bir hata oluştu: {e}")
    else:
        st.info("💡 Sistemde analiz edilecek Excel dosyası bulunamadı.")

# ==========================================
# MODÜL 2: KONYA CANLI TAKİP PANELİ
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
        c1, c2, c3, c4 = st.columns(4)
