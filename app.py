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
spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen kurumsal bilgilendirme amaçlu olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# ==========================================
# 2. SABİT SOL MENÜ (SIDEBAR) & GÜVENLİK
# ==========================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

# GİZLİ YÖNETİCİ GİRİŞİ (Şifre: BTA2026)
st.sidebar.subheader("🔒 Yönetici Alanı")
admin_pass = st.sidebar.text_input("Yönetici Şifresi:", type="password", help="Excel yönetimini, mesaj silmeyi ve kayıt düzenlemeyi açar.")
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

# Klasördeki mevcut Excel/Macro dosyalarını algılama
excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]

# ==========================================
# 3. ANA PANEL BAŞLIĞI & EN ÜST SPK UYARISI
# ==========================================
st.title("🧠 BTA Algoritmik İşlem ve Analiz Portalı")
st.warning(spk_metni)
st.markdown("---")

# Sekmeli Menü Tasarımı
tab_excel, tab_bta, tab_chat, tab_members = st.tabs([
    "📂 BTA Excel Veri Analizi", 
    "📈 KONYA Canlı Veri Odası", 
    "💬 Canlı Sohbet Odası",
    "👥 BTA Hissedarları Kayıt Listesi"
])

# ==========================================
# MODÜL 1: EXCEL & MAKRO VERİ İŞLEME (YALNIZCA YÖNETİCİ AYARLI)
# ==========================================
with tab_excel:
    st.header("📂 Excel Veri İnceleme Merkezi")
    varsayilan_dosya = None
    if excel_dosyalari:
        hedef_dosyalar = [f for f in excel_dosyalari if "bta" in f.lower() or "nurican" in f.lower()]
        if hedef_dosyalar:
            varsayilan_dosya = hedef_dosyalar[0]
        else:
            varsayilan_dosya = excel_dosyalari[0]

    secilen_dosya = varsayilan_dosya
    if is_admin:
        st.subheader("🛠️ Yönetici Excel Kontrolleri")
        dosya_kaynagi = st.radio("Dosya Kaynağı Seçin:", ["Klasördeki Dosyaları Kullan", "Yeni Dosya Yükle"])
        if dosya_kaynagi == "Klasördeki Dosyaları Kullan" and excel_dosyalari:
            secilen_dosya = st.selectbox("Analiz Edilecek Dosya:", excel_dosyalari, index=excel_dosyalari.index(varsayilan_dosya) if varsayilan_dosya in excel_dosyalari else 0)
        else:
            secilen_dosya = st.file_uploader("Bir Excel (.xlsx, .xlsm) dosyası yükleyin", type=["xlsx", "xlsm"])
        st.markdown("---")

    if secilen_dosya is not None:
        try:
            excel_obj = pd.ExcelFile(secilen_dosya, engine='openpyxl')
            sayfa_isimleri = excel_obj.sheet_names
            aktif_sayfa = sayfa_isimleri[0]
            if is_admin and len(sayfa_isimleri) > 1:
                aktif_sayfa = st.selectbox("Görüntülenecek Sayfa (Yönetici):", sayfa_isimleri)
            df = pd.read_excel(secilen_dosya, sheet_name=aktif_sayfa, engine='openpyxl')
            
            if not df.empty:
                ilk_sutun_adi = df.columns[0]
                df_goster = df[[ilk_sutun_adi]]
            else:
                df_goster = df
            
            arama_kelimesi = st.text_input("Tablo içinde dinamik filtreleme yapın:", value="KONYA")
            if arama_kelimesi:
                filtre_mask = df_goster.astype(str).apply(lambda x: x.str.contains(arama_kelimesi, case=False)).any(axis=1)
                gosterilecek_df = df_goster[filtre_mask]
            else:
                gosterilecek_df = df_goster
            st.dataframe(gosterilecek_df, use_container_width=True)
        except Exception as e:
            st.error(f"Excel verisi işlenirken bir hata oluştu: {e}")
    else:
        st.info("💡 Sistemde yüklü veya klasörde analiz edilecek Excel dosyası bulunamadı.")

# ==========================================
# MODÜL 2: KONYA CANLI TAKİP & KAR/ZARAR & TAVAN KUTLAMASI
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
        else:
            st.warning("Borsa İstanbul canlı veri sunucularından anlık KONYA verisi şu an alınamadı.")
    except Exception as e:
        st.error(f"Canlı takip motorunda teknik bir aksaklık oluştu: {e}")

# ==========================================
# MODÜL 3: CANLI SOHBET ODASI
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
# MODÜL 4: BTA HİSSEDARLARI KAYIT LİSTESİ (TAMAMLANDI)
# ==========================================
with tab_members:
    st.header("👥 BTA Hissedarları ve Sahip Olunan Hisse Kayıt Listesi")
    st.write("BTA Grubuna dahil olan yatırımcıların elindeki BTA hisselerinin şifresiz kayıt panelidir.")
    
    # Hissedar Ekleme Formu
    st.subheader("➕ Yeni Hissedar Kaydı Ekle")
