import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os, re
import time

# 1. Sayfa Yapılandırması ve Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('<style>.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important; font-family: "Segoe UI", sans-serif;} input {color: #000!important; background-color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} div.block-container {padding-top: 1rem; padding-bottom: 0.5rem;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; margin-top: 30px; margin-bottom: 20px; color: #fca5a5 !important; font-size: 0.95rem; text-align: justify; line-height: 1.5;} .bta-logo-konteyner {display: flex; justify-content: center; align-items: center; margin-top: 25px; margin-bottom: 35px; width: 100%;} .bta-logo {font-family: "Brush Script MT", "Comic Sans MS", cursive, sans-serif !important; font-weight: bold; font-size: 5.5rem; padding: 10px 50px; background: transparent; background-image: linear-gradient(45deg, #ff007f, #ff00ff, #8b00ff, #0000ff, #00ffff, #00ff00, #ffff00, #ff7f00, #ff0000); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 20px rgba(255, 0, 255, 0.8), 0 0 40px rgba(0, 255, 255, 0.6), 4px 4px 10px rgba(0, 0, 0, 0.9); display: inline-block; text-align: center; letter-spacing: 5px;} div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {font-size: 1.25rem !important; font-weight: bold !important; color: #ffffff !important;} .piyasa-kutusu {background: rgba(255, 255, 255, 0.05); border: 1px solid #eab308; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;} .haber-kutusu {background: rgba(255, 255, 255, 0.03); border-left: 4px solid #10b981; padding: 12px; border-radius: 6px; margin-bottom: 10px;}</style>', unsafe_allow_html=True)

# Hafıza Sabitleme
if "ozel_takip_kutusu" not in st.session_state: st.session_state["ozel_takip_kutusu"] = {}
if "fiyat_hafizasi" not in st.session_state: st.session_state["fiyat_hafizasi"] = {}

# 💥 BTA BÜYÜK EL YAZISI IŞIKLI LOGO ALANI
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

# 🌐  HİSSELERİ  SORGULA
st.markdown('<div class="alsat-baslik">🔎 BİST TÜM HİSSELER CANLI SORGULAMA MOTORU</div>', unsafe_allow_html=True)
arama_hisse = st.text_input("Canlı Fiyatını Görmek İstediğiniz Hisse Kodunu Girin (Örn: THYAO, EREGL, ASELS):", value="THYAO").strip().upper()

if arama_hisse:
    canli_fiyat = hızlı_canli_fiyat_bul(arama_hisse)
    if canli_fiyat > 0:
        tablo_arama = [{"Hisse Kodu 🔍": arama_hisse, "Durum": "Aktif / BIST", "💥 İnternet Canlı": f"{canli_fiyat:.2f} TL"}]
        st.dataframe(pd.DataFrame(tablo_arama), use_container_width=True, hide_index=True)
    else:
        st.error(f"❌ {arama_hisse} kodlu hisse verisi yfinance üzerinden alınamadı veya kod hatalı. Lütfen kontrol edin.")
st.write("")

# ALTIN PANELİ
st.markdown("#### 🟡 Canlı Altın Fiyatları")
p_gram, p_ceyrek, p_yarim, p_tam = canli_altin_fiyatlarini_hesapla()
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="piyasa-kutusu">🔱 GRAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_gram:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
c2.markdown(f'<div class="piyasa-kutusu">🪙 ÇEYREK ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_ceyrek:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
c3.markdown(f'<div class="piyasa-kutusu">🥈 YARIM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_yarim:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
c4.markdown(f'<div class="piyasa-kutusu">🥇 TAM ALTIN<br><span style="color:#eab308; font-size:1.4rem;">{p_tam:,.2f} TL</span></div>'.replace(',', '.').replace('._', ','), unsafe_allow_html=True)
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
            # Excel H sütunundan (7. indeks) maliyet fiyatını al
            h_sutunu_fiyati = df_kaynak.iloc[idx, 7] if len(df_kaynak.columns) > 7 else 0
            try:
                temiz_puan = float(str(h_sutunu_fiyati).replace(',', '.')) if pd.notna(h_sutunu_fiyati) else 0.0
            except:
                temiz_puan = 0.0

            if len(df_kaynak.columns) > 22:
                uv = str(df_kaynak.iloc[idx, 20]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 20]) else ""
                wv = str(df_kaynak.iloc[idx, 22]).strip().upper() if not pd.isna(df_kaynak.iloc[idx, 22]) else ""
                
                if uv and uv not in ["NAN", "NONE", "AL_SAT SİNYALİ"]:
                    h_ara = re.findall(r'[A-Z]+', uv)
                    if h_ara:
                        hisse = str(h_ara[0]).strip() # 🛠️ PARANTEZLER KESİN OLARAK SİLİNDİ
                        cfiy = hızlı_canli_fiyat_bul(hisse)
                        tablo_alsat.append({"Hisse Kodu 📈": hisse, "BTA Puan Fiyatı": f"{temiz_puan:.2f} TL", "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor..."})
                        
                if wv and wv not in ["NAN", "NONE", "AL", "SİNYALİ"]:
                    h_ara = re.findall(r'[A-Z]+', wv)
                    if h_ara:
                        hisse = str(h_ara[0]).strip() # 🛠️ PARANTEZLER KESİN OLARAK SİLİNDİ
                        cfiy = hızlı_canli_fiyat_bul(hisse)
                        
                        if temiz_puan > 0 and cfiy > 0:
                            kz_oran = ((cfiy - temiz_puan) / temiz_puan) * 100
                            kz_str = f"% {kz_oran:+.2f}"
                        else: 
                            kz_str = "% 0.00"

                        if hisse not in st.session_state["ozel_takip_kutusu"] and cfiy > 0:
                            st.session_state["ozel_takip_kutusu"][hisse] = {"kayit_fiyati": cfiy, "kayit_zamani": guncel_an}
                        
                        tablo_al.append({
                            "Hisse Kodu 🚀": hisse, 
                            "BTA Sinyal Fiyatı": f"{temiz_puan:.2f} TL", 
                            "💥 İnternet Canlı": f"{cfiy:.2f} TL" if cfiy > 0 else "Yükleniyor...",
                            "Kâr / Zarar (%) 📈": kz_str
                        })
        except: pass

st.markdown('<div class="alsat-baslik">🟡 DÖNEMSEL AL SAT SİNYALLERİ</div>', unsafe_allow_html=True)
if tablo_alsat: st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
else: st.write("🔒 Aktif AL SAT sinyali taranıyor...")

st.markdown('<div class="al-baslik">🟢 BTA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
if tablo_al: st.dataframe(pd.DataFrame(tablo_al), use_container_width=True, hide_index=True)
else: st.write("🔒 Aktif BTA sinyali taranıyor...")

# 🌟 ÖZEL TAKİP HAVUZU PANELİ
if st.session_state["ozel_takip_kutusu"]:
    st.markdown("#### 🌟 Özel Takip Havuzu 💰")
    tk_list = []
    for hisse, bilge in list(st.session_state["ozel_takip_kutusu"].items()):
        cfiy = hızlı_canli_fiyat_bul(hisse)
        if cfiy == 0.0: cfiy = bilge["kayit_fiyati"]
        
        maliyet = bilge['kayit_fiyati']
        if maliyet > 0:
            kar_zarar_yuzde = ((cfiy - maliyet) / maliyet) * 100
            kar_zarar_str = f"% {kar_zarar_yuzde:+.2f}"
        else:
            kar_zarar_str = "% 0.00"
            
        tk_list.append({
            "Hisse Kodu 🗝️": hisse, 
            "Havuz Maliyeti": f"{maliyet:.2f} TL", 
            "Anlık Güncel": f"{cfiy:.2f} TL",
            "Kâr / Zarar (%)": kar_zarar_str,
            "Eklenme Zamanı 📅": bilge.get("kayit_zamani", guncel_an)
        })
# SPK KUTUSU
st.markdown("""
<div class="spk-kutusu">
    <b>⚖️ YASAL UYARI (SPK):</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı 
    kapsamında değildir. Yatırım danışmanlığı hizmeti; aracı kurumlar, portföy şirketleri, 
    mevduat kabul etmeyen bankalar ile müşteri arasında imzalanacak yatırım danışmanlığı sözleşmesi 
    çerçevesinde sunulmaktadır. Burada yer alan yorum ve tavsiyeler, yorum ve tavsiyede bulunanların 
    kişisel görüşlerine dayanmaktadır. Bu görüşler mali durumunuz ile risk ve getiri tercihlerinize 
    uygun olmayabilir. Veriler en az 15 dakika gecikmelidir.
</div>
""", unsafe_allow_html=True)
