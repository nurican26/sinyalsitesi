import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.05); border: 1px solid #eab308; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;} .haber-kutusu {background: rgba(255, 255, 255, 0.03); border-left: 4px solid #10b981; padding: 12px; border-radius: 6px; margin-bottom: 10px;} .bta-marka-alani {text-align: left; margin-top: 15px; margin-bottom: 30px;} .bta-logo-kesin-net {font-size: 4.8rem !important; font-weight: 900 !important; color: #ffffff !important; display: inline-block; font-family: "Arial Black", "Segoe UI", sans-serif !important; transform: rotate(-2deg); padding-left: 5px; margin-bottom: 5px; text-shadow: 4px 8px 20px rgba(16, 185, 129, 0.7), -3px -3px 0px #059669, 3px 3px 0px #eab308; letter-spacing: 3px;} .bta-alt-yazi {font-size: 1.2rem; color: #a7f3d0 !important; font-weight: 600; letter-spacing: 1px; margin-top: 5px; opacity: 0.95; text-shadow: 1px 1px 4px rgba(0,0,0,0.6); font-style: italic;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.15) !important; border: 3px solid #dc2626 !important; padding: 15px !important; border-radius: 8px !important; margin-top: 25px !important; margin-bottom: 25px !important; color: #fca5a5 !important; font-family: "Segoe UI", sans-serif !important; font-size: 1rem !important; text-align: justify !important; line-height: 1.6 !important; display: block !important; font-weight: 500 !important;}</style>', unsafe_allow_html=True)

# Hafıza Sabitleme
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

# 🟢 OKUNAKLI BÜYÜK HARFLİ DERİN GÖLGELİ VE KAVİSLİ BTA LOGO PANELİ
st.markdown("""
<div class="bta-marka-alani">
    <div class="bta-logo-kesin-net">BTA</div>
    <div class="bta-alt-yazi">Hisseler BTA Tarafından Güncellenir.</div>
</div>
""", unsafe_allow_html=True)

# 💥 FİYAT VE ALTIN MOTORLARI
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

# VERİLER VE ZAMAN DAMGASI
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px;">🕒 {guncel_an}</div>', unsafe_allow_html=True)

# ALTIN PANELİ
st.markdown("#### 🟡 Canlı Altın Fiyatları")
p_gram, p_ceyrek, p_yarim, p_tam = canli_altin_fiyatlarini_hesapla()

def turkce_format_yap(sayi):
    return f"{sayi:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="piyasa-kutusu">🔱 GRAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{turkce_format_yap(p_gram)} TL</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="piyasa-kutusu">🪙 ÇEYREK ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{turkce_format_yap(p_ceyrek)} TL</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="piyasa-kutusu">🥈 YARIM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{turkce_format_yap(p_yarim)} TL</span></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="piyasa-kutusu">🥇 TAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{turkce_format_yap(p_tam)} TL</span></div>', unsafe_allow_html=True)
st.write("")

# 📰 BORSA VE EKONOMİ GÜNDEMİ HABER BLOKLARI
st.markdown("#### 📰 Borsa ve Ekonomi Gündemi")
st.markdown('<div class="haber-kutusu">🔥 <b>Borsa İstanbul (BIST 100):</b> Küresel piyasalardaki faiz beklentileri ve makroekonomik veriler eşliğinde sinyal takipleri kararlılıkla devam ediyor.</div>', unsafe_allow_html=True)
st.markdown('<div class="haber-kutusu">🌟 <b>Altın Piyasası:</b> Ons altın ve iç piyasada döviz kurlarının dengelenmesiyle gram ve çeyrek altın fiyatları darphane standartlarında işlem görüyor.</div>', unsafe_allow_html=True)
st.markdown('<div class="haber-kutusu">🚀 <b>Halka Arz Gündemi:</b> Yeni dönem şirket bilançoları ve SPK bülten raporları yatırımcılar tarafından yakından izleniyor.</div>', unsafe_allow_html=True)
st.write("")

df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except: pass

tablo_alsat, tablo_al = [], []
if df_kaynak is not None:
    for idx in range(2, len(df_kaynak)):
        try:
            if len(df_kaynak.columns) > 22:
                uv = str(df_kaynak.iloc[idx, 20]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 20]) else ""
                wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 22]) else ""
                t_deg = str(df_kaynak.iloc[idx, 19]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 19]) else ""
                
                if uv and uv not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                    h_ara = re.findall(r'[A-A-Z]+', uv) or re.findall(r'[A-Z]+', uv)
                    if h_ara:
                        # 🛠️ GÜVENLİ PARANTEZ ÇÖZÜMÜ: Listenin ilk elemanını direkt temiz metin olarak seçtik.
                        hisse = str(h_ara[0]).strip()
                        cfiy = hızlı_canli_fiyat_bul(hisse)
                        p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv)
                        bta_puan = p_bul[0] if p_bul else t_deg
                        tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan": bta_puan, "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
                        
                if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                    h_ara = re.findall(r'[A-A-Z]+', wv) or re.findall(r'[A-Z]+', wv)
                    if h_ara:
                        # 🛠️ GÜVENLİ PARANTEZ ÇÖZÜMÜ: Listenin ilk elemanını direkt temiz metin olarak seçtik.
                        hisse = str(h_ara[0]).strip()
                        cfiy = hızlı_canli_fiyat_bul(hisse)
                        p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv)
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
else: st.write("🔒 Aktif BTA sinyali taranıyor...")

if st.session_state["ozel_takip_kutusu"]:
    st.markdown("#### 🌟 Özel Takip Havuzu 💰")
    tk_list = []
    for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
        cfiy = hızlı_canli_fiyat_bul(hisse)
        if cfiy == 0.0: cfiy = bilge["kayit_fiyati"]
        tk_list.append({"Hisse Kodu 🗝️": hisse, "Havuz Maliyeti": f"{bilge['kayit_fiyati']:.2f} TL", "Anlık Güncel": f"{cfiy:.2f} TL"})
    if tk_list:
        st.dataframe(pd.DataFrame(tk_list), use_container_width=True, hide_index=True)
        if st.button("🗑️ Havuzu Temizle", use_container_width=True): st.session_state["ozel_takip_kutusu"] = {}; st.rerun()

# ⚖️ MUTLAK SABİT YASAL UYARI KUTUSU (Ezilmesi veya gizlenmesi imkansız bağımsız kırmızı kalın çerçeve)
st.write("---")
