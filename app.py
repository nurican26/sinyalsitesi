import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re
import time

# 1. Sayfa Yapılandırması ve Tasarım
st.set_page_config(page_title="BTA Finans", page_icon="📈", layout="wide")

st.markdown('''
<style>
    @import url('https://googleapis.com');
    .stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;}
    h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;}
    input {color: #000!important; background-color: #fff!important;}
    .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}
    div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;}
    .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 8px; font-size: 1.1rem;}
    .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 8px; font-size: 1.1rem;}
    .arama-baslik {background: linear-gradient(90deg, #2563eb 0%, #1e1b4b 100%); padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 15px; font-size: 1.1rem;}
    .bta-logo-konteyner {display: flex; justify-content: center; align-items: center; margin-top: 20px; margin-bottom: 25px;}
    .bta-logo {color: #ffffff !important; font-family: "Dancing Script", cursive !important; font-weight: bold; font-size: 5.5rem; padding: 0px; letter-spacing: 12px; text-shadow: 0 0 10px #ff007f, 0 0 20px #ff00ff, 0 0 30px #00ffff, 0 0 40px #00ff00, 0 0 70px #ffff00, 0 0 80px #ff7f00, 0 0 100px #ff0000;}
    .gold-card {background: rgba(251, 191, 36, 0.08); border: 1px solid #fbbf24; border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 0 15px rgba(251, 191, 36, 0.15); margin-bottom: 15px;}
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;}
</style>
''', unsafe_allow_html=True)

# Hafıza Durum Yönetimi
if "ozel_takip_kutusu" not in st.session_state:
    st.session_state["ozel_takip_kutusu"] = {}
if "altin_hafizasi" not in st.session_state:
    st.session_state["altin_hafizasi"] = {}
if "fiyat_hafizasi" not in st.session_state:
    st.session_state["fiyat_hafizasi"] = {}
if "ziyaret_sayaci" not in st.session_state:
    st.session_state["ziyaret_sayaci"] = 0

if "ziyaret_edildi" not in st.session_state:
    st.session_state["ziyaret_sayaci"] += 1
    st.session_state["ziyaret_edildi"] = True

# Kararlı Yardımcı Fonksiyonlar
def formatla_tl(deger):
    if not deger or pd.isna(deger) or deger == 0: 
        return "Yükleniyor..."
    return "{:,.2f}".format(deger).replace(",", "X").replace(".", ",").replace("X", ".")

def formatla_yuzde(deger):
    if pd.isna(deger) or deger is None: 
        return "%0.00"
    prefix = "+" if deger > 0 else ""
    return f"{prefix}{deger:.2f}%"

def havuzu_temizle_aksiyon():
    st.session_state["ozel_takip_kutusu"] = {}
    st.rerun()

def temiz_metin_al(val):
    if pd.isna(val): 
        return ""
    return str(val).strip().upper()

# Bağımsız veri parçalayıcı fonksiyon
def hücre_parçala(metin):
    metin_str = temiz_metin_al(metin)
    if not metin_str or metin_str in ["NAN", "NONE", "AL_SAT SİNYALİ", "SİNYALİ", "AL"]:
        return "", ""
    hisse_bul = re.findall(r'[A-Z]+', metin_str)
    if not hisse_bul:
        return "", ""
    hisse = "".join(hisse_bul)
    if len(hisse) < 2:
        return "", ""
    puan_bul = re.findall(r'[-+]?\d*[.,]\d+|\d+', metin_str)
    puan = "".join(puan_bul) if puan_bul else ""
    return hisse, puan

# Önbellekli Fiyat Motoru
def hizli_fiyat_al(hisse_kodu):
    if hisse_kodu in st.session_state["fiyat_hafizasi"]:
        kayit_vakti, eski_fiyat = st.session_state["fiyat_hafizasi"][hisse_kodu]
        if time.time() - kayit_vakti < 300: 
            return eski_fiyat
    try:
        data = yf.Ticker(f"{hisse_kodu}.IS").history(period="1d")
        if not data.empty and not pd.isna(data['Close'].iloc[-1]):
            fiyat = float(data['Close'].iloc[-1])
            st.session_state["fiyat_hafizasi"][hisse_kodu] = (time.time(), fiyat)
            return fiyat
    except:
        pass
    return 0.0

# 🌟 LOGO ALANI
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; text-align: center; margin-bottom: 20px;">🚪 <b>Ziyaret:</b> {st.session_state["ziyaret_sayaci"]} | 🕒 {guncel_an}</div>', unsafe_allow_html=True)

# 🪙 CANLI ALTIN MOTORU
def canlı_altın_fiyatları_hesapla():
    anlik_zaman = time.time()
    if "vakit" in st.session_state["altin_hafizasi"]:
        if anlik_zaman - st.session_state["altin_hafizasi"]["vakit"] < 300: 
            return st.session_state["altin_hafizasi"]["fiyatlar"]
    try:
        ons_data = yf.Ticker("GC=F").history(period="1d")
        usd_data = yf.Ticker("USDTRY=X").history(period="1d")
        if not ons_data.empty and not usd_data.empty:
            ons = ons_data['Close'].iloc[-1]
            usd = usd_data['Close'].iloc[-1]
            gram_has = (ons / 31.1034768) * usd
            ceyrek = gram_has * 1.75 * 0.916 * 1.03 
            yarim = ceyrek * 2
            tam = ceyrek * 4
            fiyatlar = {"gram": gram_has, "ceyrek": ceyrek, "yarim": yarim, "tam": tam}
            st.session_state["altin_hafizasi"] = {"vakit": anlik_zaman, "fiyatlar": fiyatlar}
            return fiyatlar
    except:
        pass
    return {"gram": 0.0, "ceyrek": 0.0, "yarim": 0.0, "tam": 0.0}

altınlar = canlı_altın_fiyatları_hesapla()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="gold-card"><span style="color:#fbbf24; font-weight:bold; font-size:1.1rem;">✨ GRAM ALTIN</span><br><span style="font-size:1.6rem; font-weight:bold; color:#fff;">{formatla_tl(altınlar["gram"])} TL</span></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="gold-card"><span style="color:#fbbf24; font-weight:bold; font-size:1.1rem;">🟡 ÇEYREK ALTIN</span><br><span style="font-size:1.6rem; font-weight:bold; color:#fff;">{formatla_tl(altınlar["ceyrek"])} TL</span></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="gold-card"><span style="color:#fbbf24; font-weight:bold; font-size:1.1rem;">🟠 YARIM ALTIN</span><br><span style="font-size:1.6rem; font-weight:bold; color:#fff;">{formatla_tl(altınlar["yarim"])} TL</span></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="gold-card"><span style="color:#fbbf24; font-weight:bold; font-size:1.1rem;">👑 TAM ALTIN</span><br><span style="font-size:1.6rem; font-weight:bold; color:#fff;">{formatla_tl(altınlar["tam"])} TL</span></div>', unsafe_allow_html=True)

# 🔍 BIST CANLI HİSSE ARAMA MOTORU
st.write("---")
st.markdown('<div class="arama-baslik">🔍 BIST CANLI HİSSE ARAMA MOTORU</div>', unsafe_allow_html=True)
arama_kodu = st.text_input("Sorgulamak istediğiniz hisse kodunu yazın (Örn: THYAO, ASELS):", "").strip().upper()

if arama_kodu:
    with st.spinner(f"{arama_kodu} yükleniyor..."):
        try:
            hisse_bist = yf.Ticker(f"{arama_kodu}.IS")
            bist_data = hisse_bist.history(period="5d")
            if not bist_data.empty:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Anlık Fiyat 💰", f"{formatla_tl(bist_data['Close'].iloc[-1])} TL")
                c2.metric("Günün En Yükseği 📈", f"{formatla_tl(bist_data['High'].iloc[-1])} TL")
                c3.metric("Günün En Düşüğü 📉", f"{formatla_tl(bist_data['Low'].iloc[-1])} TL")
                c4.metric("İşlem Hacmi 📊", "{:,.0f}".format(bist_data['Volume'].iloc[-1]).replace(",", "."))
                st.line_chart(bist_data['Close'])
            else:
                st.error("Veri bulunamadı. Lütfen kodu kontrol edin.")
        except:
            st.error("Bağlantı hatası oluştu.")

# 📊 EXCEL OKUMA VE ANALİZ ALANI
st.write("---")
excel_yolu = "nurican.xls.xlsm"

if not os.path.exists(excel_yolu):
    st.warning(f"'{excel_yolu}' dosyası sistemde bulunamadı.")
else:
    df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    tablo_alsat = []
    tablo_al = []
    
    for idx in range(2, len(df_kaynak)):
        if len(df_kaynak.columns) > 22:
            u_hücre = df_kaynak.iloc[idx, 20]
            w_hücre = df_kaynak.iloc[idx, 22]
            excel_maliyet = df_kaynak.iloc[idx, 17]
            bta_puan_r = str(df_kaynak.iloc[idx, 19]).strip() if not pd.isna(df_kaynak.iloc[idx, 19]) else "Mevcut"
            
            maliyet_fiyat = 0.0
            try:
                if excel_maliyet and not pd.isna(excel_maliyet):
                    maliyet_fiyat = float(excel_maliyet)
            except:
                pass
                
            hisse_uv, puan_uv = hücre_parçala(u_hücre)
            if hisse_uv:
                fiyat_uv = hizli_fiyat_al(hisse_uv)
                kar_zarar_uv = "Hesaplanamadı"
                if maliyet_fiyat > 0 and fiyat_uv > 0:
                    oran = ((fiyat_uv - maliyet_fiyat) / maliyet_fiyat) * 100
                    kar_zarar_uv = formatla_yuzde(oran)
                tablo_alsat.append({
                    "Hisse Kodu 📈": hisse_uv,
                    "BTA Puan": bta_puan_r,
                    "Maliyet Fiyat": formatla_tl(maliyet_fiyat) if maliyet_fiyat > 0 else "Belirtilmedi",
                    "💥 Canlı Fiyat": f"{formatla_tl(fiyat_uv)} TL" if fiyat_uv > 0 else "Yükleniyor...",
                    "Kâr / Zarar 📊": kar_zarar_uv
                })
                
            hisse_wv, puan_wv = hücre_parçala(w_hücre)
            if hisse_wv:
                fiyat_wv = hizli_fiyat_al(hisse_wv)
