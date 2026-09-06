import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="Canlı Hisse Takip Programı", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; margin-top: 30px; margin-bottom: 20px; color: #fca5a5 !important; font-size: 0.95rem; text-align: justify; line-height: 1.5;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;}</style>', unsafe_allow_html=True)

# Excel "BTA" Sekmesini Olduğu Gibi Okuyan Motor
@st.cache_data(ttl=5)
def excel_oku(yol):
    if os.path.exists(yol):
        try:
            # Doğrudan "BTA" sayfasını, başlıkları (A, B, C, D) sıfırlamadan düz okur
            return pd.read_excel(yol, sheet_name="BTA", engine="openpyxl")
        except:
            return None
    return None

# Yahoo Finance Canlı Veri Motoru
@st.cache_data(ttl=15)
def tekli_canli_fiyat_bul(hisse_kodu):
    hisse_kodu = str(hisse_kodu).strip().upper()
    if not hisse_kodu or hisse_kodu in ["NAN", "NONE", "BTA HİSSE", "BTA AL SAT", "HİSSE"]: 
        return 0.0, 0.0
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="2d")
        if not data.empty and len(data) >= 1:
            son_fiyat = float(data['Close'].iloc[-1])
            onceki_fiyat = float(data['Close'].iloc[-2]) if len(data) >= 2 else son_fiyat
            degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
            return son_fiyat, degisim
    except:
        pass
    return 0.0, 0.0

# Zaman Göstergesi
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div style="font-size: 1.1rem; color: #cbd5e1; margin-bottom: 15px; font-weight: bold;">🕒 Güncel Canlı Saat: {guncel_an}</div>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"
df = excel_oku(excel_yolu)

if df is not None:
    tablo_bta = []
    tablo_alsat = []

    # Excel'in her satırını sırayla, doğrudan okuyoruz
    for idx in range(len(df)):
        try:
            # 1. ÜST PANEL (A, C, D Sütunları)
            hisse_a = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = str(df.iloc[idx, 3]).strip() if pd.notna(df.iloc[idx, 3]) else ""

            # Eğer A sütunundaki hücre boş değilse ve başlık kelimesi içermiyorsa ekle
            if hisse_a and hisse_a not in ["BTA HİSSE", "HİSSE", "NAN", "NONE"]:
                canli_fiyat, _ = tekli_canli_fiyat_bul(hisse_a)
                
                try: maliyet = float(alim_c.replace(",", "."))
                except: maliyet = 0.0
                
                kz_oran_str = "-"
                if maliyet > 0 and canli_fiyat > 0:
                    kz = ((canli_fiyat - maliyet) / maliyet) * 100
                    kz_oran_str = f"%{kz:+.2f}"

                tablo_bta.append({
                    "BTA PUAN 🔢": puan_d,
                    "BTA HİSSE 📈": hisse_a,
                    "BTA ALIM 📥": f"{maliyet:.2f} TL" if maliyet > 0 else alim_c,
                    "GÜNCEL FİYAT 💥": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor...",
                    "KAR / ZARAR 📊": kz_oran_str
                })

            # 2. ALT PANEL (B Sütunu)
            alsat_b = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
            
            # Eğer B sütunundaki hücre boş değilse ve başlık kelimesi içermiyorsa ekle
            if alsat_b and alsat_b not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
                as_canli_fiyat, as_degisim = tekli_canli_fiyat_bul(alsat_b)
                
                tablo_alsat.append({
                    "GÜNLÜK AL SAT HİSSELERİ ⚡": alsat_b,
                    "ANLIK VERİ CANLI 📊": f"{as_canli_fiyat:.2f} TL" if as_canli_fiyat > 0 else "Yükleniyor...",
                    "YÜKSELİŞ ORANI 📈": f"%{as_degisim:+.2f}" if as_canli_fiyat > 0 else "-"
                })
        except:
            pass

    # 🟢 EKRANA BASMA BÖLÜMÜ
    st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
    if tablo_bta:
        st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)
    else:
        st.info("Üst panel için Excel'de veri bulunamadı.")

    st.write("")

    st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
    if tablo_alsat:
        st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
    else:
        st.info("Alt panel için Excel'de veri bulunamadı.")

else:
    st.error("Excel dosyasındaki 'BTA' sayfası okunamadı.")

st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir.</div>', unsafe_allow_html=True)
