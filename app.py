import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# CSS Tasarımı - Sitenin Görsel Kimliği
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; 
        padding: 0.5rem;
    } 
    h1,h2,h3,h4,h5,h6,p,span,label {
        color: #fff!important; 
        font-family: "Segoe UI", sans-serif;
    } 
    input {
        color: #000!important; 
        background-color: #fff!important;
    } 
    .stDataFrame {
        width: 100% !important; 
        border: 1px solid #10b981 !important; 
        border-radius: 8px;
    } 
    div.block-container {
        padding-top: 1rem; 
        padding-bottom: 0.5rem;
    } 
    .alsat-baslik {
        background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); 
        padding: 8px; 
        border-radius: 5px; 
        font-weight: bold; 
        margin-bottom: 5px;
    } 
    .al-baslik {
        background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); 
        padding: 8px; 
        border-radius: 5px; 
        font-weight: bold; 
        margin-bottom: 5px;
    } 
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        font-size: 1.25rem !important; 
        font-weight: bold !important; 
        color: #ffffff !important;
    } 
    .piyasa-kutusu {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #3b82f6;
        text-align: center;
        margin-bottom: 10px;
    }
    .spk-kutusu {
        background: rgba(231, 76, 60, 0.1);
        border-left: 5px solid #e74c3c;
        padding: 15px;
        border-radius: 6px;
        margin-top: 30px;
        font-size: 0.85rem;
        color: #cccccc !important;
    }
</style>
""", unsafe_allow_html=True)

# 🔑 PARAMETRELER
YONETICI_SIFRESI = "3015"

# Hafıza Kontrolleri
if "oda_kilitli_mi" not in st.session_state: st.session_state["oda_kilitli_mi"] = False
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}
if "sohbet_gecmisi" not in st.session_state: st.session_state["sohbet_gecmisi"] = []

st.title("📈 BTA SİNYAL MERKEZİ")

# --- 🛠️ SOL MENÜ: ODA YÖNETİM MERKEZİ ---
st.sidebar.markdown("### 🛠️ Oda Yönetim Merkezi")
admin_sifre = st.sidebar.text_input("Yönetici Şifresi:", type="password", placeholder="Ayarlar için girin...")

if admin_sifre == YONETICI_SIFRESI:
    st.sidebar.success("⚡ Yatırım Yetkisi Aktif")
    if st.session_state["oda_kilitli_mi"]:
        st.sidebar.error("🔴 Şu an: ODA KİLİTLİ")
        if st.sidebar.button("🔓 Odayı Herkese Aç", use_container_width=True):
            st.session_state["oda_kilitli_mi"] = False
            st.rerun()
    else:
        st.sidebar.success("🟢 Şu an: HERKESE AÇIK")
        if st.sidebar.button("🔒 Odayı Herkese Kilitle", use_container_width=True):
            st.session_state["oda_kilitli_mi"] = True
            st.rerun()

# --- 🏢 DURUM KONTROLÜ VE İÇERİK ---
if st.session_state["oda_kilitli_mi"] and admin_sifre != YONETICI_SIFRESI:
    st.markdown('<div class="kilit-uyari">🔒 <b>BTA Sinyal Odası Geçici Olarak Kilitlenmiştir!</b><br>Analiz robotları ve sistem verileri şu an güncelleniyor. Lütfen daha sonra tekrar deneyiniz.</div>', unsafe_allow_html=True)
else:
    # --- 📊 CANLI PİYASA TAKİP ALANI ---
    st.markdown("### 📊 Canlı Piyasa Takip Ekranı")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown('<div class="piyasa-kutusu"><h4>📉 BIST 100</h4><h2>14.012,42</h2><p style="color:#2ecc71!important; margin:0;">+%0.57</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="piyasa-kutusu"><h4>🟡 Gram Altın</h4><h2>6.857 TL</h2><p style="color:#e74c3c!important; margin:0;">-%1.30</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="piyasa-kutusu"><h4>🪙 Çeyrek Altın</h4><h2>11.246 TL</h2><p style="color:#e74c3c!important; margin:0;">-%0.74</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="piyasa-kutusu"><h4>🥈 Yarım Altın</h4><h2>22.492 TL</h2><p style="color:#e74c3c!important; margin:0;">-%0.74</p></div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="piyasa-kutusu"><h4>👑 Tam Altın</h4><h2>44.984 TL</h2><p style="color:#e74c3c!important; margin:0;">-%0.74</p></div>', unsafe_allow_html=True)

    # Excel Okuma
    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: 
            df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except Exception as e:
            st.error(f"Excel okuma hatası: {e}")

    # Fiyat Motoru
    def hızlı_canli_fiyat_bul(hisse_kodu):
        if not hisse_kodu: return 0.0
        if hisse_kodu in st.session_state["fiyat_hafizasi"]:
            saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
            if time.time() - saved_time < 300: return saved_price
        try:
            ticker = yf.Ticker(f"{hisse_kodu}.IS")
            data = ticker.history(period="1d")
            if not data.empty and not pd.isna(data['Close'].iloc[-1]):
                fiyat = float(data['Close'].iloc[-1])
                st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
                return fiyat
        except: pass
        return 0.0

    def temiz_metin_al(val):
        if pd.isna(val): return ""
        return str(val).strip().upper()

    def listeyi_sadece_hisse_yap(ham_metin):
        ad = str(ham_metin).replace("[", "").replace("]", "").replace("'", "").replace('"', '').replace(" ", "")
        ad = ad.replace(",AL", "").replace(",SAT", "").replace(",_SAT", "").replace(",_AL", "")
        return ad.strip()

    tablo_alsat = []
    tablo_al = []

    if df_kaynak is not None:
        for idx in range(2, len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 22:
                    uv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 20])
                    wv_degeri = temiz_metin_al(df_kaynak.iloc[idx, 22])
                    t_degeri = temiz_metin_al(df_kaynak.iloc[idx, 19])
                    
                    if uv_degeri and uv_degeri not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                        hisse_ara = re.findall(r'[A-Z]+', uv_degeri)
                        if hisse_ara:
                            temiz_isim = listeyi_sadece_hisse_yap(hisse_ara)
                            if temiz_isim:
                                canli_fiyat = hızlı_canli_fiyat_bul(temiz_isim)
                                puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                                bta_puan = puan_bul if puan_bul else (t_degeri if t_degeri else uv_degeri)
                                tablo_alsat.append({"Hisse Kodu 📈": temiz_isim, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."})
                    
                    if wv_degeri and wv_degeri not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                        hisse_ara = re.findall(r'[A-Z]+', wv_degeri)
                        if hisse_ara:
                            temiz_isim = listeyi_sadece_hisse_yap(hisse_ara)
                            if temiz_isim:
                                canli_fiyat = hızlı_canli_fiyat_bul(temiz_isim)
                                puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                                bta_puan = puan_bul if puan_bul else (t_degeri if t_degeri else uv_degeri)
                                tablo_al.append({"Hisse Kodu 📈": temiz_isim, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."})
            except Exception as e:
                pass

        # --- 🔍 HAFIZADA SABİT DURAN ARAMA MOTORU ---
        st.markdown("### 🔍 BTA Gelişmiş Hisse Tarama Motoru")
        arama_kutusu = st.text_input("Aramak istediğiniz hisse kodunu yazın:", placeholder="Örn: SONME, THYAO...", key="ana_hisse_arama_motoru").upper().strip()

        df_alsat_son = pd.DataFrame(tablo_alsat)
        df_al_son = pd.DataFrame(tablo_al)

        if arama_kutusu:
            if not df_alsat_son.empty:
                df_alsat_son = df_alsat_son[df_alsat_son["Hisse Kodu 📈"].str.contains(arama_kutusu, na=False)]
            if not df_al_son.empty:
                df_al_son = df_al_son[df_al_son["Hisse Kodu 📈"].str.contains(arama_kutusu, na=False)]

        # --- 🖥️ TABLOLARIN GÖSTERİMİ ---
        st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
        if not df_alsat_son.empty:
            st.dataframe(df_alsat_son, use_container_width=True, hide_index=True)
        else:
            st.info("Dönemsel sinyal listesi yükleniyor...")

        st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
        if not df_al_son.empty:
            st.dataframe(df_al_son, use_container_width=True, hide_index=True)
        else:
            st.info("BTA sinyal listesi yükleniyor...")

        # --- 💬 CANLI SOHBET ALANI ---
        st.markdown("### 💬 BTA Canlı Sohbet & Analiz Alanı")
        for msj in st.session_state["sohbet_gecmisi"]:
            st.write(f"💬 **{msj['kisi']}:** {msj['metin']}")
            
        with st.form("sohbet_formu_kutusu", clear_on_submit=True):
            kullanici_adi = st.text_input("Adınız / Takma Adınız:", placeholder="Ziyaretçi...", key="sohbet_nick")
            mesaj_metni = st.text_area("Mesajınız veya Hisse Sorunuz:", key="sohbet_text")
            gonder_butonu = st.form_submit_button("Mesaj Gönder 🚀")
            
            if gonder_butonu and mesaj_metni:
