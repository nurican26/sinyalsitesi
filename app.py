import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time
from streamlit_autorefresh import st_autorefresh

# Sayfa Yapılandırması
st.set_page_config(page_title="Canlı Hisse Takip Programı", layout="wide")

# 🔄 CANLI FİYAT VE ANIMASYON KİLİDİ: Sayfa her 10 saniyede bir otomatik yenilenir
st_autorefresh(interval=10 * 1000, key="hisse_canli_yenileyici")

# Her yenilemede animasyonu baştan oynatmak için zaman damgası
anim_id = int(time.time())

# 📱 TELEFON VE MOBİL UYUMLU ŞIK NEON TASARIM CSS KODLARI
st.markdown(f'''
<style>
    .stApp {{background: #0f172a!important; padding: 0.25rem;}} 
    h1,h2,h3,h4,h5,h6,p,span,label {{color: #fff!important;}} 
    
    .stDataFrame {{
        width: 100% !important; 
        border: 1px solid #10b981 !important; 
        border-radius: 8px;
        overflow-x: auto !important;
    }} 
    
    /* Canlı Piyasa Bilgi Kutuları CSS */
    .piyasa-kutusu-konteyner {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 20px;
        justify-content: center;
    }}
    .piyasa-kart {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #ca8a04;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        flex: 1 1 180px;
        max-width: 220px;
    }}
    .piyasa-kart-bist {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        flex: 1 1 180px;
        max-width: 220px;
    }}
    .piyasa-baslik {{ font-size: 0.85rem; color: #cbd5e1; font-weight: bold; margin-bottom: 4px; }}
    .piyasa-deger {{ font-size: 1.25rem; color: #eab308; font-weight: bold; }}
    .piyasa-deger-bist {{ font-size: 1.25rem; color: #10b981; font-weight: bold; }}

    .alsat-baslik {{
        background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); 
        padding: 8px; 
        border-radius: 5px; 
        font-weight: bold; 
        margin-bottom: 5px; 
        color:#fff;
        font-size: 1.1rem;
    }} 
    .al-baslik {{
        background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); 
        padding: 8px; 
        border-radius: 5px; 
        font-weight: bold; 
        margin-bottom: 5px; 
        color:#fff;
        font-size: 1.1rem;
    }} 
    
    /* Sağ Köşedeki Yeni Uyarı Yazısı Tasarımı */
    .ytd-yazi {{
        text-align: right;
        color: #fca5a5 !important;
        font-size: 0.9rem;
        font-weight: bold;
        margin-top: 40px;
        margin-bottom: 20px;
        padding-right: 10px;
        letter-spacing: 0.5px;
    }}
    
    .logo-konteyner {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 15px 0;
        margin-bottom: 5px;
    }}
    .cember-animasyon-{anim_id} {{
        width: 100px; 
        height: 100px;
        border: 4px solid #fff;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: transparent;
        position: relative;
        overflow: hidden;
        animation: 
            gokkusagiCember 4s linear infinite,
            yukardanDus 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }}
    .bta-yazi-{anim_id} {{
        font-family: 'Caveat', 'Segoe UI', cursive, sans-serif;
        font-size: 2.6rem; 
        font-weight: bold;
        margin: 0;
        padding: 0;
        z-index: 2;
        background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        filter: drop-shadow(0px 2px 6px rgba(255,255,255,0.3));
        animation: soldanYavascaKay 1.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }}
    
    @keyframes gokkusagiCember {{
        0% {{ border-color: #ff0000; box-shadow: 0 0 12px #ff0000, inset 0 0 12px #ff0000; }}
        14% {{ border-color: #ff7f00; box-shadow: 0 0 12px #ff7f00, inset 0 0 12px #ff7f00; }}
        28% {{ border-color: #ffff00; box-shadow: 0 0 12px #ffff00, inset 0 0 12px #ffff00; }}
        42% {{ border-color: #00ff00; box-shadow: 0 0 12px #00ff00, inset 0 0 12px #00ff00; }}
        56% {{ border-color: #00ffff; box-shadow: 0 0 12px #00ffff, inset 0 0 12px #00ffff; }}
        70% {{ border-color: #0000ff; box-shadow: 0 0 12px #0000ff, inset 0 0 12px #0000ff; }}
        84% {{ border-color: #8b00ff; box-shadow: 0 0 12px #8b00ff, inset 0 0 12px #8b00ff; }}
        100% {{ border-color: #ff0000; box-shadow: 0 0 12px #ff0000, inset 0 0 12px #ff0000; }}
    }}
    @keyframes yukardanDus {{ 0% {{ transform: translateY(-150px) scale(0.5); opacity: 0; }} 70% {{ transform: translateY(8px) scale(1.03); opacity: 1; }} 100% {{ transform: translateY(0) scale(1); opacity: 1; }} }}
    @keyframes soldanYavascaKay {{ 0% {{ transform: translateX(-110px); opacity: 0; }} 30% {{ opacity: 0.5; }} 100% {{ transform: translateX(0); opacity: 1; }} }}
</style>
''', unsafe_allow_html=True)

# 🌈 LOGO EKRAN ÇIKTISI
st.markdown(f'''
<div class="logo-konteyner">
    <div class="cember-animasyon-{anim_id}">
        <span class="bta-yazi-{anim_id}">BTA</span>
    </div>
</div>
''', unsafe_allow_html=True)

# 🕒 CANLI SAAT GÖSTERGESİ (Tarih yok)
guncel_saat = datetime.datetime.now().strftime("%H:%M:%S")
st.markdown(f'<div style="font-size: 1.1rem; color: #cbd5e1; margin-bottom: 20px; font-weight: bold; text-align:center;">🕒 Canlı Saat: {guncel_saat}</div>', unsafe_allow_html=True)

# 🟡 CANLI ALTIN VE BİST 100 MOTORU
def canli_piyasa_verilerini_hesapla():
    saf_gram, ceyrek, yarim, tam, bist_fiyat = 3025.00, 4950.00, 9900.00, 19800.00, 14000.00
    try:
        ons_ticker = yf.Ticker("GC=F").history(period="1d")
        usd_ticker = yf.Ticker("USDTRY=X").history(period="1d")
        bist_ticker = yf.Ticker("XU100.IS").history(period="1d")
        
        if not ons_ticker.empty and not usd_ticker.empty:
            ons_fiyat = float(ons_ticker['Close'].iloc[-1])
            usd_fiyat = float(usd_ticker['Close'].iloc[-1])
            saf_gram = (ons_fiyat / 31.10347) * usd_fiyat
            ceyrek = saf_gram * 1.635
            yarim = ceyrek * 2
            tam = ceyrek * 4
            
        if not bist_ticker.empty:
            bist_fiyat = float(bist_ticker['Close'].iloc[-1])
    except:
        pass
    return saf_gram, ceyrek, yarim, tam, bist_fiyat

p_gram, p_ceyrek, p_yarim, p_tam, p_bist = canli_piyasa_verilerini_hesapla()

# 📊 Canlı Piyasa Panel Çıktısı
st.markdown(f'''
<div class="piyasa-kutusu-konteyner">
    <div class="piyasa-kart"><div class="piyasa-baslik">🔱 GRAM ALTIN</div><div class="piyasa-deger">{p_gram:,.2f} TL</div></div>
    <div class="piyasa-kart"><div class="piyasa-baslik">🪙 ÇEYREK ALTIN</div><div class="piyasa-deger">{p_ceyrek:,.2f} TL</div></div>
    <div class="piyasa-kart"><div class="piyasa-baslik">🥈 YARIM ALTIN</div><div class="piyasa-deger">{p_yarim:,.2f} TL</div></div>
    <div class="piyasa-kart"><div class="piyasa-baslik">🥇 TAM ALTIN</div><div class="piyasa-deger">{p_tam:,.2f} TL</div></div>
    <div class="piyasa-kart-bist"><div class="piyasa-baslik">📈 BİST 100 ENDEKS</div><div class="piyasa-deger-bist">{p_bist:,.2f}</div></div>
</div>
''', unsafe_allow_html=True)
st.write("---")

excel_yolu = "nurican.xls.xlsm"

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        # 🔍 CANLI ARAMA MOTORU SİSTEMİ
        st.markdown("#### 🔍 BİST Canlı Fiyat Arama Motoru")
        hisse_havuzu = []
        if len(df.columns) >= 5:
            e_sutunu_temiz = df.iloc[:, 4].dropna().astype(str).str.strip().str.upper()
            hisse_havuzu = [h for h in e_sutunu_temiz if h not in ["", "NAN", "NONE", "HİSSE", "BTA HİSSE"]]
            hisse_havuzu = sorted(list(set(hisse_havuzu)))
        
        secilen_hisse = st.selectbox("Canlı verisini görmek istediğiniz hisseyi seçin:", ["Seçiniz..."] + hisse_havuzu)
        
        if secilen_hisse != "Seçiniz...":
            try:
                ticker_ara = yf.Ticker(f"{secilen_hisse}.IS")
                hist_ara = ticker_ara.history(period="2d")
                if not hist_ara.empty:
                    arama_canli_fiyat = float(hist_ara['Close'].iloc[-1])
                    onceki_kap = float(hist_ara['Close'].iloc[-2]) if len(hist_ara) >= 2 else arama_canli_fiyat
                    arama_degisim = ((arama_canli_fiyat - onceki_kap) / onceki_kap) * 100
                    st.success(f"📈 **{secilen_hisse}**: **{arama_canli_fiyat:.2f} TL** | **%{arama_degisim:+.2f}**")
                else:
                    st.warning("Veri çekilemedi.")
            except:
                st.error("Bağlantı hatası.")
        
        st.write("---")

        tablo_bta = []
        tablo_alsat = []
        sinir = min(10, len(df))
        
        for idx in range(sinir):
            # 1. ÜST PANEL VERİLERİ (A, C, D Sütunları)
            hisse_a = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]

            if hisse_a and hisse_a not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                try: 
                    puan_temiz = f"{float(puan_d):.2f}"
                except: 
                    puan_temiz = str(puan_d).strip() if pd.notna(puan_d) else ""

                canli_fiyat = 0.0
                try:
                    ticker = yf.Ticker(f"{hisse_a}.IS")
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        canli_fiyat = float(hist['Close'].iloc[-1])
                except:
                    pass
                
                try: 
                    maliyet = float(alim_c.replace(",", "."))
