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
    refresh_interval = st.sidebar.slider("Yenileme Sıklığı (Saniye)", 5, 120, 30)
    st_autorefresh(interval=refresh_interval * 1000, key="bta_refresh_counter")

# Klasördeki mevcut Excel/Macro dosyalarını algılama
excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]

# ==========================================
# 2. ANA PANEL BAŞLIĞI
# ==========================================
st.title("📊 BTA Kurumsal Analiz ve Finans Portalı")
st.write("Excel veri entegrasyonu, sabit BTA veri takibi ve canlı halka arz haber akış paneli.")

# Sekmeli Menü Tasarımı
tab_excel, tab_bta, tab_scraper = st.tabs([
    "📂 BTA Excel & Makro Analizi", 
    "📈 BTA Hisse Takip Modülü (KONYA)", 
    "📰 Canlı Halka Arz (IPO) Gündemi"
])

# ==========================================
# MODÜL 1: EXCEL & MAKRO VERİ İŞLEME (pandas & openpyxl)
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
            
            arama_kelimesi = st.text_input("Tablo içinde dinamik filtreleme yapın:")
            if arama_kelimesi:
                filtre_mask = df.astype(str).apply(lambda x: x.str.contains(arama_kelimesi, case=False)).any(axis=1)
                gosterilecek_df = df[filtre_mask]
            else:
                gosterilecek_df = df
                
            st.dataframe(gosterilecek_df, use_container_width=True)
            
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
# MODÜL 2: SADECE KONYA HİSSE SENEDİ TAKİBİ
# ==========================================
with tab_bta:
    st.header("📈 BTA Özel Veri Takip Ekranı")
    st.write("Sistem kurumsal analiz için sadece **KONYA.IS** verilerini çekecek şekilde kilitlenmiştir. Arama motoru ve AL-SAT tavsiyeleri bulunmamaktadır.")
    
    # Tablonuzda yer alan KONYA hissesi BIST uzantısı (.IS) ile tanımlandı
    kurumsal_ticker = "KONYA.IS" 
    
    try:
        hisse = yf.Ticker(kurumsal_ticker)
        tarihce = hisse.history(period="1mo", interval="1d")
        
        if not tarihce.empty:
            guncel_kapanis = tarihce['Close'].iloc[-1]
            onceki_kapanis = tarihce['Close'].iloc[-2] if len(tarihce) > 1 else guncel_kapanis
            degisim = guncel_kapanis - onceki_kapanis
            yuzde_degisim = (degisim / onceki_kapanis) * 100
            
            # Canlı Gösterge Kartları
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("KONYA Güncel Fiyat", f"{guncel_kapanis:.2f} TL", f"{yuzde_degisim:.2f}%")
            m2.metric("Günlük En Yüksek", f"{tarihce['High'].iloc[-1]:.2f} TL")
            m3.metric("Günlük En Düşük", f"{tarihce['Low'].iloc[-1]:.2f} TL")
            m4.metric("İşlem Hacmi (Adet)", f"{tarihce['Volume'].iloc[-1]:,}")
            
            # Canlı Grafik Alanı
            st.subheader("📊 KONYA - 1 Aylık Canlı Trend Grafiği")
            st.line_chart(tarihce['Close'])
        else:
            st.warning("Borsa İstanbul canlı veri sunucularından anlık KONYA verisi alınamadı. Lütfen daha sonra tekrar deneyin.")
    except Exception as e:
        st.error(f"Canlı veri çekme motorunda hata oluştu: {e}")

# ==========================================
# MODÜL 3: YENİ HALKA ARZ WEB SCRAPER (Canlı Web Botu)
# ==========================================
with tab_scraper:
    st.header("📰 Canlı Halka Arz Haber Botu")
    st.write("Sistem doğrudan Türkiye piyasalarındaki **Yeni Halka Arz (IPO) Gündemine** odaklanacak şekilde güncellenmiştir.")
    
    if st.button("Halka Arz Gündemini Yenile / Kazı"):
        try:
            # Bloomberg HT Halka Arz ve borsa haber akışı üzerinden scraping işlemi
            hedef_url = "https://bloomberght.com"
            tarayici_bilgisi = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            sayfa_istegi = requests.get(hedef_url, headers=tarayici_bilgisi)
            
            if sayfa_istegi.status_code == 200:
                html_icerik = BeautifulSoup(sayfa_istegi.text, "html.parser")
                
                # Haber başlık bloklarını seçiyoruz
                basliklar = html_icerik.find_all("span", class_="title", limit=10)
                
                if not basliklar:
                    # Alternatif etiket kontrolü
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
    else:
        st.info("Piyasadaki en güncel halka arz gelişmelerini ve şirket listelerini çekmek için yukarıdaki butona basın.")

# ==========================================
# 3. YASAL UYARI - SPK RESMİ METNİ
# ==========================================
st.markdown("---")
st.warning("""
**⚠️ SPK YASAL UYARI NOTU**

Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. 

Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir **'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır.**
""")
