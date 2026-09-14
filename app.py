import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SAYFA VE KESİN SOL MENÜSÜZ AYARLAR
# ==========================================
st.set_page_config(
    page_title="BTA KONYA Canlı Veri Odası",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Arka planda 5 saniyede bir otomatik yenileme tetikleyici
st_autorefresh(interval=5000, key="bta_terminal_refresh")

if "begeniler" not in st.session_state:
    st.session_state["begeniler"] = 0
if "yildizlar" not in st.session_state:
    st.session_state["yildizlar"] = 5.0

# SPK RESMİ YASAL UYARI METNİ
spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# ==========================================
# 🌌 TRADINGVIEW TERMİNALİ VE HAREKETLİ EL YAZISI LOGO (CSS)
# ==========================================
st.markdown("""
<style>
    @import url('https://googleapis.com');

    /* Sol menüyü tamamen yok etme */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], button[title="View sidebar"] {
        display: none !important;
        width: 0px !important;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0c0f14 !important;
        color: #d1d4dc !important;
    }
    .stApp {
        background-color: #0c0f14 !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #d1d4dc !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    .stMetric {
        background-color: #131722 !important;
        padding: 15px !important;
        border-radius: 6px !important;
        border: 1px solid #2a2e39 !important;
    }

    /* 🧠 ŞIK HAREKETLİ BTA EL YAZISI ANIMASYONU */
    .bta-logo-container {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 10px;
    }
    .bta-neon-text {
        font-family: 'Great Vibes', cursive; /* Zarif ve Şık El Yazısı Fontu */
        font-size: 90px;
        font-weight: bold;
        color: #089981;
        text-shadow: 0 0 10px #089981, 0 0 20px #089981, 0 0 40px #2962ff;
        animation: btaGlow 3s ease-in-out infinite alternate;
        display: inline-block;
    }
    @keyframes btaGlow {
        0% {
            transform: scale(0.98);
            text-shadow: 0 0 10px #089981, 0 0 20px #089981, 0 0 30px #2962ff;
        }
        100% {
            transform: scale(1.02);
            text-shadow: 0 0 15px #00e676, 0 0 30px #00e676, 0 0 50px #2979ff;
            color: #00e676;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HAREKETLİ EL YAZISI BTA BAŞLIĞI & SPK UYARISI
# ==========================================
# Göz yoran standart başlık yerine hareketli şık logo basılıyor
st.markdown("<div class='bta-logo-container'><div class='bta-neon-text'>Bta</div></div>", unsafe_allow_html=True)

st.warning(spk_metni)
st.markdown("---")

st.header("📈 KONYA Hisse Senedi Canlı Kar/Zarar Takip Paneli")

# Sabit BTA Alım Fiyat Referansı
bta_alim_fiyati = 4100.00
kurumsal_ticker = "KONYA.IS"

guncel_fta_fiyati = bta_alim_fiyati
gunluk_degisim_yuzde = 0.0
borsa_verisi_tamam = False
tarihce = pd.DataFrame()

try:
    hisse = yf.Ticker(kurumsal_ticker)
    tarihce = hisse.history(period="2d", interval="1d")
    if not tarihce.empty:
        guncel_fta_fiyati = tarihce['Close'].iloc[-1]
        gunluk_degisim_yuzde = hisse.info.get('regularMarketChangePercent', 0.0)
        if gunluk_degisim_yuzde == 0.0 and len(tarihce) > 1:
            onceki_kapanis = tarihce['Close'].iloc[-2]
            gunluk_degisim_yuzde = ((guncel_fta_fiyati - onceki_kapanis) / onceki_kapanis) * 100
        borsa_verisi_tamam = True
except:
    pass

if borsa_verisi_tamam:
    kar_zarar_tutari = guncel_fta_fiyati - bta_alim_fiyati
    kar_zarar_yuzdesi = (kar_zarar_tutari / bta_alim_fiyati) * 100
    
    # KONYA Günlük tavan veya %9 üstü toplam kârda konfetiler patlar
    if gunluk_degisim_yuzde >= 9.90 or kar_zarar_yuzdesi >= 9.0:
        st.balloons()
        st.snow()
        st.success("🚀 **ODADA KUTLAMALAR BAŞLASIN! KONYA HİSSESİ ANLIK OLARAK TAVAN OLDU VEYA +%9 KAR MARJINI AŞTI!** 🥳🎉")
    
    st.subheader("📊 Canlı Hesap Tablosu")
    st.warning("⏱️ Borsa İstanbul (BIST) verileri yasal mevzuatlar gereği en az **15 dakika gecikmeli** olarak yansımaktadır.")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Anlık Canlı FTA Fiyatı", f"{guncel_fta_fiyati:.2f} TL", f"{gunluk_degisim_yuzde:.2f}% (Günlük)")
    c2.metric("Sabit BTA Alım Fiyatı", f"{bta_alim_fiyati:.2f} TL")
    
    if kar_zarar_tutari >= 0:
        c3.metric("Net Kar/Zarar Durumu (TL)", f"+{kar_zarar_tutari:.2f} TL")
        c4.metric("Toplam Kar Oranınız", f"+% {kar_zarar_yuzdesi:.2f}")
    else:
        c3.metric("Net Kar/Zarar Durumu (TL)", f"{kar_zarar_tutari:.2f} TL")
        c4.metric("Toplam Zarar Oranınız", f"% {kar_zarar_yuzdesi:.2f}")
        
    st.markdown("---")
    st.subheader("⭐ Oda Değerlendirmesi & Topluluk Reaksiyonu")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.write(f"👍 Toplam Oda Beğenisi: **{st.session_state['begeniler']}**")
        if st.button("Portföyü Beğen 👍", key="like_btn"):
            st.session_state["begeniler"] += 1
            st.rerun()
    with col_r2:
        st.session_state["yildizlar"] = st.slider("Algoritmaya Yıldız Ver:", 1.0, 5.0, float(st.session_state["yildizlar"]), step=0.5)
        
    st.markdown("---")
    st.subheader("📊 KONYA - Gün İçi Canlı Fiyat Grafik Trendi")
    st.line_chart(tarihce['Close'])
else:
    st.warning("⚠️ Borsa İstanbul canlı veri sunucularından anlık KONYA verisi şu an alınamadı. Lütfen birkaç saniye sonra sayfayı yenileyin.")
