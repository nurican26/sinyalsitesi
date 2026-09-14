import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh
import os
from datetime import datetime

# ==========================================
# 1. SAYFA VE PANEL AYARLARI
# ==========================================
st.set_page_config(
    page_title="BTA Kurumsal Analiz Portalı",
    page_icon="📊",
    layout="wide"
)

# Canlı Sohbet ve Kayıt Veritabanı Hafızası (Session State) Kontrolü
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"user": "Sistem", "time": "12:00:00", "text": "BTA Özel Canlı Sohbet Odasına Hoş Geldiniz!"}
    ]

if "bta_members" not in st.session_state:
    st.session_state["bta_members"] = pd.DataFrame([
        {"İsim Soyisim": "Nurican Bey", "Kayıt Tarihi": "2026-09-14", "Durum": "Onaylı Üye"}
    ])

# Yan menü (Sidebar) kontrolleri
st.sidebar.header("⚙️ Sistem Kontrolleri")

# Otomatik Yenileme Ayarı (Sohbet ve veriler için 5 saniyede bir tetiklenir)
auto_refresh = st.sidebar.checkbox("Otomatik Yenilemeyi Aktif Et", value=True)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Yenileme Sıklığı (Saniye)", 2, 60, 5)
    st_autorefresh(interval=refresh_interval * 1000, key="bta_refresh_counter")

# Klasördeki mevcut Excel/Macro dosyalarını algılama
excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]

# ==========================================
# 2. ANA PANEL BAŞLIĞI
# ==========================================
st.title("📊 BTA Kurumsal Analiz ve Finans Portalı")
st.write("Excel veri entegrasyonu, KONYA canlı kâr/zarar odası ve BTA özel topluluk paneli.")

# Sekmeli Menü Tasarımı
tab_excel, tab_bta, tab_chat, tab_members, tab_scraper = st.tabs([
    "📂 BTA Excel Veri İnceleme", 
    "📈 KONYA Canlı Veri Odası", 
    "💬 Canlı Sohbet Odası",
    "👥 BTA Hissedarları Kayıt Listesi",
    "📰 Canlı Halka Arz Gündemi"
])

# ==========================================
# MODÜL 1: EXCEL & MAKRO VERİ İŞLEME (AL-SAT Gizlendi)
# ==========================================
with tab_excel:
    st.header("📂 Excel Veri İnceleme Merkezi")
    dosya_kaynagi = st.radio("Dosya Kaynağı Seçin:", ["Klasördeki Dosyaları Kullan", "Yeni Dosya Yükle"])
    secilen_dosya = None
    
    if dosya_kaynagi == "Klasördeki Dosyaları Kullan" and excel_dosyalari:
        secilen_dosya = st.selectbox("Analiz Edilecek Dosya:", excel_dosyalari)
    else:
        secilen_dosya = st.file_uploader("Bir Excel (.xlsx, .xlsm) dosyası yükleyin", type=["xlsx", "xlsm"])
        
    if secilen_dosya is not None:
        try:
            excel_obj = pd.ExcelFile(secilen_dosya, engine='openpyxl')
            sayfa_isimleri = excel_obj.sheet_names
            st.success(f"Dosya başarıyla yüklendi! Toplam **{len(sayfa_isimleri)}** çalışma sayfası bulundu.")
            
            aktif_sayfa = st.selectbox("Görüntülenecek Sayfa:", sayfa_isimleri)
            df = pd.read_excel(secilen_dosya, sheet_name=aktif_sayfa, engine='openpyxl')
            
            filtrelenmis_sutunlar = [col for col in df.columns if "AL SAT" not in col.upper()]
            df_goster = df[filtrelenmis_sutunlar]
            
            arama_kelimesi = st.text_input("Tablo içinde dinamik filtreleme yapın:", value="KONYA")
            if arama_kelimesi:
                filtre_mask = df_goster.astype(str).apply(lambda x: x.str.contains(arama_kelimesi, case=False)).any(axis=1)
                gosterilecek_df = df_goster[filtre_mask]
            else:
                gosterilecek_df = df_goster
            st.dataframe(gosterilecek_df, use_container_width=True)
        except Exception as e:
            st.error(f"Excel verisi işlenirken bir hata oluştu: {e}")

# ==========================================
# MODÜL 2: KONYA CANLI TAKİP & KAR/ZARAR & TAVAN KUTLAMASI
# ==========================================
with tab_bta:
    st.header("📈 KONYA Hisse Senedi Canlı Kar/Zarar Takip Paneli")
    kurumsal_ticker = "KONYA.IS"
    bta_alim_fiyati = 4100.00 
    
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
                st.success(f"🚀 **ODADA KUTLAMALAR BAŞLASIN! KONYA HİSSESİ ANLIK OLARAK TAVAN OLDU VEYA +%9 KAR MARJINI AŞTI!** 🥳🎉")
            
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
                
            st.subheader("📊 KONYA - Gün İçi Canlı Fiyat Grafik Trendi")
            st.line_chart(tarihce['Close'])
        else:
            st.warning("Borsa İstanbul canlı veri sunucularından anlık KONYA verisi şu an alınamadı.")
    except Exception as e:
        st.error(f"Canlı takip motorunda teknik bir aksaklık oluştu: {e}")

# ==========================================
# MODÜL 3: KAPSAMLI CANLI SOHBET ODASI
# ==========================================
with tab_chat:
    st.header("💬 BTA Hissedarları Canlı Sohbet Odası")
    st.write("Sohbet odası otomatik yenileme ile senkronize çalışmaktadır.")
    
    bta_pass = st.text_input("Sohbet Odası Erişim Şifresi:", type="password", key="chat_pass")
    
    if bta_pass == "BTA2026":
        nickname = st.text_input("Sohbet Takma Adınız:", value="Hissedar")
        
        with st.form("chat_form", clear_on_submit=True):
            user_message = st.text_input("Mesajınızı yazın:")
            submit_button = st.form_submit_button("Gönder 🚀")
            
            if submit_button and user_message:
                now_str = datetime.now().strftime("%H:%M:%S")
                new_msg = {"user": nickname, "time": now_str, "text": user_message}
                st.session_state["chat_messages"].append(new_msg)
                st.rerun()

        st.subheader("📝 Oda Akışı")
        chat_box = ""
        for msg in reversed(st.session_state["chat_messages"]):
            chat_box += f"**[{msg['time']}] {msg['user']}:** {msg['text']}\n\n"
        st.markdown(chat_box)
    elif bta_pass != "":
        st.error("❌ Hatalı şifre! Lütfen şifrenizi kontrol edin.")
    else:
        st.info("🔒 Canlı sohbet akışını görmek ve mesaj yazmak için lütfen erişim şifresini (BTA2026) girin.")

# ==========================================
# MODÜL 4: BTA HİSSEDARLARI KAYIT LİSTESİ
# ==========================================
with tab_members:
    st.header("👥 BTA Hissedarları Kayıt ve Takip Listesi")
    st.write("Bu panelden BTA grubuna ait güncel üye listesini tutabilir ve yeni kayıt ekleyebilirsiniz.")
    
    member_pass = st.text_input("Kayıt Listesi Yönetim Şifresi:", type="password", key="mem_pass")
    
    if member_pass == "BTA2026":
        with st.expander("➕ Yeni Hissedar Kaydı Oluştur"):
            with st.form("member_form", clear_on_submit=True):
                new_name = st.text_input("Hissedar İsim Soyisim:")
                add_member_btn = st.form_submit_button("Sisteme Güvenli Kaydet 💾")
                
                if add_member_btn and new_name:
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    new_row = pd.DataFrame([{"İsim Soyisim": new_name, "Kayıt Tarihi": current_date, "Durum": "Onaylı Üye"}])
                    st.session_state["bta_members"] = pd.concat([st.session_state["bta_members"], new_row], ignore_index=True)
                    st.success(f"✔️ {new_name} sisteme başarıyla işlendi!")
                    st.rerun()
        
        st.subheader("📋 Onaylı BTA Üye Listesi")
        st.dataframe(st.session_state["bta_members"], use_container_width=True)
    elif member_pass != "":
        st.error("❌ Yetkisiz Giriş! Lütfen doğru şifreyi girin.")
    else:
        st.info("🔒 Hissedar veri tabanını ve kayıt formunu açmak için lütfen erişim şifresini (BTA2026) girin.")

# ==========================================
# MODÜL 5: CANLI HALKA ARZ WEB SCRAPER (Hata Veren Karmaşık Yapı Tamamen Temizlendi)
# ==========================================
with tab_scraper:
    st.header("📰 Canlı Halka Arz (IPO) Gündemi ve Arz Şirketleri")
    
    if st.button("Halka Arz Gündemini Yenile ve Kazı"):
        try:
            hedef_url = "https://bloomberght.com"
            tarayici_bilgisi = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            sayfa_istegi = requests.get(hedef_url, headers=tarayici_bilgisi)
            
            if sayfa_istegi.status_code == 200:
                html_icerik = BeautifulSoup(sayfa_istegi.text, "html.parser")
                basliklar = html_icerik.find_all("span", class_="title", limit=10)
                
