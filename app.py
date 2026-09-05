import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os

# 1. Sayfa Yapılandırması ve TELEFON / MOBİL FORMAT UYUMU
st.set_page_config(page_title="BTA", page_icon="📈", layout="centered")

st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important; 
        color: #ffffff !important;
    }
    
    /* Yeni Geliştirilmiş Yuvarlak BTA ve Yörüngede Dönen Yıldızlar */
    .bta-cerceve-alani {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 25px;
        padding: 10px;
    }
    
    .bta-yuvarlak-wrapper {
        position: relative;
        width: 150px;
        height: 150px;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* Yıldızların Döneceği Dış Yörünge Çemberi */
    .yildiz-rotator {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        animation: spinYildiz 8s linear infinite;
    }

    /* Çember Çizgisi Üzerindeki Yıldızlar */
    .yildiz-item {
        position: absolute;
        font-size: 20px;
        color: #f1c40f;
        text-shadow: 0 0 10px #f1c40f;
    }
    .yildiz-1 { top: 0; left: 50%; transform: translateX(-50%); }
    .yildiz-2 { bottom: 0; left: 50%; transform: translateX(-50%); }
    .yildiz-3 { left: 0; top: 50%; transform: translateY(-50%); }
    .yildiz-4 { right: 0; top: 50%; transform: translateY(-50%); }

    /* İçerideki Sabit Yuvarlak BTA Kutusu */
    .bta-yuvarlak-box {
        width: 110px;
        height: 110px;
        background: rgba(15, 23, 42, 0.95);
        border-radius: 50%;
        border: 3px solid #f1c40f;
        box-shadow: 0 0 15px rgba(241, 196, 15, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 5;
    }
    
    .bta-yazi {
        font-family: 'Caveat', cursive !important;
        font-size: 38px !important;
        color: #f1c40f !important;
        font-weight: 700;
        text-align: center;
        margin: 0;
    }
    
    @keyframes spinYildiz {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Büyük ve Kendiliğinden Kayan Canlı Altın Bandı */
    .altin-bandi-konteyner {
        background-color: rgba(30, 41, 59, 0.9);
        border: 2px solid #f1c40f;
        box-shadow: 0 0 10px rgba(241, 196, 15, 0.3);
        border-radius: 10px;
        padding: 12px 5px;
        margin-bottom: 25px;
        overflow: hidden;
    }
    
    .altin-kayan-yazi {
        font-size: 16px !important;
        font-weight: bold;
        color: #f1c40f;
    }
    
    .altin-val { 
        color: #ffffff !important; 
        margin-right: 25px;
        background: rgba(255,255,255,0.1);
        padding: 2px 8px;
        border-radius: 5px;
    }
    
    .stDataFrame, div[data-testid="stTable"] { color: #ffffff !important; }
    h3, h4, p, span, label { color: #ffffff !important; }
    
    .alt-baslik-bta { border-left: 5px solid #f1c40f; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; font-weight: 600; color: #f1c40f !important; font-size: 17px; }
    .alt-baslik-alsat { border-left: 5px solid #00d2ff; padding-left: 8px; margin-top: 20px; margin-bottom: 8px; font-weight: 600; color: #00d2ff !important; font-size: 17px; }
</style>

<div class="bta-cerceve-alani">
    <div class="bta-yuvarlak-wrapper">
        <!-- Dönen Yıldızlar Yörüngesi -->
        <div class="yildiz-rotator">
            <span class="yildiz-item yildiz-1">★</span>
            <span class="yildiz-item yildiz-2">★</span>
            <span class="yildiz-item yildiz-3">★</span>
            <span class="yildiz-item yildiz-4">★</span>
        </div>
        <!-- Sabit İç Yuvarlak -->
        <div class="bta-yuvarlak-box">
            <h1 class="bta-yazi">BTA</h1>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Hızlandırılmış Canlı Altın Fiyatları (Önbellekli Hızlı İstek)
@st.cache_data(ttl=600)
def canli_altin_fiyatlari():
    try:
        data = yf.download(tickers=["GC=F", "TRY=X"], period="1d", group_by='ticker', progress=False)
        ons_gold = data["GC=F"]["Close"].iloc[-1]
        usd_try = data["TRY=X"]["Close"].iloc[-1]
        
        gram_hesap = (ons_gold / 31.1034768) * usd_try
        ceyrek_hesap = gram_hesap * 1.634
        yarim_hesap = ceyrek_hesap * 2
        tam_hesap = ceyrek_hesap * 4
        
        def formatla(sayi):
            return f"{sayi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return {"gram": formatla(gram_hesap), "ceyrek": formatla(ceyrek_hesap), "yarim": formatla(yarim_hesap), "tam": formatla(tam_hesap)}
    except:
        return {"gram": "3.210,50", "ceyrek": "5.250,00", "yarim": "10.500,00", "tam": "21.000,00"}

altin_fiyatlari = canli_altin_fiyatlari()

# Gerçek Kayan Yazı (Marquee) Entegrasyonu
st.markdown(f"""
<div class="altin-bandi-konteyner">
    <marquee class="altin-kayan-yazi" scrollamount="5" behavior="scroll" direction="left">
        🌟 GRAM ALTIN: <span class="altin-val">{altin_fiyatlari['gram']} TL</span> 
        🌟 ÇEYREK ALTIN: <span class="altin-val">{altin_fiyatlari['ceyrek']} TL</span> 
        🌟 YARIM ALTIN: <span class="altin-val">{altin_fiyatlari['yarim']} TL</span> 
        🌟 TAM ALTIN: <span class="altin-val">{altin_fiyatlari['tam']} TL</span>
    </marquee>
</div>
""", unsafe_allow_html=True)

# 3. TOPLU HİSSE FİYATI ÇEKİCİ (Hız Koruma Sistemi)
@st.cache_data(ttl=300)
def toplu_fiyat_cek(hisse_kodlari):
    if not hisse_kodlari:
        return {}
    try:
        ticker_listesi = [f"{kod}.IS" for kod in hisse_kodlari]
        data = yf.download(tickers=ticker_listesi, period="1d", progress=False)
        
        fiyat_sozlugu = {}
        for kod in hisse_kodlari:
            try:
                if len(ticker_listesi) == 1:
                    fiyat_sozlugu[kod] = data["Close"].iloc[-1]
                else:
                    fiyat_sozlugu[kod] = data["Close"][f"{kod}.IS"].iloc[-1]
            except:
                fiyat_sozlugu[kod] = 0
        return fiyat_sozlugu
    except:
        return {}

excel_yolu = "nurican.xls.xlsm"

if os.path.exists(excel_yolu):
    try:
        raw_df = pd.read_excel(excel_yolu, sheet_name="WEB", header=None)
        df_hisseler = raw_df.iloc[2:].copy()
        
        tum_kodlar = []
        for idx, row in df_hisseler.iterrows():
            hisse_kodu = str(row[0]).strip() if pd.notna(row[0]) else ""
            if hisse_kodu and hisse_kodu != "None" and hisse_kodu not in tum_kodlar:
                tum_kodlar.append(hisse_kodu)
        
        canli_fiyatlar = toplu_fiyat_cek(tum_kodlar)
        
        bta_listesi = []
        alsat_listesi = []
        
        for idx, row in df_hisseler.iterrows():
            hisse_kodu = str(row[0]).strip() if pd.notna(row[0]) else ""
            
            if hisse_kodu != "" and hisse_kodu != "None":
                bta_alimi = float(str(row[1]).replace(",", ".")) if pd.notna(row[1]) else 0
                al_sat_skoru = str(row[3]).strip() if pd.notna(row[3]) else "0"  # D SÜTUNU (index 3) -> Al Sat Skoru
                al_sat = str(row[4]).strip() if pd.notna(row[4]) else "0"        # E SÜTUNU (index 4)
                bta_puani = str(row[5]).strip() if pd.notna(row[5]) else "0"     # F SÜTUNU (index 5) -> BTA Puanı
                bta_hisse_sutun = str(row[6]).strip() if pd.notna(row[6]) else "0" # G SÜTUNU (index 6) -> BTA Hisse Adı
                
                canli_fiyat = canli_fiyatlar.get(hisse_kodu, bta_alimi)
                if canli_fiyat == 0: 
                    canli_fiyat = bta_alimi
                
                satir_veri = {
                    "BTA Hisse": bta_hisse_sutun,
                    "BTA Puanı": bta_puani,
                    "BTA Alım Fiyatı": f"{bta_alimi:,.2f} TL" if bta_alimi > 0 else "0.00 TL",
                    "Anlık Canlı Fiyat": f"{canli_fiyat:,.2f} TL" if canli_fiyat > 0 else "0.00 TL",
                    "Al Sat": al_sat,
                    "Al Sat Skoru": al_sat_skoru
                }
                
                if bta_hisse_sutun != "0" and bta_hisse_sutun != "":
                    bta_listesi.append(satir_veri)
                    
                if al_sat != "0" and al_sat != "":
                    alsat_listesi.append(satir_veri)
        
        # Tabloları Ekrana Basma
        st.markdown('<div class="alt-baslik-bta">📈 BTA Model Hisseleri</div>', unsafe_allow_html=True)
        if len(bta_listesi) > 0:
            bta_df = pd.DataFrame(bta_listesi)[["BTA Hisse", "BTA Puanı", "BTA Alım Fiyatı", "Anlık Canlı Fiyat"]]
            st.dataframe(bta_df, use_container_width=True, hide_index=True)
        else:
            st.caption("Şu anda aktif BTA modeli hissesi bulunmuyor.")

        st.markdown('<div class="alt-baslik-alsat">🚦 Al Sat Sinyal Hisseleri</div>', unsafe_allow_html=True)
        if len(alsat_listesi) > 0:
            alsat_df = pd.DataFrame(alsat_listesi)[["Al Sat", "Al Sat Skoru", "Anlık Canlı Fiyat"]]
            st.dataframe(alsat_df, use_container_width=True, hide_index=True)
        else:
            st.caption("Şu anda aktif Al Sat sinyali veren hisse bulunmuyor.")
            
    except Exception as e:
        st.error(f"Filtreleme hatası: {e}")
else:
    st.info("⚙️ 'nurican.xls.xlsm' dosyası bekleniyor...")

# 4. GENEL HİSSE ARAMA MOTORU
st.markdown("---")
st.markdown('<div class="alt-baslik-bta">🔍 Genel Hisse Arama Motoru</div>', unsafe_allow_html=True)
arama_input = st.text_input("Hisse Kodu Yazın ve Enter'a Basın (Örn: THYAO):", key="hisse_ara").upper()

if arama_input:
    try:
        hisse_ticker = yf.Ticker(f"{arama_input}.IS")
        hisse_data = hisse_ticker.history(period="1d")
        if not hisse_data.empty:
