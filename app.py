import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="Hisse Takip Sinyal Programı", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; margin-top: 30px; margin-bottom: 20px; color: #fca5a5 !important; font-size: 0.95rem; text-align: justify; line-height: 1.5;} .bta-logo-konteyner {display: flex; align-items: center; margin-top: 15px; margin-bottom: 25px;} .bta-logo {background: transparent !important; color: #10b981 !important; font-family: "Segoe UI", sans-serif !important; font-weight: bold; font-size: 4rem; padding: 0px; text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9), 0 0 20px rgba(16, 185, 129, 0.6); box-shadow: none !important;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.05); border: 1px solid #eab308; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;}</style>', unsafe_allow_html=True)

# Hafıza Sabitleme
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

# LOGO
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# 💥 CANLI FİYAT VE ORAN MOTORU
def canli_veri_ve_degisim_bul(hisse_kodu):
    hisse_kodu = str(hisse_kodu).strip().upper()
    if not hisse_kodu or hisse_kodu in ["NAN", "NONE", ""]: return 0.0, 0.0
    
    h_ara = re.findall(r'[A-Z]+', hisse_kodu)
    if not h_ara: return 0.0, 0.0
    temiz_kod = h_ara[0]

    # Hafıza kontrolü (5 dakika geçerli)
    if temiz_kod in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price, saved_change = st.session_state["fiyat_hafizasi"][temiz_kod]
        if time.time() - saved_time < 300: return saved_price, saved_change
    try:
        ticker = yf.Ticker(f"{temiz_kod}.IS")
        data = ticker.history(period="2d") # Günlük değişim için 2 günlük veri çekiyoruz
        if not data.empty and len(data) >= 1:
            fiyat = float(data['Close'].iloc[-1])
            
            # Günlük Yükseliş Oranı Hesaplama
            if 'Regular Market Change Percent' in ticker.info:
                degisim = float(ticker.info['Regular Market Change Percent'])
            elif len(data) >= 2:
                onceki_kapanis = float(data['Close'].iloc[-2])
                degisim = ((fiyat - onceki_kapanis) / onceki_kapanis) * 100
            else:
                degisim = 0.0
                
            st.session_state["fiyat_hafizasi"][temiz_kod] = (time.time(), fiyat, degisim)
            return fiyat, degisim
    except: pass
    return 0.0, 0.0

# Zaman Göstergesi
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px;">🕒 {guncel_an}</div>', unsafe_allow_html=True)

# 🔍 ARKA PLANDA EXCEL VERİSİNİ OKUMA
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"

if os.path.exists(excel_yolu):
    try: 
        df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except Exception as e:
        st.error(f"Excel dosyası okunurken hata oluştu: {e}")

tablo_bta_hisseleri = []
tablo_gunluk_alsat = []

if df_kaynak is not None:
    for idx in range(0, len(df_kaynak)):
        try:
            # -------------------------------------------------------------
            # 1. ÜST PANEL: BTA HİSSELERİ (A, C, D Sütunları)
            # A Sütunu (İndeks 0) -> BTA HİSSE
            # C Sütunu (İndeks 2) -> BTA ALIM
            # D Sütunu (İndeks 3) -> BTA PUAN
            # -------------------------------------------------------------
            if len(df_kaynak.columns) >= 4:
                bta_hisse_raw = str(df_kaynak.iloc[idx, 0]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 0]) else ""
                bta_alim_raw = str(df_kaynak.iloc[idx, 2]).strip() if not pd.isna(df_kaynak.iloc[idx, 2]) else ""
                bta_puan_raw = str(df_kaynak.iloc[idx, 3]).strip() if not pd.isna(df_kaynak.iloc[idx, 3]) else ""

                # Filtreleme: "UCUZ KALANLAR", "ANA" gibi temizlenecek kelimeleri eliyoruz
                if bta_hisse_raw and bta_hisse_raw not in ["NAN", "NONE", "HİSSE", "BTA HİSSE", "UCUZ KALANLAR", "ANA", "AL_SAT SİNYALİ"]:
                    hisse_kodlari = re.findall(r'[A-Z]+', bta_hisse_raw)
                    if hisse_kodlari:
                        hisse = hisse_kodlari[0]
                        
                        # İnternetten Canlı Veri Çekme
                        anlik_fiyat, _ = canli_veri_ve_degisim_bul(hisse)
                        
                        # Kar/Zarar Oranı Hesaplama
                        try:
                            maliyet = float(str(bta_alim_raw).replace(",", "."))
                        except:
                            maliyet = 0.0
                            
                        kz_oran_str = "-"
                        if maliyet > 0 and anlik_fiyat > 0:
                            kz_oran = ((anlik_fiyat - maliyet) / maliyet) * 100
                            kz_oran_str = f"%{kz_oran:+.2f}"
                        
                        tablo_bta_hisseleri.append({
                            "BTA PUAN 🔢": bta_puan_raw,
                            "BTA HİSSE 📈": hisse,
                            "BTA ALIM 📥": f"{maliyet:.2f} TL" if maliyet > 0 else bta_alim_raw,
                            "GÜNCEL FİYAT 💥": f"{anlik_fiyat:.2f} TL" if anlik_fiyat > 0 else "Yükleniyor...",
                            "KAR / ZARAR 📊": kz_oran_str
                        })

            # -------------------------------------------------------------
            # 2. ALT PANEL: GÜNLÜK AL SAT HİSSELERİ (B Sütunu)
            # B Sütunu (İndeks 1) -> GÜNLÜK AL SAT HİSSELERİ
            # -------------------------------------------------------------
            if len(df_kaynak.columns) >= 2:
                alsat_hisse_raw = str(df_kaynak.iloc[idx, 1]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 1]) else ""
                
                if alsat_hisse_raw and alsat_hisse_raw not in ["NAN", "NONE", "HİSSE", "UCUZ KALANLAR", "ANA", "BTA ALIMI"]:
                    alsat_kodlari = re.findall(r'[A-Z]+', alsat_hisse_raw)
                    if alsat_kodlari:
                        as_hisse = alsat_kodlari[0]
                        as_anlik_fiyat, as_degisim = canli_veri_ve_degisim_bul(as_hisse)
                        
                        tablo_gunluk_alsat.append({
                            "GÜNLÜK BTA AL SAT ⚡": as_hisse,
                            "ANLIK VERİ CANLI 📊": f"{as_anlik_fiyat:.2f} TL" if as_anlik_fiyat > 0 else "Yükleniyor...",
                            "YÜKSELİŞ ORANI 📈": f"%{as_degisim:+.2f}" if as_anlik_fiyat > 0 else "..."
                        })
        except:
            pass

# 🟢 EKRANA YAZDIRMA ALANI

# 1. ÜST KISIM TABLOSU: BTA HİSSELERİ
st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
if tablo_bta_hisseleri:
    df_bta = pd.DataFrame(tablo_bta_hisseleri)
    st.dataframe(df_bta, use_container_width=True, hide_index=True)
else:
    st.info("Excel dosyanızda uygun formatta BTA hisse verisi (A, C, D sütunları) taranıyor...")

st.write("")

# 2. ALT KISIM TABLOSU: GÜNLÜK AL SAT HİSSELERİ
st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
if tablo_gunluk_alsat:
    df_alsat = pd.DataFrame(tablo_gunluk_alsat)
    st.dataframe(df_alsat, use_container_width=True, hide_index=True)
else:
    st.info("Excel dosyanızın B sütununda günlük al-sat verisi taranıyor...")

# ⚠️ SPK UYARI KUTUSU
st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir.</div>', unsafe_allow_html=True)
