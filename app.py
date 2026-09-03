import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} 
    h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: 'Segoe UI', sans-serif;} 
    input {color: #000!important; background-color: #fff!important;}
    
    .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}
    div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;}
    
    .alsat-baslik {
        background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%);
        padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;
    }
    .al-baslik {
        background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%);
        padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;
    }
    .spk-kutusu {
        background-color: rgba(220, 38, 38, 0.1);
        border: 1px solid #dc2626; padding: 8px;
        border-radius: 6px; margin-top: 15px; margin-bottom: 10px;
        color: #fca5a5 !important; font-size: 0.8rem; text-align: justify;
    }
    
    /* 🟢 BÜYÜK HARFLİ YEŞİL BTA LOGOSU */
    .bta-logo-konteyner {
        display: flex;
        align-items: center;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .bta-logo {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white !important;
        font-family: 'Segoe UI', sans-serif !important;
        font-weight: bold;
        font-size: 2.2rem;
        padding: 4px 25px;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
    }
    
    /* Kilitli ekran uyarı kutusu */
    .kilit-uyari {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #ca8a04;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 20px;
        font-size: 1.1rem;
    }
    
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        font-size: 1.25rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# 🔑 SABİT PARAMETRELER
GIRIS_SIFRESI = "bta2026"
MESAJ_DOSYASI = "gelen_mesajlar.txt"

# Hafıza Kontrolleri
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

for k in ["kisitli_liste", "ziyaret_sayaci", "topham_oy_sayisi", "topham_yildiz_puani"]:
    if k not in st.session_state: st.session_state[k] = 0 if "sayaci" in k or "sayisi" in k or "puani" in k else []

st.session_state["ziyaret_sayaci"] += 1

# BTA LOGO ALANI
st.markdown("""
<div class="bta-logo-konteyner">
    <div class="bta-logo">BTA</div>
</div>
""", unsafe_allow_html=True)

# 🛠️ PANEL MODU SEÇİMİ (AÇ-KAPA ANAHTARI)
st.sidebar.markdown("### ⚙️ Yönetici Ayarları")
panel_modu = st.sidebar.selectbox("Panel Durumu Seçin:", ["Site Herkese Açık", "Site Şifreli / Kilitli"])

# İçerik gösterilme şartı kontrolü
erisim_izni = False
if panel_modu == "Site Herkese Açık":
    erisim_izni = True
else:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔐 Erişim Girişi")
    girilen_sifre = st.sidebar.text_input("Giriş Şifresini Yazın:", type="password", placeholder="Şifre...")
    if girilen_sifre == GIRIS_SIFRESI:
        erisim_izni = True

# 🟢 ERİŞİM İZNİ VARSA SİTE YÜKLENİR
if erisim_izni:
    guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
    st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px;">⭐ <b>Puan:</b> {puan:.2f} | 🔥 <b>Oy:</b> {st.session_state["topham_oy_sayisi"]} | 🚪 <b>Giriş:</b> {st.session_state["ziyaret_sayaci"]} | 🕒 {guncel_an}</div>', unsafe_allow_html=True)

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
        if hisse_kodu in st.session_state["fiyat_hafizasi"]:
            saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
            if time.time() - saved_time < 300: 
                return saved_price
        try:
            ticker = yf.Ticker(f"{hisse_kodu}.IS")
            data = ticker.history(period="1d")
            if not data.empty and not pd.isna(data['Close'].iloc[-1]):
                fiyat = float(data['Close'].iloc[-1])
                st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
                return fiyat
        except:
            pass
        return 0.0

    def temiz_metin_al(val):
        if pd.isna(val): return ""
        return str(val).strip().upper()

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
                            hisse = hisse_ara
                            canli_fiyat = hızlı_canli_fiyat_bul(hisse)
                            puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                            bta_puan = puan_bul if puan_bul else (t_degeri if t_degeri else uv_degeri)
                            tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."})
                    
                    if wv_degeri and wv_degeri not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                        hisse_ara = re.findall(r'[A-Z]+', wv_degeri)
                        if hisse_ara:
                            hisse = hisse_ara
                            canli_fiyat = hızlı_canli_fiyat_bul(hisse)
                            puan_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv_degeri)
                            bta_puan = puan_bul if puan_bul else (t_degeri if t_degeri else uv_degeri)
                            if hisse not in st.session_state["ozel_takip_kutusu"] and canli_fiyat > 0:
                                st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": guncel_an}
                            tablo_al.append({"Hisse Kodu 🚀": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor..."})
            except:
                pass

    st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
    if tablo_alsat: st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
    else: st.write("🔒 Aktif AL SAT sinyali taranıyor...")

    st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
    if tablo_al: st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
    else: st.write("🔒 Aktif BTA sinyali taranıyor...")

    if st.session_state["ozel_takip_kutusu"]:
        st.markdown("#### 🌟 Özel Takip Havuzu 💰")
        tk_list = []
        for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
            cfiy = hızlı_canli_fiyat_bul(hisse)
            if cfiy == 0.0: cfiy = bilge["kayit_fiyati"]
            tk_list.append({"Hisse Kodu 🗝️": hisse, "Havuz Maliyeti": f"{bilge['kayit_fiyati']:.2f} TL", "Anlık Güncel": f"{cfiy:.2f} TL"})
        if tk_list:
            st.dataframe(pd.DataFrame(tk_list), use_container_width=True, hide_index=True)
            if st.button("🗑️ Havuzu Temizle", use_container_width=True):
                st.session_state["ozel_takip_kutusu"] = {}
                st.rerun()

    # ⭐ TOPLULUK PUANLAMA SİSTEMİ
    st.write("---")
    st.subheader("⭐ Paneli Değerlendir")
    yildiz_secimi = st.feedback("stars") 
    if yildiz_secimi is not None:
        st.session_state["topham_oy_sayisi"] += 1
        st.session_state["topham_yildiz_puani"] += (yildiz_secimi + 1)
        st.success("Oyunuz kaydedildi!")
        time.sleep(1)
        st.rerun()

    # 📬 GIZLI GELEN MESAJLAR PANELİ
    if panel_modu == "Site Şifreli / Kilitli":
        st.write("---")
        st.subheader("📩 Gelen Kullanıcı Mesajları")
        if os.path.exists(MESAJ_DOSYASI):
            with open(MESAJ_DOSYASI, "r", encoding="utf-8") as f:
                mesajlar = f.readlines()
            if mesajlar:
                for m in reversed(mesajlar[-15:]): 
                    st.text(f"💬 {m.strip()}")
                st.write("")
                if st.button("🗑️ Tüm Mesajları Temizle"):
                    os.remove(MESAJ_DOSYASI)
                    st.rerun()
            else:
                st.info("Henüz yeni mesaj bulunmuyor.")
        else:
            st.info("Henüz yeni mesaj bulunmuyor.")

else:
    # 🔒 MOD "KİLİTLİ" SEÇİLDİYSE VE ŞİFRE YAZILMADIYSA GÖRÜNECEK EKRAN
    st.markdown("""
    <div class="kilit-uyari">
        ⚠️ <b>Hisseler ve Canlı Sinyaller Gizlenmiştir.</b><br>
        Güncel listeyi ve analiz raporlarını görmek için lütfen sol menüden şifrenizi giriniz.<br><br>
