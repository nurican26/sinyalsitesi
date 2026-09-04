import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Profesyonel Terminal Tasarımı
st.set_page_config(page_title="BTA Veri Analizi", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #090d16 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .istatistik-baslik {background: linear-gradient(90deg, #ca8a04 0%, #111827 100%); padding: 10px; border-radius: 6px; font-weight: bold; margin-top: 15px; margin-bottom: 15px;} .analiz-baslik {background: linear-gradient(90deg, #16a34a 0%, #111827 100%); padding: 10px; border-radius: 6px; font-weight: bold; margin-top: 15px; margin-bottom: 15px;} .bta-logo-konteyner {display: flex; align-items: center; margin-top: 15px; margin-bottom: 25px;} .bta-logo {background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white !important; font-family: "Segoe UI", sans-serif !important; font-weight: bold; font-size: 2.2rem; padding: 4px 25px; border-radius: 12px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.04); border: 1px solid #eab308; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold;} .haber-kutusu {background: #1e293b; border-left: 4px solid #10b981; padding: 14px; border-radius: 8px; margin-bottom: 12px;} .gundem-kutusu {background: #1e293b; border-left: 4px solid #3b82f6; padding: 14px; border-radius: 8px; margin-bottom: 12px;} .kap-kutusu {background: #1e293b; border-left: 4px solid #a855f7; padding: 14px; border-radius: 8px; margin-bottom: 12px;}</style>', unsafe_allow_html=True)

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

# Üst Zaman Bilgisi ve Yenileme Butonu
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
col_refresh, col_time = st.columns(2)
with col_refresh:
    if st.button("🔄 Verileri Yenile"):
        st.session_state["fiyat_hafizasi"] = {}
        st.session_state["excel_kayit_hafizasi"] = {} # Excel kilitlenen fiyat hafızası da temizleniyor
        st.rerun()
with col_time:
    st.markdown(f'<div style="font-size: 1rem; color: #cbd5e1; padding-top: 5px; text-align: right;">🕒 Son Güncelleme: {guncel_an}</div>', unsafe_allow_html=True)

st.write("---")

# MATEMATİKSEL DEĞERLER PANELİ
st.markdown("#### 🟡 Referans Emtia Değerleri")
p_gram, p_ceyrek, p_yarim, p_tam = canli_altin_fiyatlarini_hesapla()
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="piyasa-kutusu">🔱 REF. GRAM<br><span style="color:#eab308; font-size:1.4rem;">{p_gram:,.2f} TL</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="piyasa-kutusu">🪙 REF. ÇEYREK<br><span style="color:#eab308; font-size:1.4rem;">{p_ceyrek:,.2f} TL</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="piyasa-kutusu">🥈 REF. YARIM<br><span style="color:#eab308; font-size:1.4rem;">{p_yarim:,.2f} TL</span></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="piyasa-kutusu">🥇 REF. TAM<br><span style="color:#eab308; font-size:1.4rem;">{p_tam:,.2f} TL</span></div>', unsafe_allow_html=True)

st.write("---")

# 🎛️ BORSADAKİ TÜM HİSSELERE AÇILAN CANLI SORGULAMA PENCERESİ
st.markdown('<div class="istatistik-baslik">🟡 BORSA İSTANBUL TÜM HİSSELER - İNTERNETTEN CANLI VERİ MOTORU</div>', unsafe_allow_html=True)
arama_terimi = st.text_input("Aramak istediğiniz herhangi bir hisse kodunu girin (Örn: THYAO, SASA, EREGL):", "").strip().upper()

if arama_terimi:
    canli_sorgu_fiyat = hızlı_canli_fiyat_bul(arama_terimi)
    if canli_sorgu_fiyat > 0:
        tablo_canli_arama = [[arama_terimi, f"{canli_sorgu_fiyat:.2f} TL", "Kesintisiz Canlı Veri"]]
        df_arama = pd.DataFrame(tablo_canli_arama, columns=["Hisse Kodu", "Anlık İnternet Canlı Fiyatı", "Veri Akış Durumu"])
        st.dataframe(df_arama, use_container_width=True, hide_index=True)
    else:
        st.write("❌ Hisse kodu bulunamadı veya sunucu yanıt vermiyor. Lütfen kontrol edin (Örn: THYAO).")
else:
    st.write("🔎 Yukarıdaki kutuya bir BIST hisse kodu yazarak anlık fiyat sorgulaması yapabilirsiniz.")

st.write("---")

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
                wv_kontrol = str(df_kaynak.iloc[idx, 22]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 22]) else ""
                
                if wv_kontrol and wv_kontrol not in ["NAN", "NONE", "SİNYALİ", "AL"]:
                    parcalar = wv_kontrol.split(' ')
                    if parcalar:
                        hisse = str(parcalar[0]).strip()
                        
                        if len(hisse) >= 3 and hisse not in ["AL", "NONE", "NAN"]:
                            if arama_terimi == "" or arama_terimi in hisse:
                                anlik_canli = hızlı_canli_fiyat_bul(hisse)
                                
                                if anlik_canli > 0:
                                    if hisse not in st.session_state["excel_kayit_hafizasi"]:
                                        st.session_state["excel_kayit_hafizasi"][hisse] = anlik_canli
                                    
                                    yuklenen_fiyat = st.session_state["excel_kayit_hafizasi"].get(hisse, anlik_canli)
                                    puan_bul = re.findall(r'\((.*?)\)', wv_kontrol)
                                    final_puan = str(puan_bul[0]).strip() if puan_bul else "0.04"
                                    
                                    # Sizin orijinal listeniz (Kendi eklemeleriniz için ucu açık bırakıldı)
                                    f_yuklenen = f"{yuklenen_fiyat:.2f} TL"
                                    tablo_al.append([hisse, f_yuklenen, final_puan])
        except:
            pass

# Sizin kodunuzun bittiği yerdeki Excel verilerini ekrana basan ana tablo yapısı
if tablo_al:
    df_excel_tablo = pd.DataFrame(tablo_al, columns=["Hisse Kodu", "Fiyat", "Puan"])
    st.dataframe(df_excel_tablo, use_container_width=True, hide_index=True)

# ⏱️ 60 SANİYEDE BİR ARKA PLANDA OTOMATİK YENİLEME MOTORU (GÖRÜNMEZ TETİKLEYİCİ)
st.components.v1.html(
    """
    <script>
    setTimeout(function(){
        window.parent.location.reload();
    }, 60000);
    </script>
    """,
    height=0,
)
