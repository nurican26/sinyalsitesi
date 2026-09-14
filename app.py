import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os
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

# Klasördeki Excel dosyalarını bulma
excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]
varsayilan_dosya = None
if excel_dosyalari:
    hedef_dosyalar = [f for f in excel_dosyalari if "bta" in f.lower() or "nurican" in f.lower()]
    if hedef_dosyalar:
        varsayilan_dosya = hedef_dosyalar[0]
    else:
        varsayilan_dosya = excel_dosyalari[0]

# ==========================================
# 0. EXCEL TABANLI KALICI VERİ MOTORU (SADE VE GÜVENLİ)
# ==========================================
def excel_veri_hazirla(dosya):
    if not dosya:
        return
    try:
        reader = pd.ExcelFile(dosya, engine='openpyxl')
        sheets = reader.sheet_names
        with pd.ExcelWriter(dosya, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            if "Sohbet_Hafizasi" not in sheets:
                pd.DataFrame(columns=["id", "Kullanici", "Saat", "Mesaj"]).to_excel(writer, sheet_name="Sohbet_Hafizasi", index=False)
            if "Hissedar_Hafizasi" not in sheets:
                pd.DataFrame(columns=["id", "Hissedar", "Hisse", "Maliyet", "Adet"]).to_excel(writer, sheet_name="Hissedar_Hafizasi", index=False)
    except:
        pass

if varsayilan_dosya:
    excel_veri_hazirla(varsayilan_dosya)

def excel_mesaj_ekle(dosya, user, time, text):
    if not dosya:
        return
    try:
        df_old = pd.read_excel(dosya, sheet_name="Sohbet_Hafizasi", engine='openpyxl')
    except:
        df_old = pd.DataFrame(columns=["id", "Kullanici", "Saat", "Mesaj"])
    
    msg_id = int(datetime.now().timestamp() * 1000)
    df_new = pd.DataFrame([{"id": msg_id, "Kullanici": user, "Saat": time, "Mesaj": text}])
    df_total = pd.concat([df_old, df_new], ignore_index=True)
    
    try:
        with pd.ExcelWriter(dosya, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_total.to_excel(writer, sheet_name="Sohbet_Hafizasi", index=False)
    except:
        pass

def excel_mesajlari_getir(dosya):
    if not dosya:
        return []
    try:
        df = pd.read_excel(dosya, sheet_name="Sohbet_Hafizasi", engine='openpyxl')
        return df.to_dict(orient="records")
    except:
        return []

def excel_mesaj_sil(dosya, msg_id):
    if not dosya:
        return
    try:
        df = pd.read_excel(dosya, sheet_name="Sohbet_Hafizasi", engine='openpyxl')
        df = df[df["id"] != msg_id]
        with pd.ExcelWriter(dosya, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name="Sohbet_Hafizasi", index=False)
    except:
        pass

def excel_hissedar_ekle(dosya, isim, hisse, maliyet, adet):
    if not dosya:
        return
    try:
        df_old = pd.read_excel(dosya, sheet_name="Hissedar_Hafizasi", engine='openpyxl')
    except:
        df_old = pd.DataFrame(columns=["id", "Hissedar", "Hisse", "Maliyet", "Adet"])
        
    mem_id = int(datetime.now().timestamp() * 1000)
    df_new = pd.DataFrame([{"id": mem_id, "Hissedar": isim, "Hisse": hisse, "Maliyet": maliyet, "Adet": adet}])
    df_total = pd.concat([df_old, df_new], ignore_index=True)
    
    try:
        with pd.ExcelWriter(dosya, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_total.to_excel(writer, sheet_name="Hissedar_Hafizasi", index=False)
    except:
        pass

def excel_hissedarlari_getir(dosya):
    if not dosya:
        return []
    try:
        df = pd.read_excel(dosya, sheet_name="Hissedar_Hafizasi", engine='openpyxl')
        return df.to_dict(orient="records")
    except:
        return []

def excel_hissedar_sil(dosya, member_id):
    if not dosya:
        return
    try:
        df = pd.read_excel(dosya, sheet_name="Hissedar_Hafizasi", engine='openpyxl')
        df = df[df["id"] != member_id]
        with pd.ExcelWriter(dosya, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name="Hissedar_Hafizasi", index=False)
    except:
        pass

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
# MODÜL 1: EXCEL VERİ İŞLEME (SADECE A, C, D KOLONLARI)
# ==========================================
with tab_excel:
    st.header("📂 Excel Veri İnceleme Merkezi")
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
        st.info("💡 Sistemde analiz edilecek Excel dosyası bulunamadı.")

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
            c1, c2, c3, c4 = st.columns(4)
