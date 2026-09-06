import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re

# 1. Sayfa Yapılandırması ve Şık Tasarım
st.set_page_config(page_title="Canlı Hisse Takip Programı", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; margin-top: 30px; margin-bottom: 20px; color: #fca5a5 !important; font-size: 0.95rem; text-align: justify; line-height: 1.5;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;}</style>', unsafe_allow_html=True)

# Excel Okuma Motoru (Önbellekli)
@st.cache_data(ttl=30)
def excel_oku(yol):
    if os.path.exists(yol):
        try:
            return pd.read_excel(yol, header=None, engine="openpyxl")
        except:
            return None
    return None

# Web'den (Yahoo Finance) Canlı Veri Çeken Kesin ve Doğru Motor
@st.cache_data(ttl=60)
def webden_canli_veri_topla(hisse_listesi):
    veriler = {}
    if not hisse_listesi:
        return veriler
    try:
        # Borsa istanbul için kodların sonuna .IS ekliyoruz (Örn: THYAO.IS)
        ticker_listesi = [f"{h}.IS" for h in hisse_listesi]
        ticker_string = " ".join(ticker_listesi)
        
        # Web'den canlı indirme emri
        data = yf.download(ticker_string, period="5d", progress=False)
        
        for h in hisse_listesi:
            is_kodu = f"{h}.IS"
            try:
                # Çoklu hisse indirildiğinde oluşan alt kırılımları güvenli şekilde okuma
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
    ham_veriler = []

    # 1. Excel'i tarayıp sadece ham verileri hafızaya topluyoruz
    for idx in range(0, len(df_kaynak)):
        try:
            bta_hisse = ""
            alsat_hisse = ""
            bta_alim = 0.0
            bta_puan = ""

            # Üst Panel Sütun Girişleri (A, C, D)
            if len(df_kaynak.columns) >= 4:
                hisse_raw = str(df_kaynak.iloc[idx, 0]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 0]) else ""
                if hisse_raw and hisse_raw not in ["NAN", "NONE", "HİSSE", "BTA HİSSE", "UCUZ KALANLAR", "ANA", "AL_SAT SİNYALİ"]:
                    h_ara = re.findall(r'[A-Z]+', hisse_raw)
                    if h_ara:
                        bta_hisse = str(h_ara[0])
                        _bta_kodlari.append(bta_hisse)
                
                try: bta_alim = float(str(df_kaynak.iloc[idx, 2]).replace(",", ".")) if not pd.isna(df_kaynak.iloc[idx, 2]) else 0.0
                except: bta_alim = 0.0
                
                bta_puan = str(df_kaynak.iloc[idx, 3]).strip() if not pd.isna(df_kaynak.iloc[idx, 3]) else ""

            # Alt Panel Sütun Girişleri (B)
            if len(df_kaynak.columns) >= 2:
                alsat_raw = str(df_kaynak.iloc[idx, 1]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 1]) else ""
                if alsat_raw and alsat_raw not in ["NAN", "NONE", "HİSSE", "UCUZ KALANLAR", "ANA", "BTA ALIMI"]:
                    as_ara = re.findall(r'[A-Z]+', alsat_raw)
                    if as_ara:
                        alsat_hisse = str(as_ara[0])
                        _alsat_kodlari.append(alsat_hisse)

            ham_veriler.append({
                "bta_hisse": bta_hisse, "bta_alim": bta_alim, "bta_puan": bta_puan, "alsat_hisse": alsat_hisse
            })
        except:
            pass

    # 2. Web'den İnternet Canlı Bilgilerini Tek Seferde Doğru Çekiyoruz
    tum_kodlar = list(set([k for k in (_bta_kodlari + _alsat_kodlari) if k]))
    canli_havuz = webden_canli_veri_topla(tum_kodlar)

    # 3. Tabloların Eşleştirilmesi
    tablo_bta = []
    tablo_alsat = []

    for item in ham_veriler:
        # Üst Tablo Birleştirme
        if item["bta_hisse"]:
            h = item["bta_hisse"]
            c_fiyat = canli_havuz.get(h, {}).get("fiyat", 0.0)
            
            kz_oran_str = "-"
            if item["bta_alim"] > 0 and c_fiyat > 0:
                kz = ((c_fiyat - item["bta_alim"]) / item["bta_alim"]) * 100
                kz_oran_str = f"%{kz:+.2f}"

            tablo_bta.append({
                "BTA PUAN 🔢": item["bta_puan"],
                "BTA HİSSE 📈": h,
                "BTA ALIM 📥": f"{item['bta_alim']:.2f} TL" if item["bta_alim"] > 0 else "-",
                "GÜNCEL FİYAT 💥": f"{c_fiyat:.2f} TL" if c_fiyat > 0 else "Hatalı Kod/Veri Yok",
                "KAR / ZARAR 📊": kz_oran_str
            })

        # Alt Tablo Birleştirme
        if item["alsat_hisse"]:
            h_as = item["alsat_hisse"]
            c_fiyat_as = canli_havuz.get(h_as, {}).get("fiyat", 0.0)
            c_degisim_as = canli_havuz.get(h_as, {}).get("degisim", 0.0)

            tablo_alsat.append({
                "GÜNLÜK AL SAT HİSSELERİ ⚡": h_as,
                "ANLIK VERİ CANLI 📊": f"{c_fiyat_as:.2f} TL" if c_fiyat_as > 0 else "Hatalı Kod/Veri Yok",
                "YÜKSELİŞ ORANI 📈": f"%{c_degisim_as:+.2f}" if c_fiyat_as > 0 else "-"
            })

    # 🟢 WEBPAGE EKRAN ÇIKTILARI
    st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
    if tablo_bta:
        st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)
    else:
        st.info("Excel'deki A, C ve D sütunlarında veri bulunamadı.")

    st.write("")

    st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
    if tablo_alsat:
        st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
    else:
        st.info("Excel'deki B sütununda veri bulunamadı.")

else:
    st.error("Excel dosyası bulunamadı! 'nurican.xls.xlsm' dosyasının doğru klasörde olduğundan emin olun.")

st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir.</div>', unsafe_allow_html=True)
