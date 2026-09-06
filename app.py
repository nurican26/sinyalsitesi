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

# Şık Neon Tasarım, Gökkuşağı Çember, Yazı veinsanların gözünü yormayan Ticker CSS Yapısı
st.markdown(f'''
<style>
    .stApp {{background: #0f172a!important; padding: 0.5rem;}} 
    h1,h2,h3,h4,h5,h6,p,span,label {{color: #fff!important;}} 
    .stDataFrame {{width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;}} 
    .alsat-baslik {{background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    .al-baslik {{background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;}} 
    
    /* 📺 AKAR HABER BÜLTENİ BANTI CSS */
    .haber-banti-konteyner {{
        background: rgba(255, 255, 255, 0.03);
        border-top: 1px solid #ca8a04;
        border-bottom: 1px solid #10b981;
        overflow: hidden;
        white-space: nowrap;
        padding: 10px 0;
        margin-top: 10px;
        margin-bottom: 25px;
    }}
    .haber-akisi {{
        display: inline-block;
        padding-left: 100%;
        animation: haberKaydir 25s linear infinite;
        font-size: 1.2rem;
        font-weight: bold;
        color: #fff;
    }}
    .haber-item {{
        display: inline-block;
        margin-right: 50px;
    }}
    .altin-vurgu {{ color: #eab308; }}
    .bist-vurgu {{ color: #10b981; }}
    
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

    /* 🌈 ANIMASYONLU GÖKKUŞAĞI ÇEMBER VE KAYAN BTA LOGO ALANI */
    .logo-konteyner {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px 0;
        margin-bottom: 10px;
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
    @keyframes haberKaydir {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-100%); }} }}
</style>
''', unsafe_allow_html=True)

# LOGO EKRAN ÇIKTISI
st.markdown(f'''
<div class="logo-konteyner">
    <div class="cember-animasyon-{anim_id}">
        <span class="bta-yazi-{anim_id}">BTA</span>
    </div>
</div>
''', unsafe_allow_html=True)

# Zaman Düzenlemesi (Sizin ellerinizle sildiğiniz temiz düzen)
st.markdown(f'<div style="font-size: 1.1rem; color: #cbd5e1; margin-bottom: 15px; font-weight: bold; text-align: center;"><span style="color:#10b981; font-size:0.9rem;">(10sn de bir otomatik yenileniyor)</span></div>', unsafe_allow_html=True)

# 🟡 CANLI ALTIN VE BİST 100 MOTORU
def canli_piyasa_verilerini_hesapla():
    saf_gram, ceyrek, yarim, tam, bist_fiyat = 3025.00, 4950.00, 9900.00, 19800.00, 14000.00
    try:
        piyasa_data = yf.download("GC=F USDTRY=X XU100.IS", period="2d", progress=False, group_by="ticker")
        if "GC=F" in piyasa_data and "USDTRY=X" in piyasa_data:
            ons_fiyat = float(piyasa_data["GC=F"]["Close"].dropna().iloc[-1])
            usd_fiyat = float(piyasa_data["USDTRY=X"]["Close"].dropna().iloc[-1])
            saf_gram = (ons_fiyat / 31.10347) * usd_fiyat
            ceyrek = saf_gram * 1.635
            yarim = ceyrek * 2
            tam = ceyrek * 4
        if "XU100.IS" in piyasa_data:
            bist_fiyat = float(piyasa_data["XU100.IS"]["Close"].dropna().iloc[-1])
    except:
        pass
    return saf_gram, ceyrek, yarim, tam, bist_fiyat

p_gram, p_ceyrek, p_yarim, p_tam, p_bist = canli_piyasa_verilerini_hesapla()

sg_txt = f"{p_gram:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
cy_txt = f"{p_ceyrek:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
yr_txt = f"{p_yarim:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
tm_txt = f"{p_tam:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
bi_txt = f"{p_bist:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# 📺 BTA LOGOSUNUN ALTINDAN GEÇEN NEON AKAR HABER BÜLTENİ BANTI ÇIKTISI
st.markdown(f'''
<div class="haber-banti-konteyner">
    <div class="haber-akisi">
        <span class="haber-item">🔱 <span class="altin-vurgu">GRAM ALTIN:</span> {sg_txt} TL</span>
        <span class="haber-item">🪙 <span class="altin-vurgu">ÇEYREK ALTIN:</span> {cy_txt} TL</span>
        <span class="haber-item">🥈 <span class="altin-vurgu">YARIM ALTIN:</span> {yr_txt} TL</span>
        <span class="haber-item">🥇 <span class="altin-vurgu">TAM ALTIN:</span> {tm_txt} TL</span>
        <span class="haber-item">📈 <span class="bist-vurgu">BİST 100 ENDEKS:</span> {bi_txt} TL</span>
    </div>
</div>
''', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

if os.path.exists(excel_yolu):
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
        hist_ara = yf.download(f"{secilen_hisse}.IS", period="2d", progress=False)
        if not hist_ara.empty:
            arama_canli_fiyat = float(hist_ara['Close'].dropna().iloc[-1])
            onceki_kap = float(hist_ara['Close'].dropna().iloc[-2]) if len(hist_ara) >= 2 else arama_canli_fiyat
            arama_degisim = ((arama_canli_fiyat - onceki_kap) / onceki_kap) * 100
            st.success(f"📈 **{secilen_hisse}** Anlık Canlı Fiyatı: {arama_canli_fiyat:.2f} TL | Günlük Değişim: %{arama_degisim:+.2f}")

    st.write("---")

    # ⚡ TOPLU VERİ İNDİRME ADIMI (Hata riskini sıfırlayan bağımsız blok)
    sinir = min(10, len(df))
    ust_kodlar = []
    alt_kodlar = []
    
    for idx in range(sinir):
        h_a = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
        h_b = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
        if h_a and h_a not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
            ust_kodlar.append(h_a)
        if h_b and h_b not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
            alt_kodlar.append(h_b)
            
    tum_liste = list(set(ust_kodlar + alt_kodlar))
    canli_havuz = {}
    
    if tum_liste:
        indirme_metni = " ".join([f"{k}.IS" for k in tum_liste])
        toplu_data = yf.download(indirme_metni, period="2d", progress=False, group_by="ticker")
        for k in tum_liste:
            is_kodu = f"{k}.IS"
            if is_kodu in toplu_data:
                sub_df = toplu_data[is_kodu].dropna()
                if not sub_df.empty:
                    s_f = float(sub_df["Close"].iloc[-1])
                    o_f = float(sub_df["Close"].iloc[-2]) if len(sub_df) >= 2 else s_f
                    canli_havuz[k] = {"son": s_f, "onceki": o_f}

    tablo_bta = []
    tablo_alsat = []
    
    for idx in range(sinir):
