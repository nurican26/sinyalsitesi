import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os
from datetime import datetime

# ==========================================
# 1. SAYFA VE PANEL AYARLARI
# ==========================================
st.set_page_config(
    page_title="BTA Algoritmik İşlem ve Analiz Portalı",
    page_icon="🧠",
    layout="wide"
)

# Canlı Sohbet Hafızası Koruma Mekanizması
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"id": 9999, "user": "Sistem", "time": "12:00:00", "text": "BTA Algoritmik Canlı Sohbet Odasına Hoş Geldiniz!"}
    ]
else:
    for i, msg in enumerate(st.session_state["chat_messages"]):
        if "id" not in msg:
            msg["id"] = int(datetime.now().timestamp() * 1000) + i

# Hissedar BTA Hisse Kayıt Listesi Hafızası
if "bta_members_list" not in st.session_state:
    st.session_state["bta_members_list"] = [
        {"id": 8888, "Hissedar Adı": "Nurican Bey", "Sahip Olduğu BTA Hissesi": "KONYA.IS", "Hisse Maliyeti (TL)": 4100.0, "Adet": 10}
    ]

# ==========================================
# GÜVENLİ VE HATA VERMEYEN SPK YASAL METNİ
# ==========================================
spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# ==========================================
# 2. SABİT SOL MENÜ (SIDEBAR) & GÜVENLİK
# ==========================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

# GİZLİ YÖNETİCİ GİRİŞİ (Şifre: BTA2026)
st.sidebar.subheader("🔒 Yönetici Alanı")
admin_pass = st.sidebar.text_input("Yönetici Şifresi:", type="password", help="Mesaj silmeyi ve kayıt düzenlemeyi açar.")
is_admin = (admin_pass == "BTA2026")

if is_admin:
    st.sidebar.success("⚡ Yönetici Yetkileri Aktif!")

# Otomatik Yenileme Ayarı (5 saniyede bir veri tazeleme)
auto_refresh = st.sidebar.checkbox("Otomatik Yenilemeyi Aktif Et", value=True)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Yenileme Sıklığı (Saniye)", 2, 60, 5)
    st_autorefresh(interval=refresh_interval * 1000, key="bta_refresh_counter")

# Sol menü tabanına SPK uyarısını çakıyoruz
st.sidebar.markdown("---")
st.sidebar.warning(spk_metni)

# ==========================================
# 3. ANA PANEL BAŞLIĞI & EN ÜST SPK UYARISI
# ==========================================
st.title("🧠 BTA Algoritmik İşlem ve Analiz Portalı")
st.warning(spk_metni)
st.markdown("---")

# Sekmeli Menü Tasarımı (Talebiniz üzere Excel kalktı, ana sekme BTA Algoritma oldu)
tab_bta, tab_chat, tab_members = st.tabs([
    "🧠 BTA Algoritma", 
    "💬 Canlı Sohbet Odası",
    "👥 BTA Hissedarları Kayıt Listesi"
])

# ==========================================
# MODÜL 1: BTA ALGORİTMA - KONYA CANLI TAKİP
# ==========================================
with tab_bta:
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

# ==========================================
# MODÜL 2: CANLI SOHBET ODASI
# ==========================================
with tab_chat:
    st.header("💬 BTA Genel Canlı Sohbet Odası")
    st.write("Sohbet odası herkese açıktır. Mesajlaşmaya hemen başlayabilirsiniz.")
    nickname = st.text_input("Sohbet Takma Adınız:", value="Hissedar", key="chat_nick")
    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_input("Mesajınızı yazın:")
        submit_button = st.form_submit_button("Gönder 🚀")
        if submit_button and user_message:
            now_str = datetime.now().strftime("%H:%M:%S")
            msg_id = int(datetime.now().timestamp() * 1000)
            st.session_state["chat_messages"].append({"id": msg_id, "user": nickname, "time": now_str, "text": user_message})
            st.rerun()

    st.subheader("📝 Oda Akışı")
    for idx, msg in enumerate(reversed(st.session_state["chat_messages"])):
        if "id" in msg:
            cols = st.columns([0.85, 0.15])
            with cols[0]:
                st.markdown(f"**[{msg['time']}] {msg['user']}:** {msg['text']}")
            with cols[1]:
                if is_admin:
                    if st.button("❌ Mesajı Sil", key=f"del_msg_{msg['id']}_{idx}"):
                        st.session_state["chat_messages"] = [m for m in st.session_state["chat_messages"] if m.get("id") != msg["id"]]
                        st.rerun()
            st.divider()

# ==========================================
# MODÜL 3: BTA HİSSEDARLARI KAYIT LİSTESİ
# ==========================================
with tab_members:
    st.header("👥 BTA Hissedarları ve Sahip Olunan Hisse Kayıt Listesi")
    st.write("BTA Grubuna dahil olan yatırımcıların elindeki BTA hisselerini şifresiz kayıt panelidir.")
