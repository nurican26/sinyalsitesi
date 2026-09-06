import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.1); border: 1px solid #dc2626; padding: 8px; border-radius: 6px; margin-top: 25px; margin-bottom: 10px; color: #fca5a5 !important; font-size: 0.8rem; text-align: justify;} .bta-logo-konteyner {display: flex; justify-content: center; align-items: center; margin-top: 25px; margin-bottom: 35px; width: 100%;} .bta-logo {font-family: "Brush Script MT", "Comic Sans MS", cursive, sans-serif !important; font-weight: bold; font-size: 4rem; width: 160px; height: 160px; line-height: 148px; border-radius: 50%; border: 4px solid transparent; background: linear-gradient(#0f172a, #1e1b4b) padding-box, linear-gradient(45deg, #39ff14, #00ffff, #ff007f, #ffff00) border-box; box-shadow: 0 0 10px rgba(57, 255, 20, 0.3), inset 0 0 5px rgba(0, 255, 255, 0.2); background-image: linear-gradient(45deg, #ff007f, #ff00ff, #8b00ff, #0000ff, #00ffff, #00ff00, #ffff00, #ff7f00, #ff0000); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; text-align: center; letter-spacing: 2px; animation: btaHafifYansin 2.5s ease-in-out infinite alternate;} .kilit-uyari {background: rgba(255, 255, 255, 0.05); border-left: 4px solid #ca8a04; padding: 15px; border-radius: 6px; margin-bottom: 20px; font-size: 1.1rem;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} @keyframes btaHafifYansin {0% {filter: drop-shadow(0 0 3px rgba(255, 0, 127, 0.4)); text-shadow: 0 0 6px rgba(255, 0, 127, 0.5);} 50% {filter: drop-shadow(0 0 8px rgba(0, 255, 255, 0.5)); text-shadow: 0 0 12px rgba(0, 255, 255, 0.6);} 100% {filter: drop-shadow(0 0 3px rgba(57, 255, 20, 0.4)); text-shadow: 0 0 6px rgba(57, 255, 20, 0.5);}}</style>', unsafe_allow_html=True)

# 🔑 GÜVENLİ ÇİFT ŞİFRE PARAMETRELERİ
ZIYARETCI_SIFRESI = "bta3015"         # Sadece hisseleri görme yetkisi
YONETICI_SIFRESI = "3015"     # Kilitleyip açma (Yönetici) yetkisi

MESAJ_DOSYASI = "gelen_mesajlar.txt"
DURUM_DOSYASI = "site_durumu.txt"

# 💾 Kalıcı Kilit Durumunu Dosyadan Okuma
if not os.path.exists(DURUM_DOSYASI):
    with open(DURUM_DOSYASI, "w", encoding="utf-8") as f:
        f.write("Açık")

with open(DURUM_DOSYASI, "r", encoding="utf-8") as f:
    mevcut_kilit = f.read().strip()

# Hafıza Kontrolleri
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

for k in ["kisitli_liste", "ziyaret_sayaci"]:
    if k not in st.session_state: st.session_state[k] = 0 if k == "ziyaret_sayaci" else []

# Giriş sayısı her etkileşimde hızlıca yükselmesi için kısıtlama kaldırıldı
st.session_state["ziyaret_sayaci"] += 1

# BTA LOGO ALANI (ORTALANMIŞ, GÖKKUŞAĞI, EL YAZISI, IŞIKLI VE GÖLGELİ)
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# 🔐 GİRİŞ KUTUSU
st.markdown("### 🔐 Erişim Paneli")
girilen_sifre = st.text_input("Sinyal listesini açmak veya yönetici ayarlarını yönetmek için şifrenizi giriniz:", type="password", placeholder="Şifrenizi yazıp Enter'a basın...")

# 🎛️ BAĞIMSIZ YÖNETİCİ ODASI
is_admin = False
if girilen_sifre == YONETICI_SIFRESI:
    is_admin = True

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
erisim_izni = False
if mevcut_kilit == "Açık" or girilen_sifre == ZIYARETCI_SIFRESI or girilen_sifre == YONETICI_SIFRESI:
    erisim_izni = True
else:
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

# 🟢 1. BLOK: ERİŞİM İZNİ VARSA SİTE DETAYLARI VE HİSSELER SORUNSUZ YÜKLENİR
if erisim_izni:
    # Sadece Giriş Sayısı Bırakıldı (Puan, Oy, Tarih/Saat tamamen temizlendi)
    st.markdown(f'<div style="font-size: 1rem; color: #a5f3fc; margin-bottom: 20px; font-weight: bold;">🚪 Giriş Sayısı: {st.session_state["ziyaret_sayaci"]}</div>', unsafe_allow_html=True)

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
                    t_deg = str(df_kaynak.iloc[idx, 19]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 19]) else ""
                    
                    if uv and uv not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                        h_ara = re.findall(r'[A-Z]+', uv)
                        if h_ara:
                            hisse = str(h_ara[0])
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv)
                            bta_puan = p_bul[0] if p_bul else t_deg
                            tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
                            
                    if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                        h_ara = re.findall(r'[A-Z]+', wv)
                        if h_ara:
                            hisse = str(h_ara[0])
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', wv)
                            bta_puan = p_bul[0] if p_bul else t_deg
                            if hisse not in st.session_state["ozel_takip_kutusu"] and cfiy > 0:
                                st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                            tablo_al.append({"Hisse Kodu 🚀": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
            except: pass

    st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
    if tablo_alsat: st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
    else: st.write("🔒 Aktif AL SAT sinyali taranıyor...")

    st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
    if tablo_al: st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
    else: st.write("🔒 Aktif AL sinyali taranıyor...")

# ⚠️ YASAL UYARI (SPK MEVZUATI)
st.markdown('<div class="spk-kutusu"><b>⚠️ YASAL UYARI / SPK BİLGİLENDİRMESİ:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti, yetkili kuruluşlar tarafından kişilerin risk ve getiri tercihleri dikkate alınarak kişiye özel sunulmaktadır. Burada yer alan puanlamalar ve canlı fiyat verileri tamamen algoritmik simülasyon ve veri okuma amaçlı olup, herhangi bir yatırım enstrümanı için doğrudan "AL", "SAT" veya "TUT" tavsiyesi teşkil etmez. Analizlerin doğruluğu garanti edilmemekte olup, verilerde yaşanabilecek gecikme veya eksikliklerden yazılım geliştirici sorumlu tutulamaz.</div>', unsafe_allow_html=True)
