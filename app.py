import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Profesyonel Terminal Tasarımı
st.set_page_config(page_title="BTA Veri Analizi", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .istatistik-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .analiz-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .bta-logo-konteyner {display: flex; align-items: center; margin-top: 15px; margin-bottom: 25px;} .bta-logo {background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white !important; font-family: "Segoe UI", sans-serif !important; font-weight: bold; font-size: 2.2rem; padding: 4px 25px; border-radius: 12px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.05); border: 1px solid #eab308; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;} .haber-kutusu {background: rgba(255, 255, 255, 0.03); border-left: 4px solid #10b981; padding: 12px; border-radius: 6px; margin-bottom: 10px;} .gundem-kutusu {background: rgba(255, 255, 255, 0.03); border-left: 4px solid #3b82f6; padding: 12px; border-radius: 6px; margin-bottom: 10px;}</style>', unsafe_allow_html=True)

# Hafıza Sabitleme
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

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
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        return st.session_state["fiyat_hafizasi"][hisse_kodu]
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

# Zaman Bilgisi ve Yenileme Butonu
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
col_refresh, col_time = st.columns(2)
with col_refresh:
    if st.button("🔄 Verileri Yenile"):
        st.session_state["fiyat_hafizasi"] = {}
        st.rerun()
with col_time:
    st.markdown(f'<div style="font-size: 1rem; color: #cbd5e1; padding-top: 5px;">🕒 Son Veri Güncelleme: {guncel_an}</div>', unsafe_allow_html=True)

# MATEMATİKSEL DEĞERLER PANELİ
st.markdown("#### 🟡 Referans Emtia Değerleri")
p_gram, p_ceyrek, p_yarim, p_tam = canli_altin_fiyatlarini_hesapla()
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="piyasa-kutusu">🔱 GRAM<br><span style="color:#eab308; font-size:1.4rem;">{p_gram:,.2f} TL</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="piyasa-kutusu">🪙  ÇEYREK<br><span style="color:#eab308; font-size:1.4rem;">{p_ceyrek:,.2f} TL</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="piyasa-kutusu">🥈 YARIM<br><span style="color:#eab308; font-size:1.4rem;">{p_yarim:,.2f} TL</span></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="piyasa-kutusu">🥇 TAM<br><span style="color:#eab308; font-size:1.4rem;">{p_tam:,.2f} TL</span></div>', unsafe_allow_html=True)
st.write("")

# 📌 İKİYE BÖLÜNMÜŞ HABER MERKEZİ
col_eko, col_genel = st.columns(2)
with col_eko:
    st.markdown("#### 📰 Türkiye Ekonomi Gündemi")
    st.markdown('<div class="haber-kutusu">📊 <b>Ağustos Enflasyonu Açıklandı:</b> TÜİK yıllık tüketici enflasyonunu (TÜFE) piyasa öngörülerine paralel olarak %31,51 seviyesinde duyurdu.</div>', unsafe_allow_html=True)
    st.markdown('<div class="haber-kutusu">🏛️ <b>Merkez Bankası Likidite Hamlesi:</b> TCMB, piyasadaki fazla likiditeyi sterilize etmek amacıyla repo ihalelerine başladı.</div>', unsafe_allow_html=True)
with col_genel:
    st.markdown("#### 🌐 Türkiye Genel Gündem Başlıkları")
    st.markdown('<div class="gundem-kutusu">✈️ <b>Milli Savunmada Kritik Aşama:</b> Eurofighter Typhoon savaş uçakları tedariki kapsamında pilotların uçuş eğitimleri başlıyor.</div>', unsafe_allow_html=True)
    st.markdown('<div class="gundem-kutusu">🚊 <b>Ulaşım ve Altyapı Yatırımları:</b> Havalimanları ve yeni metro/tramvay hatlarının genişletilmesine yönelik bölge yatırımları hız kazandı.</div>', unsafe_allow_html=True)

st.write("")

# 🎛️ BORSADAKİ TÜM HİSSELERE AÇILAN CANLI SORGULAMA PENCERESI
st.markdown('<div class="istatistik-baslik">🟡 BORSA İSTANBUL TÜM HİSSELER - İNTERNETTEN CANLI VERİ MOTORU</div>', unsafe_allow_html=True)
arama_terimi = st.text_input("Aramak istediğiniz herhangi bir hisse kodunu girin (Örn: THYAO, SASA, EREGL):", "").strip().upper()

if arama_terimi:
    canli_sorgu_fiyat = hızlı_canli_fiyat_bul(arama_terimi)
    if canli_sorgu_fiyat > 0:
        tablo_canli_arama = [{
            "Aranan Varlık": arama_terimi,
            "Anlık İnternet Canlı Fiyatı": f"{canli_sorgu_fiyat:.2f} TL",
            "Veri Akış Durumu": "Kesintisiz Canlı Veri"
        }]
        st.dataframe(pd.DataFrame(tablo_canli_arama), use_container_width=True, hide_index=True)
    else:
        st.write("❌ Hisse kodu bulunamadı veya Yahoo Finance veri sunucusuna bağlanılamıyor. Lütfen kodu kontrol edin (Örn: THYAO).")
else:
    st.write("🔎 Yukarıdaki kutuya bir BIST hisse kodu yazarak anlık fiyat sorgulaması yapabilirsiniz.")

st.write("")

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
            if len(df_kaynak.columns) > 22:
                wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 22]) else ""
                t_deg = str(df_kaynak.iloc[idx, 19]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 19]) else ""
                
               # 🟢 BTA MATEMATİKSEL VERİ MODELLEMESİ
if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
    h_ara = re.findall(r'[A-Z]+', wv)
    if h_ara:
        hisse = str(h_ara[0]).strip()
        if 4 <= len(hisse) <= 5 and hisse not in ["NONE", "NAN", "SINYAL"]:
            cfiy = hızlı_canli_fiyat_bul(hisse)
            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', wv)
            
            # T harfi eklenmiş dinamik puan ataması (Başına ekler)
            bta_puan = f"T {p_bul[0]}" if p_bul else f"T {t_deg}"
            
            tablo_al.append({
                "Varlık Kodu": hisse, 
                "BTA Puanı": bta_puan,  # Sütun adı ve veri formatı düzeltildi
                "Anlık Fiyat": f"{cfiy:.2f} TL" if cfiy > 0 else "Hesaplanıyor...",
                "Matris Durumu": "Pozitif Matris"
            })
                        
        except: pass

# 2. BTA Matematiksel Veri Modellemesi Ekrana Basma
st.markdown('<div class="analiz-baslik">🟢 BTA MATEMATİKSEL VERİ MODELLEMESİ</div>', unsafe_allow_html=True)
if tablo_al: 
    st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
else: 
    st.write("⏳ Matematiksel veri tabanı taranıyor...")

# Sorumluluk Reddi Beyanı
st.markdown('<div style="font-size: 0.85rem; color: #94a3b8; text-align: justify; margin-top: 40px; padding: 10px; border-top: 1px solid #334155;"><b>Sorumluluk Reddi Beyanı:</b> Bu platformda sunulan tüm veriler, listeler ve hesaplamalar tamamen matematiksel algoritmalara ve geçmiş istatistiki verilere dayalı bir veri simülasyonudur. Burada yer alan hiçbir ifade, başlık, tablo veya puanlama 6362 sayılı Sermaye Piyasası Kanunu kapsamında bir yatırım danışmanlığı, alım-satım tavsiyesi veya finansal sinyal teşkil etmez. Kullanıcıların veri modellerine dayalı alacağı kararlar tamamen kendi sorumluluğundadır.</div>', unsafe_allow_html=True)

# Otomatik arka plan yenileme tetikleyici (60 saniye)
time.sleep(60)
st.rerun()
