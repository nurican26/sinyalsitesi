import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Telefon Uyumlu Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# Google Fonts'tan şık bir el yazısı (Caveat) yazı tipi eklendi
st.markdown('<link href="https://googleapis.com" rel="stylesheet">', unsafe_allow_html=True)

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; margin-top: 30px; margin-bottom: 20px; color: #fca5a5 !important; font-size: 0.95rem; text-align: justify; line-height: 1.5;} .bta-logo-konteyner {display: flex; align-items: center; margin-top: 15px; margin-bottom: 25px;} .bta-logo {background: transparent !important; color: #10b981 !important; font-family: "Caveat", cursive !important; font-weight: bold; font-size: 4rem; padding: 0px; text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9), 0 0 20px rgba(16, 185, 129, 0.6); box-shadow: none !important;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.05); border: 1px solid #eab308; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;}</style>', unsafe_allow_html=True)

# Hafıza Sabitleme
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

# LOGO (Şeffaf Arka Plan, El Yazısı, Gölgeli)
st.markdown('<div class="bta-logo-konteyner"><div class="bta-logo">BTA</div></div>', unsafe_allow_html=True)

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

# 🟢 VERİLER VE TABLOLAR DOĞRUDAN YÜKLENİR
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px;">🕒 {guncel_an}</div>', unsafe_allow_html=True)

# ALTIN PANELİ
st.markdown("#### 🟡 Canlı Altın Fiyatları")
p_gram, p_ceyrek, p_yarim, p_tam = canli_altin_fiyatlarini_hesapla()
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="piyasa-kutusu">🔱 GRAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_gram:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
c2.markdown(f'<div class="piyasa-kutusu">🪙 ÇEYREK ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_ceyrek:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
c3.markdown(f'<div class="piyasa-kutusu">🥈 YARIM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_yarim:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
c4.markdown(f'<div class="piyasa-kutusu">🥇 TAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_tam:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
st.write("")

# 🔍 BİST ARAMA MOTORU SİSTEMİ
st.markdown("#### 🔍 BİST Canlı Fiyat Arama")
arama_kodu = st.text_input("Hisse Kodu Giriniz (Örn: THYAO, ASELS):", "").strip().upper()
if arama_kodu:
    anlik_fiy = hızlı_canli_fiyat_bul(arama_kodu)
    if anlik_fiy > 0:
        st.success(f"📈 {arama_kodu} Güncel Canlı Fiyatı: **{anlik_fiy:.2f} TL**")
    else:
        st.error("Hisse bulunamadı veya veri çekilemedi. Lütfen kodu kontrol edin.")

st.write("---")

# 🔍 ARKA PLANDA EXCEL VERİSİNİ OKUMA
df_kaynak = None
excel_yolu = "nurican.xls.xlsm"
if os.path.exists(excel_yolu):
    try: df_kaynak = pd.read_excel(excel_yolu, header=None, engine="openpyxl")
    except: pass

tablo_alsat, tablo_al = [], []
if df_kaynak is not None:
    for idx in range(2, len(df_kaynak)):
        try:
            # Excel yapısının yeterli sütuna sahip olduğundan emin oluyoruz
            if len(df_kaynak.columns) > 22:
                # Sütun İndeksleri: R=17, T=19, U=20, W=22
                bta_puan_raw = str(df_kaynak.iloc[idx, 17]).strip() if not pd.isna(df_kaynak.iloc[idx, 17]) else "0"
                uv = str(df_kaynak.iloc[idx, 20]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 20]) else ""
                wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 22]) else ""
                t_deg = str(df_kaynak.iloc[idx, 19]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 19]) else ""
                
                # Kar-Zarar hesaplaması için Excel'deki T sütununu (19. indeks) maliyet/anlık fiyat kabul ediyoruz
                try: excel_maliyet = float(t_deg.replace(",", ".")) if t_deg else 0.0
                except: excel_maliyet = 0.0

                if uv and uv not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                    h_ara = re.findall(r'[A-Z]+', uv)
                    if h_ara:
                        hisse = str(h_ara[0]).strip()
                        cfiy = hızlı_canli_fiyat_bul(hisse)
                        
                        # Kar/Zarar Oranı Hesaplama
                        kz_oran = 0.0
                        if excel_maliyet > 0 and cfiy > 0:
                            kz_oran = ((cfiy - excel_maliyet) / excel_maliyet) * 100
                        
                        tablo_alsat.append({
                            "Hisse Kodu 📈": hisse, 
                            "BTA Puan": bta_puan_raw, 
                            "💵 Excel Maliyet": f"{excel_maliyet:.2f} TL" if excel_maliyet > 0 else "-",
                            "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor...",
                            "📊 Kar/Zarar (%)": f"%{kz_oran:+.2f}" if excel_maliyet > 0 and cfiy > 0 else "-"
                        })
                        
                if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                    h_ara = re.findall(r'[A-Z]+', wv)
                    if h_ara:
                        hisse = str(h_ara[0]).strip()
                        cfiy = hızlı_canli_fiyat_bul(hisse)
                        
                        # Kar/Zarar Oranı Hesaplama
                        kz_oran = 0.0
                        if excel_maliyet > 0 and cfiy > 0:
                            kz_oran = ((cfiy - excel_maliyet) / excel_maliyet) * 100

                        if hisse not in st.session_state["ozel_takip_kutusu"] and cfiy > 0:
                            st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                        
                        tablo_al.append({
                            "Hisse Kodu 🚀": hisse, 
                            "BTA Puan": bta_puan_raw, 
                            "💵 Excel Maliyet": f"{excel_maliyet:.2f} TL" if excel_maliyet > 0 else "-",
                            "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor...",
                            "📊 Kar/Zarar (%)": f"%{kz_oran:+.2f}" if excel_maliyet > 0 and cfiy > 0 else "-"
                        })
        except: pass

# 🟢 BTA SİNYAL MERKEZİ EN ÜSTE LİSTELENİR
st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
if tablo_al: st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
else: st.write("🔒 Aktif Al sinyali taranıyor...")

st.markdown('<div class="alsat-baslik">🟡  AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
if tablo_alsat: st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
else: st.write("🔒 Aktif AL SAT sinyali taranıyor...")

# Yasal Uyarı Kutusu
st.markdown('<div class="spk-kutusu">⚠️ <b>YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeler yatırım danışmanlığı kapsamında değildir. Sıra listeler otomatik formüllerle üretilmektedir.</div>', unsafe_allow_html=True)
