import streamlit as st
import pandas as pd
import os

# Sayfa Yapılandırması
st.set_page_config(page_title="Sinyal Sitesi", layout="wide")
st.title("📊 Sinyal Sitesi Yönetim Paneli")

# Excel Dosya Adı
excel_dosyasi = "nurcan.xlsx"

# Dosya Kontrolü ve Okuma
if os.path.exists(excel_dosyasi):
    try:
        # Excel verisini oku
        df = pd.read_excel(excel_dosyasi)
        
        # Basit Metrikler
        st.success("✅ Veriler başarıyla yüklendi!")
        col1, col2 = st.columns(2)
        col1.metric("Toplam Satır Sayısı", len(df))
        col2.metric("Toplam Sütun Sayısı", len(df.columns))
        
        # Veri Tablosunu Göster
        st.subheader("📋 Güncel Verileriniz")
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Excel dosyası okunurken bir hata oluştu: {e}")
else:
    st.error(f"❌ '{excel_dosyasi}' dosyası bulunamadı. Lütfen klasörde bu isimde bir Excel olduğundan emin olun.")

# Chat/Mesaj Giriş Alanı (Görseldeki alanın hatasız versiyonu)
st.markdown("---")
st.subheader("💬 Mesaj Gönder")
yeni_mesaj = st.text_input("Mesajınızı yazınız:", placeholder="Örn: Hisseler bugün çok iyi gidiyor...", key="chat_msg")

if yeni_mesaj:
    st.info(f"Gönderilen Mesaj: {yeni_mesaj}")
