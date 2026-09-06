import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA Hisse Takip Sinyal Programı", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; margin-top: 30px; margin-bottom: 20px; color: #fca5a5 !important; font-size: 0.95rem; text-align: justify; line-height: 1.5;} .bta-logo-konteyner {display: flex; align-items: center; margin-top: 15px; margin-bottom: 25px;} .bta-logo {background: transparent !important; color: #10b981 !important; font-family: "Segoe UI", sans-serif !important; font-weight: bold; font-size: 4rem; padding: 0px; text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9), 0 0 20px rgba(16, 185, 129, 0.6); box-shadow: none !important;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.05); border: 1px solid #eab308; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;}</style>', unsafe_allow_html=True)

# Hafıza Sabitleme
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

# LOGO
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

# 💥 CANLI FİYAT MOTORU
def hızlı_canli_fiyat_bul(hisse_kodu):
    hisse_kodu = str(hisse_kodu).strip().upper()
    if not hisse_kodu or hisse_kodu in ["NAN", "NONE", ""]: return 0.0
    
    # Sadece harflerden oluşan borsa kodunu temizle (Örn: "ALCAR" temizleme)
    h_ara = re.findall(r'[A-Z]+', hisse_kodu)
    if not h_ara: return 0.0
    temiz_kod = h_ara[0]

    if temiz_kod in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price = st.session_state["fiyat_hafizasi"][temiz_kod]
        if time.time() - saved_time < 300: return saved_price
    try:
        ticker = yf.Ticker(f"{temiz_kod}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            fiyat = float(data['Close'].iloc[-1])
            st.session_state["fiyat_hafizasi"][temiz_kod] = (time.time(), fiyat)
            return fiyat
    except: pass
    return 0.0

def canli_altin_fiyatlarini_hesapla():
    try:
        ons_ticker = yf.Ticker("GC=F").history(period="5d")
        usd_ticker = yf.Ticker("USDTRY=X").history(period="5d")
        if not ons_ticker.empty and not usd_ticker.empty:
            ons_fiyat = float(ons_ticker['Close'].iloc[-1])
            usd_fiyat = float(usd_ticker['Close'].iloc[-1])
            if ons_fiyat > 500 and usd_fiyat > 5:
                saf_gram = (ons_fiyat / 31.10347) * usd_fiyat
                ceyrek_fiyat = saf_gram * 1.635
                return saf_gram, ceyrek_fiyat, ceyrek_fiyat * 2, ceyrek_fiyat * 4
    except: pass
    return 3020.50, 4950.00, 9900.00, 19800.00 

# Zaman Göstergesi
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px;">🕒 {guncel_an}</div>', unsafe_allow_html=True)

# ALTIN PANELİ
st.markdown("#### 🟡 Canlı Altın Fiyatları")
p_gram, p_ceyrek, p_yarim, p_tam = canli_altin_fiyatlarini_hesapla()
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="piyasa-kutusu">🔱 GRAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_gram:,.2f} TL</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="piyasa-kutusu">🪙 ÇEYREK ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_ceyrek:,.2f} TL</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="piyasa-kutusu">🥈 YARIM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_yarim:,.2f} TL</span></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="piyasa-kutusu">🥇 TAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_tam:,.2f} TL</span></div>', unsafe_allow_html=True)

st.write("---")

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
    # Boş satırları veya başlıkları atlayarak verileri tarıyoruz
    for idx in range(1, len(df_kaynak)):
        try:
            # Excel sütun uzunluğu kontrolü
            if len(df_kaynak.columns) > 17:
                
                # -------------------------------------------------------------
                # Kağıttaki ÜST KISIM: BTA Hisseleri Veri Eşlemesi
                # R Sütunu (İndeks 17) -> BTA PUAN
                # A Sütunu (İndeks 0)  -> BTA HİSSE
                # C Sütunu (İndeks 2)  -> BTA ALIM (300 Sabit kalacak)
                # -------------------------------------------------------------
                bta_puan_raw = str(df_kaynak.iloc[idx, 17]).strip() if not pd.isna(df_kaynak.iloc[idx, 17]) else ""
                bta_hisse_raw = str(df_kaynak.iloc[idx, 0]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 0]) else ""
                bta_alim_raw = str(df_kaynak.iloc[idx, 2]).strip() if not pd.isna(df_kaynak.iloc[idx, 2]) else ""

                # Eğer A sütununda geçerli bir hisse adı varsa Üst Tabloya ekle
                if bta_hisse_raw and bta_hisse_raw not in ["NAN", "NONE", "HİSSE", "BTA HİSSE"]:
                    hisse_kodlari = re.findall(r'[A-Z]+', bta_hisse_raw)
                    if hisse_kodlari:
                        hisse = hisse_kodlari[0]
                        # İnternetten Canlı Anlık Fiyat Alımı
                        anlik_fiyat = hızlı_canli_fiyat_bul(hisse)
                        
                        tablo_bta_hisseleri.append({
                            "BTA PUAN 🔢": bta_puan_raw,
                            "BTA HİSSE 📈": hisse,
                            "BTA ALIM 📥": bta_alim_raw if bta_alim_raw else "300 Sabit",
                            "GÜNCEL FİYAT 💥": f"{anlik_fiyat:.2f} TL" if anlik_fiyat > 0 else "İnternetten alınıyor..."
                        })

                # -------------------------------------------------------------
                # Kağıttaki ALT KISIM: Günlük Al-Sat Hisseleri Veri Eşlemesi
                # Örnek: Eğer Excel şablonunuzda Günlük Al-Sat hisseleri farklı bir sütundaysa 
                # (Örn: U sütunu/20. indeks) burayı ona göre eşler.
                # -------------------------------------------------------------
                if len(df_kaynak.columns) > 20:
                    alsat_hisse_raw = str(df_kaynak.iloc[idx, 20]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 20]) else ""
                    
                    if alsat_hisse_raw and alsat_hisse_raw not in ["NAN", "NONE", "AL_SAT SİNYALİ", "HİSSE"]:
                        alsat_kodlari = re.findall(r'[A-Z]+', alsat_hisse_raw)
                        if alsat_kodlari:
                            as_hisse = alsat_kodlari[0]
                            as_anlik_fiyat = hızlı_canli_fiyat_bul(as_hisse)
                            
                            tablo_gunluk_alsat.append({
                                "GÜNLÜK BTA AL SAT ⚡": as_hisse,
                                "ANLIK VERİ CANLI 📊": f"{as_anlik_fiyat:.2f} TL" if as_anlik_fiyat > 0 else "Yükleniyor..."
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
    st.info("Excel'in ilgili sütunlarında (A ve R) BTA hisse verisi bulunamadı.")

st.write("")

# 2. ALT KISIM TABLOSU: GÜNLÜK AL SAT HİSSELERİ
st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
if tablo_gunluk_alsat:
    df_alsat = pd.DataFrame(tablo_gunluk_alsat)
    st.dataframe(df_alsat, use_container_width=True, hide_index=True)
else:
    # Eğer Excel'de 20. sütun boşsa kağıttaki örnek ALCAR hissesini test olarak gösterir
    temiz_alcar_fiyat = hızlı_canli_fiyat_bul("ALCAR")
    test_veri = [{"GÜNLÜK BTA AL SAT ⚡": "ALCAR", "ANLIK VERİ CANLI 📊": f"{temiz_alcar_fiyat:.2f} TL"}]
    st.dataframe(pd.DataFrame(test_veri), use_container_width=True, hide_index=True)

# ⚠️ SPK UYARI KUTUSU
st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır.</div>', unsafe_allow_html=True)
