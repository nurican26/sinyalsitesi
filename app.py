import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh
import os

# ==========================================
# 1. SAYFA VE PANEL AYARLARI
# ==========================================
st.set_page_config(
    page_title="BTA Finansal Analiz & Web Uygulaması",
    page_icon="📈",
    layout="wide"
)

# Yan menü (Sidebar) kontrolleri
st.sidebar.header("⚙️ Sistem Kontrolleri")

# Otomatik Yenileme Ayarı (streamlit-autorefresh)
auto_refresh = st.sidebar.checkbox("Otomatik Yenilemeyi Aktif Et", value=True)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Yenileme Sıklığı (Saniye)", 5, 120, 30)
    st_autorefresh(interval=refresh_interval * 1000, key="bta_refresh_counter")

# Klasördeki mevcut Excel/Macro dosyalarını algılama
excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]

# ==========================================
# 2. ANA PANEL BAŞLIĞI
# ==========================================
st.title("📊 BTA Web Uygulaması & Finansal Analiz Portalı")
st.write("Excel makro entegrasyonu, canlı hisse takibi ve web scraping modüllerinin birleşik paneli.")

# Sekmeli Menü Tasarımı
tab_excel, tab_market, tab_scraper = st.tabs([
    "📂 BTA Excel & Makro Analizi", 
    "📈 Canlı Hisse Senedi Takibi (yfinance)", 
    "📰 Global Finans Scraper"
])

# ==========================================
# MODÜL 1: EXCEL & MAKRO VERİ İŞLEME (pandas & openpyxl)
# ==========================================
with tab_excel:
    st.header("📂 Excel Veri İnceleme Merkezi")
    
    # Kullanıcı ister yerel dosyayı seçer, ister yeni yükler
    dosya_kaynagi = st.radio("Dosya Kaynağı Seçin:", ["Klasördeki Dosyaları Kullan", "Yeni Dosya Yükle"])
    
    secilen_dosya = None
    if dosya_kaynagi == "Klasördeki Dosyaları Kullan" and excel_dosyalari:
        secilen_dosya = st.selectbox("Analiz Edilecek Dosya:", excel_dosyalari)
    else:
        secilen_dosya = st.file_uploader("Bir Excel (.xlsx, .xlsm) dosyası yükleyin", type=["xlsx", "xlsm"])
        
    if secilen_dosya is not None:
        try:
            # Excel yapısını okuma
            excel_obj = pd.ExcelFile(secilen_dosya, engine='openpyxl')
            sayfa_isimleri = excel_obj.sheet_names
            
            st.success(f"Dosya başarıyla yüklendi! Toplam **{len(sayfa_isimleri)}** çalışma sayfası bulundu.")
            
            aktif_sayfa = st.selectbox("Görüntülenecek Sayfa:", sayfa_isimleri)
            df = pd.read_excel(secilen_dosya, sheet_name=aktif_sayfa, engine='openpyxl')
            
            # Veri arama filtresi
            arama_kelimesi = st.text_input("Tablo içinde dinamik filtreleme yapın:")
            if arama_kelimesi:
                filtre_mask = df.astype(str).apply(lambda x: x.str.contains(arama_kelimesi, case=False)).any(axis=1)
                gosterilecek_df = df[filtre_mask]
            else:
                gosterilecek_df = df
                
            st.dataframe(gosterilecek_df, use_container_width=True)
            
            # Sayısal grafik tetikleyici
            sayisal_sutunlar = df.select_dtypes(include=['number']).columns.tolist()
            if len(sayisal_sutunlar) >= 1:
                with st.expander("📊 Veri Görselleştirme Ayarları"):
                    x_ekseni = st.selectbox("X Ekseni:", df.columns.tolist())
                    y_ekseni = st.multiselect("Y Ekseni (Sayısal):", sayisal_sutunlar, default=sayisal_sutunlar[:1])
                    if x_ekseni and y_ekseni:
                        st.line_chart(df.set_index(x_ekseni)[y_ekseni])
                        
        except Exception as e:
            st.error(f"Excel verisi işlenirken bir hata oluştu: {e}")
    else:
        st.info("💡 Lütfen işlem yapmak için bir veri kaynağı belirtin.")

# ==========================================
# MODÜL 2: YFINANCE CANLI HİSSE Senedi ANALİZİ
# ==========================================
with tab_market:
    st.header("📈 Canlı Piyasa Takip Ekranı")
    
    # Kullanıcıdan Ticker Girişi Alma
    ticker = st.text_input("Hisse / Emtia Kodu Giriniz (Örn: THYAO.IS, AAPL, BTC-USD):", value="THYAO.IS").upper()
    
    if ticker:
        try:
            hisse = yf.Ticker(ticker)
            tarihce = hisse.history(period="1mo", interval="1d")
            
            if not tarihce.empty:
                # Son gün ve bir önceki gün verileri
                guncel_kapanis = tarihce['Close'].iloc[-1]
                onceki_kapanis = tarihce['Close'].iloc[-2] if len(tarihce) > 1 else guncel_kapanis
                degisim = guncel_kapanis - onceki_kapanis
                yuzde_degisim = (degisim / onceki_kapanis) * 100
                
                # Özet Gösterge Kartları
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Son Fiyat", f"{guncel_kapanis:.2f}", f"{yuzde_degisim:.2f}%")
                m2.metric("Günlük En Yüksek", f"{tarihce['High'].iloc[-1]:.2f}")
                m3.metric("Günlük En Düşük", f"{tarihce['Low'].iloc[-1]:.2f}")
                m4.metric("İşlem Hacmi", f"{tarihce['Volume'].iloc[-1]:,}")
                
                # Grafik Alanı
                st.subheader(f"📊 {ticker} - 1 Aylık Kapanış Değişim Grafiği")
                st.line_chart(tarihce['Close'])
            else:
                st.warning("Girdiğiniz koda ait piyasa verisi çekilemedi. Lütfen sembolü kontrol edin.")
        except Exception as e:
            st.error(f"yfinance entegrasyon hatası: {e}")

# ==========================================
# MODÜL 3: WEB SCRAPER (requests & bs4)
# ==========================================
with tab_scraper:
    st.header("📰 Finans Haberleri Canlı Botu")
    st.write("Aşağıdaki butona basarak web kazıma (scraping) motorunu anlık tetikleyebilirsiniz.")
    
    if st.button("Haber Akışını Yenile ve Kazı"):
        try:
            hedef_url = "https://yahoo.com"
            tarayici_bilgisi = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            
            sayfa_istegi = requests.get(hedef_url, headers=tarayici_bilgisi)
            
            if sayfa_istegi.status_code == 200:
                html_icerik = BeautifulSoup(sayfa_istegi.text, "html.parser")
                basliklar = html_icerik.find_all("h3", limit=12)
                
                if basliklar:
                    st.success("Canlı veriler web sitesinden başarıyla kazındı!")
                    for sira, baslik in enumerate(basliklar, 1):
                        metin = baslik.get_text(strip=True)
                        st.markdown(f"**{sira}.** {metin}")
                        st.caption("Kaynak: Yahoo Finance")
                        st.divider()
                else:
                    st.warning("Web sitesinin veri yapısı (DOM) değiştiği için başlıklar ayrıştırılamadı.")
            else:
                st.error(f"Bağlantı başarısız oldu. Durum Kodu: {sayfa_istegi.status_code}")
        except Exception as e:
            st.error(f"Web Scraping işlemi sırasında hata: {e}")
    else:
        st.info("Piyasa gündemini ve kazınan başlıkları listelemek için yukarıdaki butona tıklayın.")
