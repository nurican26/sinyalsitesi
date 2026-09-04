import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Yasal Risklerden Uzak Analitik Tasarım
st.set_page_config(page_title="BTA Veri Analizi", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .istatistik-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .analiz-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .performans-baslik {background: linear-gradient(90deg, #06b6d4 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .bta-logo-konteyner {display: flex; align-items: center; margin-top: 15px; margin-bottom: 25px;} .bta-logo {background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white !important; font-family: "Segoe UI", sans-serif !important; font-weight: bold; font-size: 2.2rem; padding: 4px 25px; border-radius: 12px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.05); border: 1px solid #eab308; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;} .haber-kutusu {background: rgba(255, 255, 255, 0.03); border-left: 4px solid #10b981; padding: 12px; border-radius: 6px; margin-bottom: 10px;}</style>', unsafe_allow_html=True)

# Hafıza Sabitleme
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
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
        return st.session_state["fiyat_hafizasi"][hisse_kodu][1]
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
c1.markdown(f'<div class="piyasa-kutusu">🔱 REF. GRAM<br><span style="color:#eab308; font-size:1.4rem;">{p_gram:,.2f} TL</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="piyasa-kutusu">🪙 REF. ÇEYREK<br><span style="color:#eab308; font-size:1.4rem;">{p_ceyrek:,.2f} TL</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="piyasa-kutusu">🥈 REF. YARIM<br><span style="color:#eab308; font-size:1.4rem;">{p_yarim:,.2f} TL</span></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="piyasa-kutusu">🥇 REF. TAM<br><span style="color:#eab308; font-size:1.4rem;">{p_tam:,.2f} TL</span></div>', unsafe_allow_html=True)
st.write("")

# 📰 MAKROEKONOMİK GÖSTERGELER
st.markdown("#### 📰 Makroekonomik Bülten Akışı")
st.markdown('<div class="haber-kutusu">📊 <b>Endeks İzleme Modülü:</b> Yurtiçi ve yurtdışı pazarlardaki matematiksel fiyat hareketleri analitik veri modelleriyle takip edilmektedir.</div>', unsafe_allow_html=True)
st.markdown('<div class="haber-kutusu">🌟 <b>Emtia İstatistikleri:</b> Ons ve döviz kurları korelasyonu matematiksel standartlarda veri tabanına işlenmektedir.</div>', unsafe_allow_html=True)
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
                
                # 🟡 DÖNEMSEL İSTATİSTİKLER (Eski Dönemsel Al Sat)
                if uv and uv not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                    h_ara = re.findall(r'[A-Z]+', uv)
                    if h_ara:
                        hisse = str(h_ara[0]).strip() # Kesin düz metin
                        if 4 <= len(hisse) <= 5 and hisse not in ["NONE", "NAN", "SINYAL"]:
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', uv)
                            bta_puan = p_bul[0] if p_bul else t_deg
                            tablo_alsat.append({"Varlık Kodu 📈": hisse, "Matematiksel Puan": bta_puan, "Anlık Fiyat": f"{cfiy:.2f} TL" if cfiy > 0 else "Hesaplanıyor..."})
                        
                # 🟢 BTA MATEMATİKSEL MODELLEME (Eski BTA Sinyal Merkezi)
                if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                    h_ara = re.findall(r'[A-Z]+', wv)
                    if h_ara:
                        hisse = str(h_ara[0]).strip() # Kesin düz metin
                        if 4 <= len(hisse) <= 5 and hisse not in ["NONE", "NAN", "SINYAL"]:
                            cfiy = hızlı_canli_fiyat_bul(hisse)
                            p_bul = re.findall(r'[-+]?\d*,\d+|[-+]?\d*\.\d+|\d+', wv)
                            bta_puan = p_bul[0] if p_bul else t_deg
                            
                            # Her zaman bu tabloda düz yazı olarak listelensin
                            tablo_al.append({"Varlık Kodu 🚀": hisse, "Matematiksel Puan": bta_puan, "Anlık Fiyat": f"{cfiy:.2f} TL" if cfiy > 0 else "Hesaplanıyor..."})
                            
                            # Canlı Veri İzleme Paneline (Takip Havuzuna) kaydet
                            if hisse not in st.session_state["ozel_takip_kutusu"] and cfiy > 0:
                                st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
        except: pass

# --- YENİLENEN BAŞLIKLARLA EKRANA BASMA ---

# 1. Eski Dönemsel Al Sat
st.markdown('<div class="istatistik-baslik">🟡 DÖNEMSEL VARLIK İSTATİSTİKLERİ</div>', unsafe_allow_html=True)
if tablo_alsat: 
    st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
else: 
    st.write("⏳ Veri matrisi taranıyor...")

# 2. Eski BTA Sinyal Merkezi
st.markdown('<div class="analiz-baslik">🟢 BTA MATEMATİKSEL VERİ MODELLEMESİ</div>', unsafe_allow_html=True)
if tablo_al: 
    st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
else: 
    st.write("⏳ Matematiksel model taranıyor...")

# 3. Eski BTA Canlı Takip Paneli
st.markdown('<div class="performans-baslik">🔵 ANLIK VERİ İZLEME VE PERFORMANS MODÜLÜ</div>', unsafe_allow_html=True)
takip_listesi = []

if st.session_state["ozel_takip_kutusu"]:
    for hisse, veri in list(st.session_state["ozel_takip_kutusu"].items()):
        guncel_fiy = hızlı_canli_fiyat_bul(hisse)
        if guncel_fiy > 0:
            maliyet = veri["kayit_fiyati"]
            degisim = ((guncel_fiy - maliyet) / maliyet) * 100
            
            yeni_satir = {}
            yeni_satir["Varlık Tipi"] = hisse
            yeni_satir["Başlangıç Değeri (Sabit)"] = f"{maliyet:.2f} TL"
            yeni_satir["Anlık Güncel Değer"] = f"{guncel_fiy:.2f} TL"
            yeni_satir["Fiyat Değişim Oranı"] = f"{degisim:+.2f}%"
            yeni_satir["Sisteme Giriş Dönemi"] = veri["kayit_zamani"]
            
            takip_listesi.append(yeni_satir)

if takip_listesi:
    st.dataframe(pd.DataFrame(takip_listesi), use_container_width=True, hide_index=True)
else:
    st.write("📂 İzleme modülünde aktif matematiksel veri bulunmuyor.")

st.write("---")
# ⚖️ MUTLAK SABİT YASAL UYARI KUTUSU (Sayfanın en altında kusursuzca parlar)
st.write("---")
st.markdown('<div class="spk-kutusu"><b>⚖️ YASAL UYARI (SPK):</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy yönetim şirketleri, mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların kişisel görüşlerine dayanmaktadır. Bu tavsiyeler mali durumunuz ile risk ve getiri tercihlerinize uygun olmayabilir. Bu nedenle, sadece burada yer alan bilgilere dayanılarak yatırım kararı verilmesi beklentilerinize uygun sonuçlar doğurmayabilir. Veriler borsa standartlarında en az 15 dakika gecikmelidir.</div>', unsafe_allow_html=True)

