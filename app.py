import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re

# 1. Sayfa Yapılandırması ve Şık Tasarım
st.set_page_config(page_title="Canlı Hisse Takip Programı", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; margin-top: 30px; margin-bottom: 20px; color: #fca5a5 !important; font-size: 0.95rem; text-align: justify; line-height: 1.5;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;}</style>', unsafe_allow_html=True)

# Excel "BTA" Sekmesini Okuma Motoru (Önbellekli)
@st.cache_data(ttl=15)
def excel_oku(yol):
    if os.path.exists(yol):
        try:
            # Excel'deki kırmızı logolu "BTA" sekmesini doğrudan hedef alıyoruz
            return pd.read_excel(yol, sheet_name="BTA", header=0, engine="openpyxl")
        except:
            return None
    return None

# Web'den (Yahoo Finance) Canlı Veri Çeken Motor
@st.cache_data(ttl=30)
def webden_canli_veri_topla(hisse_listesi):
    veriler = {}
    if not hisse_listesi:
        return veriler
    try:
        ticker_listesi = [f"{h}.IS" for h in hisse_listesi]
        ticker_string = " ".join(ticker_listesi)
        
        data = yf.download(ticker_string, period="5d", progress=False)
        
        for h in hisse_listesi:
            is_kodu = f"{h}.IS"
            try:
                if len(hisse_listesi) > 1:
                    son_fiyat = float(data['Close'][is_kodu].dropna().iloc[-1])
                    onceki_fiyat = float(data['Close'][is_kodu].dropna().iloc[-2])
                else:
                    son_fiyat = float(data['Close'].dropna().iloc[-1])
                    onceki_fiyat = float(data['Close'].dropna().iloc[-2])
                
                degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
                veriler[h] = {"fiyat": son_fiyat, "degisim": degisim}
            except:
                veriler[h] = {"fiyat": 0.0, "degisim": 0.0}
    except:
        pass
    return veriler

# Zaman Göstergesi
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div style="font-size: 1.1rem; color: #cbd5e1; margin-bottom: 15px; font-weight: bold;">🕒 Canlı Veri Saati: {guncel_an}</div>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"
df_kaynak = excel_oku(excel_yolu)

if df_kaynak is not None:
    _bta_kodlari = []
    _alsat_kodlari = []
    
    tablo_bta_ham = []
    tablo_alsat_ham = []

    # Excel satırlarını tek tek tarama (E SÜTUNUNA ASLA BAKILMAZ)
    for idx in range(len(df_kaynak)):
        try:
            # 1. ÜST PANEL VERİLERİ (A, C, D Sütunları)
            # Sütun İndeksleri: 0=BTA HİSSE, 2=BTA ALIM FİYATI, 3=BTA PUANI
            bta_hisse_raw = str(df_kaynak.iloc[idx, 0]).strip().upper() if pd.notna(df_kaynak.iloc[idx, 0]) else ""
            bta_alim_raw = str(df_kaynak.iloc[idx, 2]).strip() if pd.notna(df_kaynak.iloc[idx, 2]) else ""
            bta_puan_raw = str(df_kaynak.iloc[idx, 3]).strip() if pd.notna(df_kaynak.iloc[idx, 3]) else ""

            if bta_hisse_raw and bta_hisse_raw not in ["NAN", "NONE", "BTA HİSSE", "HİSSE"]:
                h_ara = re.findall(r'[A-Z]+', bta_hisse_raw)
                if h_ara:
                    temiz_bta_kod = str(h_ara[0]).strip()
                    _bta_kodlari.append(temiz_bta_kod)
                    
                    try: maliyet = float(bta_alim_raw.replace(",", "."))
                    except: maliyet = 0.0
                    
                    tablo_bta_ham.append({
                        "puan": bta_puan_raw, "hisse": temiz_bta_kod, "maliyet": maliyet
                    })

            # 2. ALT PANEL VERİLERİ (B Sütunu)
            # Sütun İndeksleri: 1=BTA AL SAT
            alsat_raw = str(df_kaynak.iloc[idx, 1]).strip().upper() if pd.notna(df_kaynak.iloc[idx, 1]) else ""
            if alsat_raw and alsat_raw not in ["NAN", "NONE", "BTA AL SAT"]:
                as_ara = re.findall(r'[A-Z]+', alsat_raw)
                if as_ara:
                    temiz_alsat_kod = str(as_ara[0]).strip()
                    _alsat_kodlari.append(temiz_alsat_kod)
                    tablo_alsat_ham.append({"hisse": temiz_alsat_kod})
        except:
            pass

    # Web'den Canlı Fiyat Havuzunu Doldurma
    tum_kodlar = list(set(_bta_kodlari + _alsat_kodlari))
    canli_havuz = webden_canli_veri_topla(tum_kodlar)

    # Tablo Listelerini Son Biçimine Getirme
    tablo_bta_final = []
    tablo_alsat_final = []

    # Üst Tablo Eşleme
    for item in tablo_bta_ham:
        c_fiyat = canli_havuz.get(item["hisse"], {}).get("fiyat", 0.0)
        
        kz_oran_str = "-"
        if item["maliyet"] > 0 and c_fiyat > 0:
            kz = ((c_fiyat - item["maliyet"]) / item["maliyet"]) * 100
            kz_oran_str = f"%{kz:+.2f}"

        tablo_bta_final.append({
            "BTA PUAN 🔢": item["puan"],
            "BTA HİSSE 📈": item["hisse"],
            "BTA ALIM 📥": f"{item['maliyet']:.2f} TL" if item["maliyet"] > 0 else "-",
            "GÜNCEL FİYAT 💥": f"{c_fiyat:.2f} TL" if c_fiyat > 0 else "Yükleniyor...",
            "KAR / ZARAR 📊": kz_oran_str
        })

    # Alt Tablo Eşleme
    for item in tablo_alsat_ham:
        c_fiyat_as = canli_havuz.get(item["hisse"], {}).get("fiyat", 0.0)
        c_degisim_as = canli_havuz.get(item["hisse"], {}).get("degisim", 0.0)

        tablo_alsat_final.append({
            "GÜNLÜK AL SAT HİSSELERİ ⚡": item["hisse"],
            "ANLIK VERİ CANLI 📊": f"{c_fiyat_as:.2f} TL" if c_fiyat_as > 0 else "Yükleniyor...",
            "YÜKSELİŞ ORANI 📈": f"%{c_degisim_as:+.2f}" if c_fiyat_as > 0 else "-"
        })

    # 🟢 EKRANA YAZDIRMA PANELİ
    st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
    if tablo_bta_final:
        st.dataframe(pd.DataFrame(tablo_bta_final), use_container_width=True, hide_index=True)
    else:
        st.info("BTA sekmesindeki Üst Panel verileri taranıyor...")

    st.write("")

    st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
    if tablo_alsat_final:
        st.dataframe(pd.DataFrame(tablo_alsat_final), use_container_width=True, hide_index=True)
    else:
        st.info("BTA sekmesindeki Alt Panel verileri taranıyor...")

else:
    st.error("Excel dosyasındaki 'BTA' sekmesi okunamadı. Lütfen sekme adını kontrol edin.")

st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir.</div>', unsafe_allow_html=True)
