import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SAYFA VE KESİN SOL MENÜSÜZ AYARLAR
# ==========================================
st.set_page_config(
    page_title="BTA KONYA Canlı Veri Odası",
    page_icon="🧠",
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
# 🌌 EN ARKA PANELİN RENGİNİ BAŞTAN AŞAĞI DEĞİŞTİREN CSS
# ==========================================
st.markdown("""
<style>
    /* Sol menüyü tamamen yok etme */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], button[title="View sidebar"] {
        display: none !important;
        width: 0px !important;
    }
    
    /* 🚀 İSTEK: EN ARKA PANELİ (TÜM TARAYICI DUVARINI) CANLI VE RENKLİ YAPMA */
    /* Koyu/siyah renkler tamamen kaldırıldı. Yerine borsa yeşili ve canlı siber maviden oluşan parlayan harika bir gradient fon serildi */
    html, body, [data-testid="stAppViewContainer"], .main {
        background: linear-gradient(135deg, #0b2520 0%, #0d253f 50%, #1c1330 100%) !important;
        background-attachment: fixed !important;
        color: #ffffff !important;
    }
    .stApp {
        background-color: transparent !important;
    }

    /* Tam Ekran Dijital Matris Kare Çizgileri */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.02) 1.5px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1.5px, transparent 1px);
        background-size: 40px 40px;
        z-index: -1;
        pointer-events: none;
    }

    /* Şık Borsa Hesaplama Kutuları */
    div[data-testid="stMetric"] {
        background: rgba(15, 32, 67, 0.75) !important;
        padding: 22px !important;
        border-radius: 14px !important;
        border: 2px solid #00b0ff !important;
        box-shadow: 0 0 20px rgba(0, 176, 255, 0.3) !important;
        backdrop-filter: blur(5px);
    }

    /* 🧠 LOGO PANELİ */
    .bta-logo-box {
        text-align: center;
        padding: 25px 0;
        margin-bottom: 20px;
        background: rgba(10, 20, 40, 0.65);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(5px);
    }
    /* Net ve Sabit Beyin Amblemi */
    .bta-brain-fixed {
        font-size: 60px;
        vertical-align: middle;
        margin-right: 20px;
        display: inline-block;
    }
    
    /* 💎 BTA HAREKETLİ GÖKKUŞAĞI YAZISI VE EKSTRA YOĞUN GÖLGELENDİRME */
    .bta-neon-rainbow {
        font-family: 'Great Vibes', cursive;
        font-size: 110px;
        font-weight: bold;
        letter-spacing: 6px;
        background: linear-gradient(90deg, #ff007f, #7000ff, #00b0ff, #00e676, #ffeb3b, #ff007f);
        background-size: 400% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: rainbowFlow 5s linear infinite, waveMotion 2.5s ease-in-out infinite alternate;
        display: inline-block;
        vertical-align: middle;
        /* Canlı fona uyumlu yoğun gölge katmanları */
        filter: drop-shadow(2px 6px 12px rgba(0, 0, 0, 0.9)) 
                drop-shadow(0 0 20px rgba(255, 0, 127, 0.6)) 
                drop-shadow(0 0 35px rgba(0, 230, 118, 0.5));
    }
    
    @keyframes rainbowFlow {
        0% { background-position: 0% 50%; }
        100% { background-position: 400% 50%; }
    }
    @keyframes waveMotion {
        0% { transform: translateY(-4px) scale(0.98); }
        100% { transform: translateY(4px) scale(1.02); }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 🧠 SABİT BEYNİLİ & GÖKKUŞAĞI BTA LOGO PANELİ
# ==========================================
st.markdown("""
<div class='bta-logo-box'>
    <span class='bta-brain-fixed'>🧠</span>
    <div class='bta-neon-rainbow'>BTA</div>
</div>
""", unsafe_allow_html=True)

st.warning(spk_metni)
st.markdown("---")

st.subheader("📈 KONYA Hisse Senedi Canlı Kar/Zarar Takip Paneli")

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
    
    st.info("⏱️ Borsa İstanbul (BIST) verileri yasal mevzuatlar gereği en az **15 dakika gecikmeli** olarak yansımaktadır.")
    
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
