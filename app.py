import streamlit as st
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Yıldız Panel - Beğeni Paneli", layout="wide")

# 2. ÖZEL CSS TASARIMI (BTA Görsel Diline Sadık Kalınmıştır)
css_kodu = """
<style>
.stApp { 
    background-color: #0b111e !important; 
    background-image: radial-gradient(at 0% 0%, rgba(26, 54, 93, 0.4) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.15) 0px, transparent 50%) !important; 
}
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
div[data-testid="stMetric"], div[data-testid="stExpander"] { background-color: #121d33 !important; border: 1px solid #1e3a5f !important; border-radius: 10px !important; padding: 12px !important; }

/* Sipariş Geçmişi Tablo Tasarımı */
.siparis-tablo { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 15px; background-color: #121d33; border-radius: 10px; overflow: hidden; }
.siparis-tablo th { background-color: #1e2e4d; color: #00ffcc; text-align: left; padding: 10px 8px; }
.siparis-tablo td { padding: 10px 8px; color: #ffffff; border-bottom: 1px solid #1e2e4d; font-weight: bold; }

/* Yürüyen Yıldız Panel Logosu */
.logo-yurume-alani {
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1;
}

@keyframes yildizYoru {
    0% { transform: translateX(-10%); }
    50% { transform: translateX(75%); }
    100% { transform: translateX(-10%); }
}

.yuruyen-yildiz-logo {
    font-family: 'Brush Script MT', cursive, sans-serif !important;
    font-weight: bold; 
    font-size: 65px; 
    color: #00ffcc;
    display: inline-block;
    animation: yildizYoru 18s infinite linear;
    text-shadow: 0 0 10px #00ffcc, 0 0 20px #1e90ff, 0 0 35px #0d9488;
}
</style>
"""
st.markdown(css_kodu, unsafe_allow_html=True)

# 3. OTOMATİK YENİLEME MOTORU (5 Saniyede Bir)
st_autorefresh(interval=5 * 1000, key="yildiz_panel_senkronize_motoru")

# 4. VERİ TABANLARI VE SAYAÇLAR
db_siparisler = "yildiz_panel_siparisler_db.csv"
db_istatistik = "yildiz_panel_istatistik_db.csv"

if not os.path.exists(db_siparisler):
    pd.DataFrame(columns=["tarih", "platform", "link", "miktar", "durum"]).to_csv(db_siparisler, index=False)

if not os.path.exists(db_istatistik):
    pd.DataFrame([[0]], columns=["toplam_ziyaret"]).to_csv(db_istatistik, index=False)

# Ziyaretçi Sayacı
ziyaret = 0
try:
    df_ist = pd.read_csv(db_istatistik)
    if "ziyaret_sayildi" not in st.session_state:
        df_ist.at[0, "toplam_ziyaret"] = int(df_ist.at[0, "toplam_ziyaret"]) + 1
        df_ist.to_csv(db_istatistik, index=False)
        st.session_state["ziyaret_sayildi"] = True
    ziyaret = int(df_ist.at[0, "toplam_ziyaret"])
except:
    pass

# 5. YÜRÜYEN LOGO BÖLÜMÜ
st.markdown('<div class="logo-yurume-alani"><h1 class="yuruyen-yildiz-logo">Yıldız Panel</h1></div>', unsafe_allow_html=True)

# 6. BEĞENİ GÖNDERİM FORMU KARTI
st.markdown('<p style="font-size:16px; font-weight:bold; color:#1E90FF; margin-bottom:5px;">🚀 ANLIK BEĞENİ GÖNDERİM SİSTEMİ</p>', unsafe_allow_html=True)

with st.container():
    # Streamlit bileşenleriyle form yapısı
    col1, col2 = st.columns([1, 1])
    with col1:
        platform = st.selectbox("Platform Seçimi", ["Instagram Beğeni", "TikTok Beğeni", "X (Twitter) Beğeni", "YouTube Beğeni"])
        miktar = st.number_input("Beğeni Miktarı", min_value=10, max_value=10000, value=100, step=50)
    with col2:
        link = st.text_input("Gönderi Bağlantısı (URL)", placeholder="https://instagram.com...")
        
    # Yasal Uyarı & Bilgilendirme Kutusu
    uyari_html = '<div style="background-color: #121d33; border: 1px solid #00ffcc; border-radius: 8px; padding: 10px; margin-top: 10px;"><p style="font-size:12px; color:#b2c3d9; line-height:1.5; margin:0;"><b style="color:#00ffcc;">⚠️ SİSTEM BİLGİLENDİRMESİ:</b> Gönderimler yoğunluğa bağlı olarak 15 dakikaya kadar gecikebilir. İşlem görecek hesabın <b>"Gizli"</b> olmaması gerekmektedir. Gizli hesaplara sipariş iletilemez.</p></div>'
    st.markdown(uyari_html, unsafe_allow_html=True)
    
    st.write("")
    if st.button("Beğeni Gönderimini Başlat", use_container_width=True):
        if link:
            # Yeni siparişi veritabanına ekleme
            yeni_siparis = pd.DataFrame([{
                "tarih": datetime.datetime.now().strftime("%d.%m.%Y - %H:%M"),
                "platform": platform,
                "link": link[:30] + "..." if len(link) > 30 else link, # Tablo taşmasın diye kısaltma
                "miktar": f"{miktar} Adet",
                "durum": "Sırada"
            }])
            
            if os.path.exists(db_siparisler):
                df_sip = pd.read_csv(db_siparisler)
                df_sip = pd.concat([yeni_siparis, df_sip], ignore_index=True)
                df_sip.to_csv(db_siparisler, index=False)
            
            st.success(f"⚡ {platform} işlemi başarıyla sıraya alındı!")
        else:
            st.error("Lütfen geçerli bir gönderi bağlantısı (URL) giriniz!")

# 7. SİPARİŞ GEÇMİŞİ TABLOSU
st.write("---")
st.markdown('<p style="font-size:16px; font-weight:bold; color:#00ffcc; margin-bottom:5px;">📊 GÜNCEL SİPARİŞ DURUMLARI</p>', unsafe_allow_html=True)

if os.path.exists(db_siparisler):
    df_siparisler = pd.read_csv(db_siparisler)
    if not df_siparisler.empty:
        tablo_rows_html = ""
        # Sadece son 5 siparişi listele
        for idx, row in df_siparisler.head(5).iterrows():
            durum_stil = '<span style="color:#00ff66;">● Tamamlandı</span>' if idx != 0 else '<span style="color:#ffea00;">⏳ Gönderiliyor</span>'
            tablo_rows_html += f'<tr><td>{row["tarih"]}</td><td>{row["platform"]}</td><td>{row["link"]}</td><td>{row["miktar"]}</td><td>{durum_stil}</td></tr>'
        
        tablo_html = '<table class="siparis-tablo"><tr><th>ZAMAN</th><th>PLATFORM</th><th>HEDEF BAĞLANTI</th><th>MİKTAR</th><th>DURUM</th></tr>' + tablo_rows_html + '</table>'
        st.markdown(tablo_html, unsafe_allow_html=True)
    else:
        st.info("Henüz verilmiş bir sipariş bulunmuyor.")

# 8. ETKİLEŞİM VE İSTATİSTİK PANELİ
st.write("---")
st.markdown('<p style="font-size:16px; font-weight:bold; color:#00ffcc; margin-bottom:8px;">📈 PLATFORM ETKİLEŞİM VE BAŞARI ANALİZİ</p>', unsafe_allow_html=True)
st.metric("👁️ Toplam Ziyaret Sayısı", f"{ziyaret} Kez")
