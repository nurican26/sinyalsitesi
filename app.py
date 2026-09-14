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
# 🌌 DEĞİŞTİRİLEN CANLI ARKA PLAN VE BTA GÖLGELENDİRME (CSS)
# ==========================================
st.markdown("""
<style>
    @import url('https://googleapis.com');

    /* Sol menüyü tamamen yok etme */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], button[title="View sidebar"] {
        display: none !important;
        width: 0px !important;
    }
    
    /* 🌌 ARKA PLAN: Koyu mavilik açıldı! Canlı ve berrak bir kurumsal finans rengine kavuşturuldu */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #111e38 !important; /* Canlı kurumsal lacivert/mavi tonu */
        background-image: 
            radial-gradient(circle at 50% 40%, #172c4f 0%, #0a1424 100%),
            linear-gradient(rgba(255, 255, 255, 0.03) 1.5px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1.5px, transparent 1px) !important;
        background-size: 100% 100%, 35px 30px, 35px 30px !important;
        color: #f3f4f6 !important;
    }
    .stApp {
        background-color: transparent !important;
    }

    /* Siber Işıklı Borsa Hesaplama Kutuları */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #0f2042 0%, #1a325c 100%) !important;
        padding: 22px !important;
        border-radius: 14px !important;
        border: 2px solid #3b82f6 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.3) !important;
    }

    /* 🧠 LOGO PANELİ */
    .bta-logo-box {
        text-align: center;
        padding: 25px 0;
        margin-bottom: 20px;
        background: rgba(15, 32, 66, 0.7);
        border-radius: 16px;
        border: 1px solid #2d4263;
        box-shadow: inset 0 0 25px rgba(59, 130, 246, 0.2);
    }
    /* Net ve sabit duran Beyin İkonu */
    .bta-brain-fixed {
        font-size: 60px;
        vertical-align: middle;
        margin-right: 20px;
        display: inline-block;
    }
    
    /* 💎 BTA HAREKETLİ GÖKKUŞAĞI VE YOĞUN GÖLGELENDİRME EFEKTİ */
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
        /* 🚀 İSTEK: BTA Yazısının arkasına çok katmanlı muazzam bir siber gölgelendirme eklendi */
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.8)) 
                drop-shadow(0 0 15px rgba(112, 0, 255, 0.7)) 
                drop-shadow(0 0 30px rgba(0, 176, 255, 0.5));
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
# 3. 🧠 SABİT BEYNİLİ & DERİN GÖLGELİ BTA LOGO PANELİ
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
