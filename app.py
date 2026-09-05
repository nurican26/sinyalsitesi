import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.1); border: 1px solid #dc2626; padding: 8px; border-radius: 6px; margin-top: 25px; margin-bottom: 10px; color: #fca5a5 !important; font-size: 0.8rem; text-align: justify;} .kilit-uyari {background: rgba(255, 255, 255, 0.05); border-left: 4px solid #ca8a04; padding: 15px; border-radius: 6px; margin-bottom: 20px; font-size: 1.1rem;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .bta-kayan-konteyner {width: 100%; overflow: hidden; margin-top: 25px; margin-bottom: 35px; background: transparent;} .bta-kayan-yazi {display: inline-block; white-space: nowrap; animation: kaydirma 15s linear infinite; font-family: "Brush Script MT", "Comic Sans MS", cursive, sans-serif !important; font-weight: bold; font-size: 5rem; letter-spacing: 5px; background: linear-gradient(45deg, #ff007f, #ff00ff, #8b00ff, #0000ff, #00ffff, #00ff00, #ffff00, #ff7f00, #ff0000); background-size: 400% 400%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 20px rgba(255, 0, 255, 0.6), 0 0 40px rgba(0, 255, 255, 0.4), 4px 4px 10px rgba(0, 0, 0, 0.8); animation: kaydirma 15s linear infinite, gokkusagi 5s ease infinite;} @keyframes kaydirma {0% {transform: translate3d(-100%, 0, 0);} 100% {transform: translate3d(100%, 0, 0);}} @keyframes gokkusagi {0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;}} .chat-kutusu {background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; border: 1px solid #3b82f6; max-height: 300px; overflow-y: auto; margin-bottom: 15px;} .chat-mesaj {padding: 5px 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.95rem;} .chat-zaman {color: #94a3b8; font-size: 0.8rem; margin-right: 10px;} .chat-isim {color: #38bdf8; font-weight: bold; margin-right: 5px;}</style>', unsafe_allow_html=True)

# 🔑 GÜVENLİ ÇİFT ŞİFRE PARAMETRELERİ
ZIYARETCI_SIFRESI = "bta3015"
YONETICI_SIFRESI = "3015"

MESAJ_DOSYASI = "gelen_mesajlar.txt"
DURUM_DOSYASI = "site_durumu.txt"

# 💾 Dosya Kontrolleri
if not os.path.exists(DURUM_DOSYASI):
    with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Açık")

if not os.path.exists(MESAJ_DOSYASI):
    with open(MESAJ_DOSYASI, "w", encoding="utf-8") as f: f.write("")

with open(DURUM_DOSYASI, "r", encoding="utf-8") as f:
    mevcut_kilit = f.read().strip()

# Hafıza Kontrolleri
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

for k in ["kisitli_liste", "ziyaret_sayaci"]:
    if k not in st.session_state: st.session_state[k] = 0 if k == "ziyaret_sayaci" else []

st.session_state["ziyaret_sayaci"] += 102

# 🚀 KAYAN VE PARLAYAN GÖKKUŞAĞI BTA LOGO ALANI
st.markdown('<div class="bta-kayan-konteyner"><div class="bta-kayan-yazi">BTA</div></div>', unsafe_allow_html=True)

# 🔐 GİRİŞ KUTUSU
st.markdown("### 🔐 Erişim Paneli şifre girin enter tuşlayın")
girilen_sifre = st.text_input("Sinyal listesini açmak veya yönetici ayarlarını yönetmek için şifrenizi giriniz:", type="password", placeholder="Şifrenizi yazıp Enter'a basın...")

is_admin = (girilen_sifre == YONETICI_SIFRESI)

if is_admin:
    st.info(f"👑 **Yönetici Girişi Başarılı.** Sitenin Mevcut Durumu: **{mevcut_kilit}**")
    col_ac, col_kilitle = st.columns(2)
    if col_ac.button("🔓 HERKESE AÇ (Şifre Sorma)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Açık")
        st.rerun()
    if col_kilitle.button("🔒 SİTEYİ KİLİTLE (kilile)"):
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f: f.write("Kilitli")
        st.rerun()

erisim_izni = mevcut_kilit == "Açık" or girilen_sifre == ZIYARETCI_SIFRESI or girilen_sifre == YONETICI_SIFRESI

if not erisim_izni:
    st.warning("⚠️ Bu içeriği görebilmek için geçerli bir erişim şifresi girmeniz gerekmektedir.")

# 💥 CANLI FİYAT MOTORU
def hızlı_canli_fiyat_bul(hisse_kodu):
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

# 🟢 ERİŞİM İZNİ VARSA ÇALIŞACAK ALAN
if erisim_izni:
    st.markdown(f'<div style="font-size: 1rem; color: #a5f3fc; margin-bottom: 20px; font-weight: bold;">🚪 Giriş Sayısı: {st.session_state["ziyaret_sayaci"]}</div>', unsafe_allow_html=True)

    # 💬 SOHBET ODASI MODÜLÜ (Ekranı bölmeden üst/alt yerleşime uygun yapıldı)
    st.markdown('### 💬 BTA Canlı Sohbet Odası')
    
    # Mesajları Dosyadan Okuma ve Gösterme
    with open(MESAJ_DOSYASI, "r", encoding="utf-8") as f:
        mesajlar = f.readlines()
    
    chat_html = '<div class="chat-kutusu">'
    if mesajlar:
        for m in mesajlar:
            if " - " in m and ": " in m:
                parca = m.split(" - ", 1)
                zaman = parca[0]
                icerik_parca = parca[1].split(": ", 1)
                isim = icerik_parca[0]
                mesaj_metni = icerik_parca[1]
                chat_html += f'<div class="chat-mesaj"><span class="chat-zaman">[{zaman}]</span><span class="chat-isim">{isim}:</span> <span>{mesaj_metni}</span></div>'
            else:
                chat_html += f'<div class="chat-mesaj"><span>{m}</span></div>'
    else:
        chat_html += '<div style="color: #94a3b8; text-align: center; padding: 10px;">Henüz mesaj yok. İlk mesajı siz yazın!</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)
    
    # Mesaj Gönderme Formu
    with st.form("chat_formu", clear_on_submit=True):
        col_isim, col_mesaj, col_buton = st.columns([2, 7, 2])
        varsayilan_isim = "Yönetici" if is_admin else "Ziyaretçi"
        rumuz = col_isim.text_input("Rumuz:", value=varsayilan_isim, max_chars=15)
        yeni_mesaj = col_mesaj.text_input("Mesajınız:", placeholder="Mesajınızı buraya yazın...")
        gonderildi = col_buton.form_submit_button("Gönder 🚀")
        
        if gonderildi and yeni_mesaj.strip():
            su_an = datetime.datetime.now().strftime("%H:%M:%S")
            with open(MESAJ_DOSYASI, "a", encoding="utf-8") as f:
                f.write(f"{su_an} - {rumuz}: {yeni_mesaj.strip()}\n")
            st.rerun()

    # --- HİSSE SİNYAL TABLOLARI ---
    df_kaynak = None
    excel_yolu = "nurican.xls.xlsm"
    if os.path.exists(excel_yolu):
        try: df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
        except: pass

    tablo_alsat, tablo_al = [], []
    guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")

    if df_kaynak is not None:
        for idx in range(2, len(df_kaynak)):
            try:
                if len(df_kaynak.columns) > 22:
                    uv = str(df_kaynak.iloc[idx, 20]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 20]) else ""
                    wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 22]) else ""
                    t_deg = str(df_kaynak.iloc[idx, 19]).strip() if not pd.isna(df_kaynak.iloc[idx, 19]) else "0"
                    
                    if uv and uv not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                        h_ara = re.findall(r'[A-Z]+', uv)
                        if h_ara:
                            hisse = str(h_ara[0])
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": t_deg, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
                            
                    if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                        h_ara = re.findall(r'[A-Z]+', wv)
                        if h_ara:
                            hisse = str(h_ara[0])
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            if hisse not in st.session_state["ozel_takip_kutusu"] and cfiy > 0:
                                st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                            tablo_al.append({"Hisse Kodu 🚀": hisse, "BTA Puan": t_deg, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
            except: pass

    st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
    if tablo_alsat: st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
    else: st.write("🔒 Aktif AL SAT sinyali taranıyor...")

