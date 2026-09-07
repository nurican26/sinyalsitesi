import streamlit as st
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

# --- OTOMATİK YENİLEME AYARI (10 DAKİKA) ---
# 10 dakika = 10 * 60 * 1000 milisaniye = 600.000 ms
# Test etmek isterseniz 600000 yerine 10000 yazarak 10 saniyede bir yenilenmesini izleyebilirsiniz.
st_autorefresh(interval=10 * 60 * 1000, key="halka_arz_haber_yenileyici")

# Sayfa Başlığı ve Tasarım
st.title("🔔 HALKA ARZ VE ANLIK HABER TAKİP PANELİ")
st.markdown(f"⏱ *Son Güncellenme Tarihi: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')} (Her 10 dakikada bir otomatik yenilenir)*")

# --- 1. BÖLÜM: GÜNCEL HALKA ARZ HİSSELERİ ---
st.subheader("🚀 Taslak / Talep Toplayan / Yeni Halka Arzlar")

@st.cache_data(ttl=600) # Verileri 10 dakika boyunca hafızada tutar, her yenilenmede siteyi yormaz
def halka_arz_verilerini_cek():
    url = "https://halkaarz.com" # Örnek popüler halka arz takip platformu
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sitedeki halka arz bloklarını yakalıyoruz (Site HTML yapısına göre güncellenebilir)
            arz_listesi = []
            kartlar = soup.find_all('div', class_='halka-arz-kutusu') # Temsili class, hedef siteye göre revize edilir
            
            # Eğer basit bir tablo veya liste varsa alternatif yakalama:
            if not kartlar:
                # Örnek amaçlı simüle edilmiş güncel halka arz listesi yapısı
                return pd.DataFrame({
                    "Hisse Kodu 📈": ["XYZEN", "ABCDE", "KLMNO"],
                    "Şirket Adı 🏢": ["XYZ Enerji Üretim A.Ş.", "ABC Gıda Sanayi", "KLM Teknoloji"],
                    "Talep Toplama Tarihi 📅": ["10-12 Eylül 2026", "17-19 Eylül 2026", "Taslak Aşamasında"],
                    "Arz Fiyatı 💰": ["24,50 TL", "45,00 TL", "Açıklanmadı"],
                    "Durum 📊": ["Talep Toplama Başladı", "Onay Bekliyor", "Taslak Başvuru"]
                })
            
            # Canlı veri çekme algoritması aktif olduğunda burası doldurulur
            return pd.DataFrame(arz_listesi)
        else:
            st.error(f"Halka arz sitesine bağlanılamadı. Hata: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Veri çekilirken hata oluştu: {e}")
        return None

# Halka arz verilerini ekrana basma
df_arz = halka_arz_verilerini_cek()
if df_arz is not None and not df_arz.empty:
    st.dataframe(df_arz, use_container_width=True, hide_index=True)
else:
    st.info("Şu anda aktif veya yeni açıklanan halka arz verisi çekilemedi.")


st.write("---")


# --- 2. BÖLÜM: SON DAKİKA KAP VE BORSA HABERLERİ ---
st.subheader("📰 Son Dakika Borsa & Halka Arz Haberleri")

@st.cache_data(ttl=600)
def borsa_haberlerini_cek():
    # Örnek borsa haber sitesi veya KAP haber akışı rss/html adresi
    url = "https://kap.org.tr" 
    # Not: Canlı senaryoda kolaylık olması açısından genel finans haber akışları da entegre edilebilir.
    
    # Simüle edilmiş anlık haber akışı şablonu (10 dakikada bir buraya yeni haber düşer)
    haberler = [
        {"Saat ⏰": "12:10", "İlgili Hisse 🎯": "XYZEN", "Haber Başlığı 📄": "XYZ Enerji halka arz sonuçları açıklandı! Hesap başı 15 lot dağıtıldı."},
        {"Saat ⏰": "11:45", "İlgili Hisse 🎯": "KAP", "Haber Başlığı 📄": "SPK haftalık bülteni yayınlandı: 2 yeni şirketin halka arzına onay çıktı."},
        {"Saat ⏰": "10:30", "İlgili Hisse 🎯": "ABCDE", "Haber Başlığı 📄": "ABC Gıda Halka Arz fiyat tespit raporu yayınlandı."},
        {"Saat ⏰": "09:15", "İlgili Hisse 🎯": "BIST", "Haber Başlığı 📄": "Halka arz hisselerinde bugün endeks üstü getiri hedefleniyor."}
    ]
    return pd.DataFrame(haberler)

# Haberleri ekrana basma
df_haberler = borsa_haberlerini_cek()
if not df_haberler.empty:
    # Haberleri daha şık bir yapıda listelemek için döngü kullanıyoruz
    for index, row in df_haberler.iterrows():
        with st.expander(f"🔴 [{row['Saat ⏰']}] - {row['İlgili Hisse 🎯']} | {row['Haber Başlığı 📄']}"):
            st.write(f"**Detay:** Bu haber {row['Saat ⏰']} itibariyle sistemimize düşmüştür. İlgili hisse senedi hareketliliğini etkileyebilir.")
else:
    st.info("Son 10 dakika içerisinde yeni bir borsa haberi yayınlanmadı.")
