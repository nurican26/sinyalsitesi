import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.1); border: 1px solid #dc2626; padding: 8px; border-radius: 6px; margin-top: 25px; margin-bottom: 10px; color: #fca5a5 !important; font-size: 0.8rem; text-align: justify;} .bta-logo-konteyner {display: flex; align-items: center; margin-top: 15px; margin-bottom: 25px;} .bta-logo {background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white !important; font-family: "Segoe UI", sans-serif !important; font-weight: bold; font-size: 2.2rem; padding: 4px 25px; border-radius: 12px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);} .kilit-uyari {background: rgba(255, 255, 255, 0.05); border-left: 4px solid #ca8a04; padding: 15px; border-radius: 6px; margin-bottom: 20px; font-size: 1.1rem;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.05); border: 1px solid #3b82f6; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;}</style>', unsafe_allow_html=True)

# 🔑 GÜVENLİ ÇİFT ŞİFRE PARAMETRELERİ
ZIYARETCI_SIFRESI = "bta2026"         # Sadece hisseleri görme yetkisi
YONETICI_SIFRESI = "adminBTA2026"     # Kilitleyip açma (Yönetici) yetkisi

MESAJ_DOSYASI = "gelen_mesajlar.txt"
DURUM_DOSYASI = "site_durumu.txt"

# 💾 Kalıcı Kilit Durumunu Dosyadan Okuma
if not os.path.exists(DURUM_DOSYASI):
    with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Açık")

with open(DURUM_DOSYASI, "r", encoding="utf-8") as f: mevcut_kilit = f.read().strip()

# Hafıza Kontrolleri
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

for k in ["kisitli_liste", "ziyaret_sayaci", "topham_oy_sayisi", "topham_yildiz_puani"]:
    if k not in st.session_state: st.session_state[k] = 0 if "sayaci" in k or "sayisi" in k or "puani" in k else []

st.session_state["ziyaret_sayaci"] += 1

# BTA LOGO ALANI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# 🔐 GİRİŞ KUTUSU
st.markdown("### 🔐 Erişim Paneli")
girilen_sifre = st.text_input("Sinyal listesini açmak veya yönetici ayarlarını yönetmek için şifrenizi giriniz:", type="password", placeholder="Şifrenizi yazıp Enter'a basın...")

# Yönetici yetki kontrolü
is_admin = girilen_sifre == YONETICI_SIFRESI

# 🎛️ YÖNETİCİ ODASI PANELİ
if is_admin:
    st.info(f"👑 **Yönetici Girişi Başarılı.** Sitenin Mevcut Durumu: **{mevcut_kilit}**")
    col_ac, col_kilitle = st.columns(2)
    if col_ac.button("🔓 HERKESE AÇ (Şifre Sorma)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Açık")
        st.rerun()
    if col_kilitle.button("🔒 SİTEYİ KİLİTLE (Herkes Şifre Girsin)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Kilitli")
        st.rerun()

# 🛠️ ERİŞİM KONTROL MANTIĞI
erisim_izni = mevcut_kilit == "Açık" or girilen_sifre == ZIYARETCI_SIFRESI or is_admin

# 💥 CANLI HİSSE VE PİYASA MOTORLARI
def hızlı_canli_fiyat_bul(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - saved_time < 300: return saved_price
    try:
        temiz_kod = str(hisse_kodu).replace("['", "").replace("']", "").replace("[\"", "").replace("\"]", "").strip()
        ticker = yf.Ticker(f"{temiz_kod}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            fiyat = float(data['Close'].iloc[-1])
            st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
            return fiyat
    except: pass
    return 0.0

def doviz_altin_cek(ticker_kod):
    try:
        data = yf.Ticker(ticker_kod).history(period="1d")
        if not data.empty: return float(data['Close'].iloc[-1])
    except: pass
    return 0.0

# 🟢 1. BLOK: ERİŞİM İZNİ VARSA SİTE DETAYLARI VE HİSSELER SORUNSUZ YÜKLENİR
if erisim_izni:
    guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0
    st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px;">⭐ <b>Puan:</b> {puan:.2f} | 🔥 <b>Oy:</b> {st.session_state["topham_oy_sayisi"]} | 🚪 <b>Giriş:</b> {st.session_state["ziyaret_sayaci"]} | 🕒 {guncel_an}</div>', unsafe_allow_html=True)

    # 📊 CANLI DÖVİZ VE ALTIN PANELDEN GÖRÜNÜM (Yeni Eklenen Alan)
    st.markdown("#### 🌍 Canlı Makro Piyasalar")
    p_usd = doviz_altin_cek("USDTRY=X")
    p_eur = doviz_altin_cek("EURTRY=X")
    p_ons = doviz_altin_cek("GC=F")
    p_gram = (p_ons / 31.10347) * p_usd if p_ons > 0 and p_usd > 0 else 0.0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="piyasa-kutusu">💵 DOLAR (USD/TRY)<br><span style="color:#10b981; font-size:1.4rem;">{p_usd:.2f} TL</span></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="piyasa-kutusu">💶 EURO (EUR/TRY)<br><span style="color:#10b981; font-size:1.4rem;">{p_eur:.2f} TL</span></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="piyasa-kutusu">🟡 GRAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_gram:.2f} TL</span></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="piyasa-kutusu">🔱 ONS ALTIN<br><span style="color:#ca8a04; font-size:1.4rem;">{p_ons:.1f} $</span></div>', unsafe_allow_html=True)
    st.write("")

    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except: pass

    tablo_alsat, tablo_al = [], []
    if df_kaynak is not None:
        for idx in range(2, len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 22:
                    uv = str(df_kaynak.iloc[idx, 20]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 20]) else ""
                    wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 22]) else ""
                    t_deg = str(df_kaynak.iloc[idx, 19]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 19]) else ""
                    
                    if uv and uv not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                        h_ara = re.findall(r'[A-Z]+', uv)
                        if h_ara:
                            hisse = str(h_ara)
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv)
                            bta_puan = p_bul if p_bul else t_deg
                            tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
                            
                    if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                        h_ara = re.findall(r'[A-Z]+', wv)
                        if h_ara:
                            hisse = str(h_ara)
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv)
                            bta_puan = p_bul if p_bul else t_deg
                            if hisse not in st.session_state["ozel_takip_kutusu"] and cfiy > 0:
                                st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                            tablo_al.append({"Hisse Kodu 🚀": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
            except: pass

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
