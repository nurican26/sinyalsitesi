import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Profesyonel Terminal Tasarımı
st.set_page_config(page_title="BTA Veri Analizi", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #090d16 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .istatistik-baslik {background: linear-gradient(90deg, #ca8a04 0%, #111827 100%); padding: 10px; border-radius: 6px; font-weight: bold; margin-top: 15px; margin-bottom: 15px;} .analiz-baslik {background: linear-gradient(90deg, #16a34a 0%, #111827 100%); padding: 10px; border-radius: 6px; font-weight: bold; margin-top: 15px; margin-bottom: 15px;} .bta-logo-konteyner {display: flex; align-items: center; margin-top: 15px; margin-bottom: 25px;} .bta-logo {background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white !important; font-family: "Segoe UI", sans-serif !important; font-weight: bold; font-size: 2.2rem; padding: 4px 25px; border-radius: 12px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.04); border: 1px solid #eab308; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold;} .haber-kutusu {background: #1e293b; border-left: 4px solid #10b981; padding: 14px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);} .gundem-kutusu {background: #1e293b; border-left: 4px solid #3b82f6; padding: 14px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);} .kap-kutusu {background: #1e293b; border-left: 4px solid #a855f7; padding: 14px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}</style>', unsafe_allow_html=True)

# Hafıza Sabitleme
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}
if "excel_kayit_hafizasi" not in st.session_state: st.session_state["excel_kayit_hafizasi"] = {}

# LOGO
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA ANALİTİK</div></div>', unsafe_allow_html=True)

# 💥 CANLI VERİ MOTORLARI
def hızlı_canli_fiyat_bul(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        saved_time, saved_price = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - saved_time < 60: return saved_price
    try:
        ticker = yf.Ticker(f"{hisse_kodu}.IS")
        data = ticker.history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            fiyat = float(data['Close'].iloc[-1])
            st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
            return fiyat
    except: pass
    return st.session_state["fiyat_hafizasi"].get(hisse_kodu, 0.0)

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

# Üst Bilgi Paneli
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
col_refresh, col_time = st.columns(2)
with col_refresh:
    if st.button("🔄 Verileri Yenile"):
        st.session_state["fiyat_hafizasi"] = {}
        st.rerun()
with col_time:
    st.markdown(f'<div style="font-size: 1rem; color: #cbd5e1; padding-top: 5px; text-align: right;">🕒 Son Güncelleme: {guncel_an}</div>', unsafe_allow_html=True)

st.write("---") # ➡️ Görsel Ayraç Çizgisi

# MATEMATİKSEL DEĞERLER PANELİ
st.markdown("#### 🟡 Referans Emtia Değerleri")
p_gram, p_ceyrek, p_yarim, p_tam = canli_altin_fiyatlarini_hesapla()
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="piyasa-kutusu">🔱 REF. GRAM<br><span style="color:#eab308; font-size:1.4rem;">{p_gram:,.2f} TL</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="piyasa-kutusu">🪙 REF. ÇEYREK<br><span style="color:#eab308; font-size:1.4rem;">{p_ceyrek:,.2f} TL</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="piyasa-kutusu">🥈 REF. YARIM<br><span style="color:#eab308; font-size:1.4rem;">{p_yarim:,.2f} TL</span></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="piyasa-kutusu">🥇 REF. TAM<br><span style="color:#eab308; font-size:1.4rem;">{p_tam:,.2f} TL</span></div>', unsafe_allow_html=True)

st.write("---") # ➡️ Görsel Ayraç Çizgisi

# 📌 İKİYE BÖLÜNMÜŞ HABER MERKEZİ
col_eko, col_genel = st.columns(2)
with col_eko:
    st.markdown("#### 📰 Türkiye Ekonomi Gündemi")
    st.markdown('<div class="haber-kutusu">📊 <b>Ağustos Enflasyonu Açıklandı:</b> TÜİK yıllık tüketici enflasyonunu (TÜFE) piyasa öngörülerine paralel olarak %31,51 seviyesinde duyurdu.</div>', unsafe_allow_html=True)
    st.markdown('<div class="haber-kutusu">🏛️ <b>Merkez Bankası Likidite Hamlesi:</b> TCMB, piyasadaki fazla likiditeyi sterilize etmek amacıyla repo ihalelerine başladı.</div>', unsafe_allow_html=True)
with col_genel:
    st.markdown("#### 🌐 Türkiye Genel Gündem Başlıkları")
    st.markdown('<div class="gundem-kutusu">✈️ <b>Milli Savunmada Kritik Aşama:</b> Eurofighter Typhoon savaş uçakları tedariki kapsamında pilotların uçuş eğitimleri başlıyor.</div>', unsafe_allow_html=True)
    st.markdown('<div class="gundem-kutusu">🚊 <b>Ulaşım ve Altyapı Yatırımları:</b> Havalimanları ve metro hatlarının genişletilmesine yönelik bölge yatırımları hız kazandı.</div>', unsafe_allow_html=True)

st.write("---") # ➡️ Görsel Ayraç Çizgisi

# 📢 MANUEL SEÇİLMİŞ 3 KRİTİK KAP HABERİ BÖLÜMÜ
st.markdown("#### 🔮 Kritik KAP Gelişmeleri")
st.markdown('<div class="kap-kutusu">💼 <b>ASELSAN (ASELS):</b> MSB ile savunma sistemleri tedariki kapsamında 42 milyon dolar tutarında sözleşme imzalandığını duyurdu.</div>', unsafe_allow_html=True)
st.markdown('<div class="kap-kutusu">🔋 <b>KONTROLMATİK (KONTR):</b> Yurt dışı iştirakinin ABD merkezli enerji depolama projesinde niyet mektubu imzaladığını bildirdi.</div>', unsafe_allow_html=True)
st.markdown('<div class="kap-kutusu">📊 <b>TÜRK HAVA YOLLARI (THYAO):</b> Gelecek dönem filo genişletme stratejileri doğrultusunda 4 adet yeni geniş gövdeli uçak kiralandığını açıkladı.</div>', unsafe_allow_html=True)

st.write("---") # ➡️ Görsel Ayraç Çizgisi

# 🎛️ BORSADAKİ TÜM HİSSELERE AÇILAN CANLI SORGULAMA PENCERESİ
st.markdown('<div class="istatistik-baslik">🟡 BORSA İSTANBUL TÜM HİSSELER - İNTERNETTEN CANLI VERİ MOTORU</div>', unsafe_allow_html=True)
arama_terimi = st.text_input("Aramak istediğiniz herhangi bir hisse kodunu girin (Örn: THYAO, SASA, EREGL):", "").strip().upper()

if arama_terimi:
    canli_sorgu_fiyat = hızlı_canli_fiyat_bul(arama_terimi)
    if canli_sorgu_fiyat > 0:
        tablo_canli_arama = [["Aranan Varlık", f"{canli_sorgu_fiyat:.2f} TL", "Kesintisiz Canlı Veri"]]
        df_arama = pd.DataFrame(tablo_canli_arama, columns=["Aranan Varlık", "Anlık İnternet Canlı Fiyatı", "Veri Akış Durumu"])
        st.dataframe(df_arama, use_container_width=True, hide_index=True)
    else:
        st.write("❌ Hisse kodu bulunamadı veya sunucu yanıt vermiyor. Lütfen kontrol edin (Örn: THYAO).")
else:
    st.write("🔎 Yukarıdaki kutuya bir BIST hisse kodu yazarak anlık fiyat sorgulaması yapabilirsiniz.")

st.write("---") # ➡️ Görsel Ayraç Çizgisi

# EXCEL VERİ TABANI OKUMA VE MATEMATİKSEL MODELLEME
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except: pass

tablo_al = []
if df_kaynak is not None:
    for idx in range(2, len(df_kaynak)):
        try:
            # 🛠️ GÜVENLİK YUMUŞATILDI: Hisselerin görünmesini engelleyen sütun filtresi esnetildi
            wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if idx < len(df_kaynak) else ""
            if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                h_ara = re.findall(r'[A-Z]+', wv)
                if h_ara:
                    hisse = str(h_ara[0]).strip()
                    if len(hisse) >= 3: # Kod uzunluğu filtresi genişletildi
                        if arama_terimi == "" or arama_terimi in hisse:
                            anlik_canli = hızlı_canli_fiyat_bul(hisse)
                            if hisse not in st.session_state["excel_kayit_hafizasi"] and anlik_canli > 0:
                                st.session_state["excel_kayit_hafizasi"][hisse] = anlik_canli
                            yuklenen_fiyat = st.session_state["excel_kayit_hafizasi"].get(hisse, anlik_canli)
                            
                            ham_r_degeri = df_kaynak.iloc[idx, 17]
                            final_puan = "0.00" if pd.isna(ham_r_degeri) else str(ham_r_degeri).strip()
                            
                            f_yuklenen = f"{yuklenen_fiyat:.2f} TL" if yuklenen_fiyat > 0 else "Hesaplanıyor..."
                            f_canli = f"{anlik_canli:.2f} TL" if anlik_canli > 0 else "Yükleniyor..."
                            
                            tablo_al.append([hisse, final_puan, f_yuklenen, f_canli, "Pozitif Matris"])
        except: pass

