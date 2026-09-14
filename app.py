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

# Otomatik Yenileme Ayarı (streamlit-autorefresh)
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
st.write("Excel veri entegrasyonu, sabit BTA veri takibi ve canlı halka arz haber akış paneli.")

# Sekmeli Menü Tasarımı (AL-SAT hisseleri listelerden kaldırılmıştır)
tab_excel, tab_bta, tab_scraper = st.tabs([
    "📂 BTA Excel & Makro Analizi", 
    "📈 KONYA Canlı Veri & Kar/Zarar Takibi", 
    "📰 Canlı Halka Arz (IPO) Gündemi"
])

# ==========================================
# MODÜL 1: EXCEL & MAKRO VERİ İŞLEME (AL-SAT Kısıtlamalı)
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
            
            # İstek: AL SAT listelenmesin, sadece ana BTA hisse mantığı kalsın.
            # Tabloda "BTA AL SAT" kolonunu veya al sat verilerini kullanıcıya göstermiyoruz.
            filtrelenmis_sutunlar = [col for col in df.columns if "AL SAT" not in col.upper()]
            df_goster = df[filtrelenmis_sutunlar]
            
            arama_kelimesi = st.text_input("Tablo içinde dinamik filtreleme yapın:")
            if arama_kelimesi:
                filtre_mask = df_goster.astype(str).apply(lambda x: x.str.contains(arama_kelimesi, case=False)).any(axis=1)
                gosterilecek_df = df_goster[filtre_mask]
            else:
                gosterilecek_df = df_goster
                
            st.dataframe(gosterilecek_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Excel verisi işlenirken bir hata oluştu: {e}")

# ==========================================
# MODÜL 2: SADECE KONYA HİSSE TAKİBİ & +9 KUTLAMA ALGORİTMASI
# ==========================================
with tab_bta:
    st.header("📈 BTA Kurumsal Veri & Hedef Takip Ekranı")
    
    kurumsal_ticker = "KONYA.IS"
    # Tablonuzun 1. satırındaki ALIM FİYATI: 41.00 TL
    bta_alim_fiyati = 41.00 
    
    try:
        hisse = yf.Ticker(kurumsal_ticker)
        tarihce = hisse.history(period="1mo", interval="1d")
        
        if not tarihce.empty:
            guncel_fta_fiyati = tarihce['Close'].iloc[-1]
            
            # Kar/Zarar Yüzdesi Hesaplama
            kar_zarar_yuzdesi = ((guncel_fta_fiyati - bta_alim_fiyati) / bta_alim_fiyati) * 100
            
            # +9 VE ÜSTÜ YAPTIĞINDA ÇALIŞACAK TEBRİK / KUTLAMA ODASI
            if kar_zarar_yuzdesi >= 9.0:
                st.balloons()  # Ekranda uçan konfeti/balon efekti yaratır
                st.snow()      # Görsel şöleni artırır
                st.success(f"🚀 **TEBRİKLER! KONYA HİSSESİNDE +%9 HEDEFİ AŞILDI!** 🥳🎉\n\n Mevcut FTA Fiyatı: **{guncel_fta_fiyati:.2f} TL** seviyesine ulaşarak BTA alım fiyatınız olan {bta_alim_fiyati} TL üzerinden tam **% {kar_zarar_yuzdesi:.2f}** kar marjı yakalamıştır. Odada kutlamalar başlasın!")
            
            # Canlı Gösterge Kartları
            m1, m2, m3 = st.columns(3)
            m1.metric("KONYA Güncel FTA Fiyatı", f"{guncel_fta_fiyati:.2f} TL")
            m2.metric("Referans Alım Fiyatınız", f"{bta_alim_fiyati:.2f} TL")
            
            # Kar/Zarar durumuna göre renkli metrik gösterimi
            if kar_zarar_yuzdesi >= 0:
                m3.metric("Anlık Kar/Zarar Durumu", f"+% {kar_zarar_yuzdesi:.2f}", delta_color="normal")
            else:
                m3.metric("Anlık Kar/Zarar Durumu", f"% {kar_zarar_yuzdesi:.2f}", delta_color="inverse")
            
            # Canlı Grafik Alanı
            st.subheader("📊 KONYA - Canlı Fiyat Değişim Trendi")
            st.line_chart(tarihce['Close'])
        else:
            st.warning("Canlı borsa sunucularından anlık veri çekilemedi.")
    except Exception as e:
        st.error(f"Canlı takip motorunda hata: {e}")

# ==========================================
# MODÜL 3: CANLI HALKA ARZ WEB SCRAPER (BloombergHT Entegrasyonu)
# ==========================================
with tab_scraper:
    st.header("📰 Canlı Halka Arz (IPO) Haber Botu")
    st.write("Sistem doğrudan Türkiye piyasalarındaki **Yeni Halka Arz Gündemine** odaklanmıştır.")
    
    if st.button("Halka Arz Gündemini Yenile ve Kazı"):
        try:
            hedef_url = "https://www.bloomberght.com/halka-arz"
            tarayici_bilgisi = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            
            sayfa_istegi = requests.get(hedef_url, headers=tarayici_bilgisi)
            
            if sayfa_istegi.status_code == 200:
                html_icerik = BeautifulSoup(sayfa_istegi.text, "html.parser")
                basliklar = html_icerik.find_all("span", class_="title", limit=10)
                
                if not basliklar:
                    basliklar = html_icerik.find_all("h3", limit=10)
                
                if basliklar:
                    st.success("Anlık Halka Arz haberleri finans servislerinden başarıyla kazındı!")
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
