import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os

# ==========================================
# 1. SAYFA VE PANEL AYARLARI
# ==========================================
st.set_page_config(
    page_title="BTA Algoritmik İşlem ve Analiz Portalı",
    page_icon="🧠",
    layout="wide"
)

# ==========================================
# GÜVENLİ SPK YASAL METNİ
# ==========================================
spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# ==========================================
# 2. SABİT SOL MENÜ (SIDEBAR) & YENİLEME
# ==========================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

# Otomatik Yenileme Ayarı (5 saniyede bir veri tazeleme)
auto_refresh = st.sidebar.checkbox("Otomatik Yenilemeyi Aktif Et", value=True)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Yenileme Sıklığı (Saniye)", 2, 60, 5)
    st_autorefresh(interval=refresh_interval * 1000, key="bta_refresh_counter")

st.sidebar.markdown("---")
st.sidebar.warning(spk_metni)

# ==========================================
# 3. ANA PANEL - BTA ALGORITMA (TEK ALAN)
# ==========================================
st.title("🧠 BTA Algoritma")
st.warning(spk_metni)
st.markdown("---")

st.header("📈 KONYA Hisse Senedi Canlı Kar/Zarar Takip Paneli")
kurumsal_ticker = "KONYA.IS"
bta_alim_fiyati = 4100.00 

try:
    hisse = yf.Ticker(kurumsal_ticker)
    tarihce = hisse.history(period="2d", interval="1d")
    if not tarihce.empty:
        guncel_fta_fiyati = tarihce['Close'].iloc[-1]
        gunluk_degisim_yuzde = hisse.info.get('regularMarketChangePercent', 0.0)
        
        if gunluk_degisim_yuzde == 0.0 and len(tarihce) > 1:
            onceki_kapanis = tarihce['Close'].iloc[-2]
            gunluk_degisim_yuzde = ((guncel_fta_fiyati - onceki_kapanis) / onceki_kapanis) * 100
        
        kar_zarar_tutari = guncel_fta_fiyati - bta_alim_fiyati
        kar_zarar_yuzdesi = (kar_zarar_tutari / bta_alim_fiyati) * 100
        
        if gunluk_degisim_yuzde >= 9.90 or kar_zarar_yuzdesi >= 9.0:
            st.balloons()
            st.snow()
            st.success("🚀 **ODADA KUTLAMALAR BAŞLASIN! KONYA HİSSESİ ANLIK OLARAK TAVAN OLDU VEYA +%9 KAR MARJINI AŞTI!** 🥳🎉")
        
        st.subheader("📊 Canlı Hesap Tablosu ve Portföy Durumu")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Anlık Canlı FTA Fiyatı", f"{guncel_fta_fiyati:.2f} TL", f"{gunluk_degisim_yuzde:.2f}% (Günlük)")
        c2.metric("Sizin Alım Maliyetiniz", f"{bta_alim_fiyati:.2f} TL")
        
        if kar_zarar_tutari >= 0:
            c3.metric("Net Kar/Zarar Durumu (TL)", f"+{kar_zarar_tutari:.2f} TL")
            c4.metric("Toplam Kar Oranınız", f"+% {kar_zarar_yuzdesi:.2f}")
        else:
            c3.metric("Net Kar/Zarar Durumu (TL)", f"{kar_zarar_tutari:.2f} TL")
            c4.metric("Toplam Zarar Oranınız", f"% {kar_zarar_yuzdesi:.2f}")
        
        st.subheader("📊 KONYA - Gün İçi Canlı Fiyat Grafik Trendi")
        st.line_chart(tarihce['Close'])
    else:
        st.warning("Borsa İstanbul canlı veri sunucularından anlık KONYA verisi şu an alınamadı.")
except Exception as e:
    st.error(f"Canlı takip motorunda teknik bir aksaklık oluştu: {e}")
