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
    page_title="BTA Kurumsal Analiz Portalı",
    page_icon="📊",
    layout="wide"
)

# Yan menü (Sidebar) kontrolleri
st.sidebar.header("⚙️ Sistem Kontrolleri")

# Otomatik Yenileme Ayarı (Sayfa 10 saniyede bir verileri canlı tazeler)
auto_refresh = st.sidebar.checkbox("Otomatik Yenilemeyi Aktif Et", value=True)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Yenileme Sıklığı (Saniye)", 5, 120, 10)
    st_autorefresh(interval=refresh_interval * 1000, key="bta_refresh_counter")

# Klasördeki mevcut Excel/Macro dosyalarını algılama
excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]

# ==========================================
# 2. ANA PANEL BAŞLIĞI
# ==========================================
st.title("📊 BTA Kurumsal Analiz ve Finans Portalı")
st.write("Excel veri entegrasyonu, KONYA hissesi anlık kar/zarar analizi ve tavan takip ekranı.")

# Sekmeli Menü Tasarımı (AL-SAT hisseleri listelerden tamamen kaldırılmıştır)
tab_excel, tab_bta, tab_scraper = st.tabs([
    "📂 BTA Excel Veri İnceleme", 
    "📈 KONYA Canlı Veri & Kar/Zarar Odası", 
    "📰 Canlı Halka Arz (IPO) Gündemi"
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
            
            # İstek Doğrultusunda: "BTA AL SAT" kolonu ve tüm türevleri tablodan gizleniyor
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
    # Gönderdiğiniz son görseldeki net alım fiyatınız 4100 TL olarak sisteme işlendi
    bta_alim_fiyati = 4100.00 
    
    try:
        hisse = yf.Ticker(kurumsal_ticker)
        # Gün içi değişim oranını doğru saptamak için son verileri çekiyoruz
        tarihce = hisse.history(period="2d", interval="1d")
        
        if not tarihce.empty:
            guncel_fta_fiyati = history_data = tarihce['Close'].iloc[-1]
            
            # Günlük yüzde değişim verisini alma
            gunluk_degisim_yuzde = hisse.info.get('regularMarketChangePercent', 0.0)
            if gunluk_degisim_yuzde == 0.0 and len(tarihce) > 1:
                onceki_kapanis = tarihce['Close'].iloc[-2]
                gunluk_degisim_yuzde = ((guncel_fta_fiyati - onceki_kapanis) / onceki_kapanis) * 100
            
            # Alım Fiyatına Göre Net Kar/Zarar Hesaplaması
            kar_zarar_tutari = guncel_fta_fiyati - bta_alim_fiyati
            kar_zarar_yuzdesi = (kar_zarar_tutari / bta_alim_fiyati) * 100
            
            # 🚨 GÜNLÜK HİSSE TAVAN OLDUĞUNDA (%9.90+) VEYA TOPLAM KARINIZ %9+ OLDUĞUNDA KUTLAMA ODASI
            if gunluk_degisim_yuzde >= 9.90 or kar_zarar_yuzdesi >= 9.0:
                st.balloons()  # Havada uçan konfeti balonları efekti
                st.snow()      # Görsel coşkuyu artıran kar efekti
                st.success(f"🚀 **ODADA KUTLAMALAR BAŞLASIN! KONYA HİSSESİ ANLIK OLARAK TAVAN OLDU VEYA +%9 KAR MARJINI AŞTI!** 🥳🎉")
                st.info(f"Hisse Borsa İstanbul'da güçlü tavan serisine girdi veya alım maliyetiniz olan {bta_alim_fiyati} TL üzerinden hedeflenen büyük kârlılığa ulaştı!")
            
            # İstediğiniz Canlı Kar / Zarar ve Anlık Fiyat Gösterim Tablosu
            st.subheader("📊 Canlı Hesap Tablosu ve Portföy Durumu")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Anlık Canlı FTA Fiyatı", f"{guncel_fta_fiyati:.2f} TL", f"{gunluk_degisim_yuzde:.2f}% (Günlük)")
            c2.metric("Sizin Alım Maliyetiniz", f"{bta_alim_fiyati:.2f} TL")
            
            # Kar/Zarar durumlarının dinamik renk kodlamalı gösterimi
            if kar_zarar_tutari >= 0:
                c3.metric("Net Kar/Zarar Durumu (TL)", f"+{kar_zarar_tutari:.2f} TL")
                c4.metric("Toplam Kar Oranınız", f"+% {kar_zarar_yuzdesi:.2f}")
            else:
                c3.metric("Net Kar/Zarar Durumu (TL)", f"{kar_zarar_tutari:.2f} TL")
                c4.metric("Toplam Zarar Oranınız", f"% {kar_zarar_yuzdesi:.2f}")
                
            # Canlı Fiyat Grafik Alanı
            st.subheader("📊 KONYA - Gün İçi Canlı Fiyat Grafik Trendi")
            st.line_chart(tarihce['Close'])
        else:
            st.warning("Borsa İstanbul canlı veri sunucularından anlık KONYA verisi şu an alınamadı.")
    except Exception as e:
        st.error(f"Canlı takip motorunda teknik bir aksaklık oluştu: {e}")

# ==========================================
# MODÜL 3: CANLI HALKA ARZ WEB SCRAPER (BloombergHT Entegrasyonu)
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
                
                if not basliklar:
                    basliklar = html_icerik.find_all("h3", limit=10)
                
                if basliklar:
                    st.success("Anlık Halka Arz haberleri ve arz şirketleri başarıyla kazındı!")
                    for sira, baslik in enumerate(basliklar, 1):
                        metin = baslik.get_text(strip=True)
                        if metin:
                            st.markdown(f"🚀 **{sira}.** {metin}")
                            st.caption("Kaynak: Canlı Finans Servisleri (BloombergHT)")
                            st.divider()
                else:
                    st.warning("Veri kaynağının kod yapısı değiştiği için başlıklar okunamadı.")
            else:
                st.error(f"Finans sunucularına bağlanılamadı. Durum Kodu: {sayfa_istegi.status_code}")
        except Exception as e:
            st.error(f"Web Scraping işlemi sırasında bir hata meydana geldi: {e}")

# ==========================================
# 4. YASAL UYARI - SPK RESMİ METNİ
# ==========================================
st.markdown("---")
st.warning("""
**⚠️ SPK YASAL UYARI NOTU**

Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. 

Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir **'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır.**
""")
