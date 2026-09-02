import streamlit as st
import pandas as pd
import os

# 1. Sayfa Yapılandırması (Geniş Ekran Modu)
st.set_page_config(page_title="Sinyal Sitesi", layout="wide")
st.title("📊 Sinyal Sitesi Yönetim Paneli")

# 2. Excel Dosya Adı Tanımlaması
excel_dosyasi = "nurcan.xlsx"

# 3. 💬 MESAJLAŞMA / CHAT ALANI (Kullanıcı Girişi)
st.markdown("---")
st.subheader("💬 Mesaj Gönder")
yeni_mesaj = st.text_input(
    "Mesajınızı yazınız:", 
    placeholder="Örn: Hisseler bugün çok iyi gidiyor...", 
    key="chat_msg"
)

# Eğer kullanıcı kutuya bir şey yazıp Enter'a basarsa ekranda gösterir
if yeni_mesaj:
    st.info(f"🔹 Gönderilen Mesaj: {yeni_mesaj}")
st.markdown("---")

# 4. EXCEL DOSYASI KONTROLÜ VE VERİ GÖSTERİMİ
if os.path.exists(excel_dosyasi):
    try:
        # Excel verisini arka planda oku
        df = pd.read_excel(excel_dosyasi)
        
        st.success("✅ Veriler başarıyla yüklendi!")
        
        # Üst Metrik Sayaçları (Satır ve Sütun Sayıları)
        col1, col2 = st.columns(2)
        col1.metric("Toplam Satır Sayısı", len(df))
        col2.metric("Toplam Sütun Sayısı", len(df.columns))
        
        # İnteraktif Veri Tablosu
        st.subheader("📋 Güncel Verileriniz")
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        # Dosya okunurken teknik bir sorun çıkarsa çökmeyi önler
        st.error(f"❌ Excel dosyası okunurken bir hata oluştu: {e}")
else:
    # Dosya klasörde veya GitHub'da yoksa kullanıcıyı uyarır
    st.error(f"❌ '{excel_dosyasi}' dosyası bulunamadı. Lütfen klasörde bu isimde bir Excel olduğundan emin olun.")
