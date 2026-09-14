import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import os
from datetime import datetime

# ==========================================
# 1. SAYFA VE MOBİL UYUMLULUK AYARLARI
# ==========================================
st.set_page_config(
    page_title="BTA Algoritmik İşlem",
    page_icon="🧠",
    layout="wide"
)

# Mobil Telefonlar İçin Tam Uyum CSS
mobil_css = """
<style>
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}
div[data-testid="stDataFrame"] {
    width: 100% !important;
    overflow-x: auto !important;
}
.stButton button {
    width: 100% !important;
}
/* Yasal uyarıyı küçültme tasarımı */
.kucuk-yasal-metin {
    font-size: 11px !important;
    color: #9ca3af !important;
    text-align: justify;
    line-height: 1.4;
    background-color: #121d33;
    padding: 10px;
    border-radius: 6px;
    border-left: 3px solid #ff3344;
    margin-top: 20px;
}
</style>
"""
st.markdown(mobil_css, unsafe_allow_html=True)

# Canlı Sohbet Hafızası Sabitleri
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"id": 9999, "user": "Sistem", "time": "12:00:00", "text": "BTA Algoritmik Canlı Sohbet Odasına Hoş Geldiniz!"}
    ]

# Hissedar BTA Hisse Kayıt Listesi Hafızası
if "bta_members_list" not in st.session_state:
    st.session_state["bta_members_list"] = [
        {"id": 8888, "Hissedar Adı": "Nurican Bey", "Sahip Olduğu BTA Hissesi": "KONYA.IS", "Hisse Maliyeti (TL)": 4100.0, "Adet": 10}
    ]

# TELEGRAM TARZI KATILIMCI SAYAÇ MOTORU
db_istatistik = "bta_site_istatistik_db.csv"
if not os.path.exists(db_istatistik):
    pd.DataFrame([], columns=["ziyaret_sayisi", "basarili_oy", "basarisiz_oy"]).to_csv(db_istatistik, index=False)

katilimci_sayisi = 1
try:
    df_ist = pd.read_csv(db_istatistik)
    if "ziyaret_sayildi" not in st.session_state:
        df_ist.at[0, "ziyaret_sayisi"] = int(df_ist.at[0, "ziyaret_sayisi"]) + 1
        df_ist.to_csv(db_istatistik, index=False)
        st.session_state["ziyaret_sayildi"] = True
    katilimci_sayisi = int(df_ist.at[0, "ziyaret_sayisi"])
except:
    pass

# SPK YASAL METNİ (Değişken olarak saklanıyor, sadece en altta gösterilecek)
spk_metni = "⚠️ SPK YASAL UYARI NOTU: Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Buradaki yorumlar kişisel görüşlere dayanmaktadır. Sadece buradaki bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Bu platformda sunulan veriler tamamen bilgilendirme amaçlı olup, kesinlikle bir 'AL', 'SAT' veya 'TUT' tavsiyesi niteliği taşımamaktadır."

# ==========================================
# 2. SABİT SOL MENÜ (SIDEBAR) & GÜVENLİK
# ==========================================
st.sidebar.header("⚙️ Sistem Kontrolleri")

# GİZLİ YÖNETİCİ GİRİŞİ (Şifre: BTA2026)
st.sidebar.subheader("🔒 Yönetici Alanı")
admin_pass = st.sidebar.text_input("Yönetici Şifresi:", type="password")
is_admin = (admin_pass == "BTA2026")

if is_admin:
    st.sidebar.success("⚡ Yönetici Yetkileri Aktif!")

# Otomatik Yenileme Ayarı
auto_refresh = st.sidebar.checkbox("Otomatik Yenileme", value=True)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Saniye", 2, 60, 5)
    st_autorefresh(interval=refresh_interval * 1000, key="bta_refresh_counter")

# SPK Uyarısını Sol Menünün En Altına Alıyoruz
st.sidebar.markdown("---")
st.sidebar.markdown(f'<div class="kucuk-yasal-metin">{spk_metni}</div>', unsafe_allow_html=True)

# Klasördeki mevcut Excel dosyalarını algılama
excel_dosyalari = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]

# ==========================================
# 3. ANA PANEL ÜST BAR (TEMİZ VE SADE BAŞLIK)
# ==========================================
top_col1, top_col2 = st.columns([0.7, 0.3])
with top_col1:
    st.subheader("🧠 BTA İşlem Portalı")
with top_col2:
    st.markdown(f"📢 **Katılımcı:** `{katilimci_sayisi} Üye`")

# Sekmeli Menü Tasarımı
tab_excel, tab_bta, tab_chat, tab_members = st.tabs([
    "📂 Excel Veri", 
    "📈 KONYA Canlı", 
    "💬 Canlı Sohbet",
    "👥 Hissedarlar"
])

# ==========================================
# MODÜL 1: EXCEL VERİ İNCELEME
# ==========================================
with tab_excel:
    st.header("📂 Excel Veri İnceleme")
    varsayilan_dosya = None
    if excel_dosyalari:
        hedef_dosyalar = [f for f in excel_dosyalari if "bta" in f.lower() or "nurican" in f.lower()]
        if hedef_dosyalar:
            varsayilan_dosya = hedef_dosyalar[0]
        else:
            varsayilan_dosya = excel_dosyalari[0]

    secilen_dosya = varsayilan_dosya
    if is_admin:
        st.subheader("🛠️ Yönetici Kontrolleri")
        dosya_kaynagi = st.radio("Dosya Kaynağı:", ["Klasördeki Dosyalar", "Yeni Dosya Yükle"])
        if dosya_kaynagi == "Klasördeki Dosyaları Kullan" and excel_dosyalari:
            secilen_dosya = st.selectbox("Analiz Edilecek Dosya:", excel_dosyalari, index=excel_dosyalari.index(varsayilan_dosya) if varsayilan_dosya in excel_dosyalari else 0)
        else:
            secilen_dosya = st.file_uploader("Excel Yükle", type=["xlsx", "xlsm"])
        st.markdown("---")

    if secilen_dosya is not None:
        try:
            excel_obj = pd.ExcelFile(secilen_dosya, engine='openpyxl')
            sayfa_isimleri = excel_obj.sheet_names
            aktif_sayfa = sayfa_isimleri[0]
            if is_admin and len(sayfa_isimleri) > 1:
                aktif_sayfa = st.selectbox("Sayfa Seç (Yönetici):", sayfa_isimleri)
            df = pd.read_excel(secilen_dosya, sheet_name=aktif_sayfa, engine='openpyxl')
            
            if not df.empty:
                df_goster = df[[df.columns[0]]]
            else:
                df_goster = df
            
            arama_kelimesi = st.text_input("Filtrele:", value="KONYA")
            if arama_kelimesi:
                filtre_mask = df_goster.astype(str).apply(lambda x: x.str.contains(arama_kelimesi, case=False)).any(axis=1)
                gosterilecek_df = df_goster[filtre_mask]
            else:
                gosterilecek_df = df_goster
            st.dataframe(gosterilecek_df, use_container_width=True)
        except Exception as e:
            st.error(f"Excel Hatası: {e}")
    else:
        st.info("💡 Analiz edilecek Excel dosyası bulunamadı.")

# ==========================================
# MODÜL 2: KONYA CANLI TAKİP
# ==========================================
with tab_bta:
    st.header("📈 KONYA Canlı Takip Paneli")
    kurumsal_ticker = "KONYA.IS"
    bta_alim_fiyati = 4100.00 
    try:
        hisse = yf.Ticker(kurumsal_ticker)
        tarihce = hisse.history(period="2d", interval="1d")
        if not tarihce.empty:
            guncel_fta_fiyati = float(tarihce['Close'].iloc[-1])
            gunluk_degisim_yuzde = float(hisse.info.get('regularMarketChangePercent', 0.0))
            if gunluk_degisim_yuzde == 0.0 and len(tarihce) > 1:
                onceki_kapanis = float(tarihce['Close'].iloc[-2])
                gunluk_degisim_yuzde = ((guncel_fta_fiyati - onceki_kapanis) / onceki_kapanis) * 100
            kar_zarar_tutari = guncel_fta_fiyati - bta_alim_fiyati
            kar_zarar_yuzdesi = (kar_zarar_tutari / bta_alim_fiyati) * 100
            
            if gunluk_degisim_yuzde >= 9.90 or kar_zarar_yuzdesi >= 9.0:
                st.balloons()
                st.success("🚀 **KONYA TAVAN VEYA +%9 ÜZERİ PERFORMANS GÖSTERDİ!** 🥳🎉")
                
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Anlık Fiyat", f"{guncel_fta_fiyati:.2f} TL", f"{gunluk_degisim_yuzde:.2f}%")
            with c2:
                st.metric("Maliyetiniz", f"{bta_alim_fiyati:.2f} TL")
                
            c3, c4 = st.columns(2)
            with c3:
                st.metric("Net K/Z (TL)", f"{kar_zarar_tutari:+.2f} TL")
            with c4:
                st.metric("Kar Oranı", f"% {kar_zarar_yuzdesi:+.2f}")
        else:
            st.warning("Anlık veri şu an alınamadı.")
    except Exception as e:
        st.error(f"Takip motoru hatası: {e}")

# ==========================================
# MODÜL 3: CANLI SOHBET ODASI (TAMAMEN DÜZELTİLDİ)
# ==========================================
with tab_chat:
    st.header("💬 Canlı Sohbet Odası")
    nickname = st.text_input("Takma Adınız:", value="Hissedar", key="chat_nick")
    
    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_input("Mesajınız:")
        submit_button = st.form_submit_button("Gönder 🚀")
        if submit_button and user_message:
            now_str = datetime.now().strftime("%H:%M:%S")
            msg_id = int(datetime.now().timestamp() * 1000)
            st.session_state["chat_messages"].append({"id": msg_id, "user": nickname, "time": now_str, "text": user_message})
            st.rerun()

    st.write("---")
    st.subheader("📝 Mesaj Akışı")
    
    # Hatalı 'with cols:' yapısı düzeltildi, kararlı yerleşime geçildi
    for idx, msg in enumerate(reversed(st.session_state["chat_messages"])):
        col_m1, col_m2 = st.columns([0.8, 0.2])
        with col_m1:
            st.markdown(f"**[{msg['time']}] {msg['user']}:** {msg['text']}")
        with col_col2 := col_m2:
            if is_admin:
                if st.button("❌ Sil", key=f"del_msg_{msg['id']}_{idx}"):
                    st.session_state["chat_messages"] = [m for m in st.session_state["chat_messages"] if m.get("id") != msg["id"]]
                    st.rerun()
        st.divider()

# ==========================================
# MODÜL 4: BTA HİSSEDARLARI KAYIT LİSTESİ
# ==========================================
with tab_members:
    st.header("👥 Hissedarlar Kayıt Listesi")
    
    with st.form("add_member_form", clear_on_submit=True):
        m_name = st.text_input("Hissedar Adı Soyadı:")
