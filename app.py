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
    
    /* Yanan Dönen Lambalı Neon Yuvarlak BTA Alanı */
    .bta-cerceve-alani {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 30px;
        padding: 10px;
    }
    
    .bta-yuvarlak-wrapper {
        position: relative;
        width: 160px;
        height: 160px;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* Sürekli Renk Değiştiren Dönen Neon Lamba Çemberi */
    .neon-lamba-cemberi {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 4px dashed #f1c40f;
        box-shadow: 0 0 20px #f1c40f, inset 0 0 15px #f1c40f;
        animation: lambaDonus 6s linear infinite, neonRenkYanis 4s linear infinite;
    }

    /* Çember Etrafındaki Dönen Yıldızlar */
    .yildiz-rotator {
        position: absolute;
        width: 115%;
        height: 115%;
        border-radius: 50%;
        animation: lambaDonus 10s linear infinite;
        z-index: 1;
    }
    .yildiz-item {
        position: absolute;
        font-size: 22px;
        color: #f1c40f;
        text-shadow: 0 0 12px #f1c40f;
    }
    .yildiz-1 { top: 0; left: 50%; transform: translateX(-50%); }
    .yildiz-2 { bottom: 0; left: 50%; transform: translateX(-50%); }
    .yildiz-3 { left: 0; top: 50%; transform: translateY(-50%); }
    .yildiz-4 { right: 0; top: 50%; transform: translateY(-50%); }

    /* Sabit İç Yuvarlak BTA Kutusu */
    .bta-yuvarlak-box {
        width: 120px;
        height: 120px;
        background: rgba(15, 23, 42, 0.95);
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 5;
    }
    
    /* Lambalı El Yazısı Fontu */
    .bta-yazi {
        font-family: 'Playwrite GB S', cursive !important;
        font-size: 34px !important;
        color: #f1c40f !important;
        font-weight: 700;
        text-align: center;
        margin: 0;
        text-shadow: 0 0 10px #f1c40f, 0 0 20px #f1c40f;
    }
    
    @keyframes lambaDonus {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes neonRenkYanis {
        0% { border-color: #f1c40f; box-shadow: 0 0 20px #f1c40f; }
        33% { border-color: #ff3366; box-shadow: 0 0 20px #ff3366; }
        66% { border-color: #00ffcc; box-shadow: 0 0 20px #00ffcc; }
        100% { border-color: #f1c40f; box-shadow: 0 0 20px #f1c40f; }
    }

    /* BÜYÜTÜLMÜŞ SABİT ALTIN FORMATI */
    .altin-blok-konteyner {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-bottom: 30px;
    }
    .altin-satir {
        display: flex;
        justify-content: space-between;
        gap: 10px;
    }
    .altin-kart {
        flex: 1;
        background: rgba(30, 41, 59, 0.9);
        border: 2px solid #f1c40f;
        box-shadow: 0 0 12px rgba(241, 196, 15, 0.2);
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
    }
    .altin-baslik {
        font-size: 14px;
        color: #f1c40f;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .altin-fiyat-deger {
        font-size: 20px !important;
        font-weight: 800;
        color: #ffffff;
    }
    
    .stDataFrame, div[data-testid="stTable"] { color: #ffffff !important; }
    h3, h4, p, span, label { color: #ffffff !important; }
    
    .alt-baslik-bta { border-left: 5px solid #f1c40f; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; font-weight: 600; color: #f1c40f !important; font-size: 18px; }
    .alt-baslik-alsat { border-left: 5px solid #00d2ff; padding-left: 8px; margin-top: 20px; margin-bottom: 8px; font-weight: 600; color: #00d2ff !important; font-size: 18px; }
</style>

<div class="bta-cerceve-alani">
    <div class="bta-yuvarlak-wrapper">
        <!-- Dönen Dış Yıldızlar -->
        <div class="yildiz-rotator">
            <span class="yildiz-item yildiz-1">★</span>
            <span class="yildiz-item yildiz-2">★</span>
            <span class="yildiz-item yildiz-3">★</span>
            <span class="yildiz-item yildiz-4">★</span>
        </div>
        <!-- Yanan Dönen Neon Çember -->
        <div class="neon-lamba-cemberi"></div>
        <!-- Sabit İç Yuvarlak -->
        <div class="bta-yuvarlak-box">
            <h1 class="bta-yazi">BTA</h1>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Hızlandırılmış Canlı Altın Fiyatları
@st.cache_data(ttl=600)
def canli_altin_fiyatlari():
    try:
        data = yf.download(tickers=["GC=F", "TRY=X"], period="1d", group_by='ticker', progress=False)
        ons_gold = data["GC=F"]["Close"].iloc[-1]
        usd_try = data["TRY=X"]["Close"].iloc[-1]
        if pd.isna(ons_gold) or pd.isna(usd_try) or ons_gold <= 0 or usd_try <= 0:
            return {"gram": "3.245,20", "ceyrek": "5.310,00", "yarim": "10.620,00", "tam": "21.240,00"}
        gram_hesap = (ons_gold / 31.1034768) * usd_try
        ceyrek_hesap = gram_hesap * 1.634
        yarim_hesap = ceyrek_hesap * 2
        tam_hesap = ceyrek_hesap * 4
        def formatla(sayi):
            return f"{sayi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return {"gram": formatla(gram_hesap), "ceyrek": formatla(ceyrek_hesap), "yarim": formatla(yarim_hesap), "tam": formatla(tam_hesap)}
    except:
        return {"gram": "3.245,20", "ceyrek": "5.310,00", "yarim": "10.620,00", "tam": "21.240,00"}

altin_fiyatlari = canli_altin_fiyatlari()

st.markdown(f"""
<div class="altin-blok-konteyner">
    <div class="altin-satir">
        <div class="altin-kart">
            <div class="altin-baslik">🌟 GRAM ALTIN</div>
            <div class="altin-fiyat-deger">{altin_fiyatlari['gram']} TL</div>
        </div>
        <div class="altin-kart">
            <div class="altin-baslik">🌟 ÇEYREK ALTIN</div>
            <div class="altin-fiyat-deger">{altin_fiyatlari['ceyrek']} TL</div>
        </div>
    </div>
    <div class="altin-satir">
        <div class="altin-kart">
            <div class="altin-baslik">🌟 YARIM ALTIN</div>
            <div class="altin-fiyat-deger">{altin_fiyatlari['yarim']} TL</div>
        </div>
        <div class="altin-kart">
            <div class="altin-baslik">🌟 TAM ALTIN</div>
            <div class="altin-fiyat-deger">{altin_fiyatlari['tam']} TL</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 3. TOPLU HİSSE FİYATI ÇEKİCİ
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
bta_listesi = []
alsat_listesi = []

if not os.path.exists(excel_yolu):
    st.info("⚙️ 'nurican.xls.xlsm' dosyası bekleniyor...")
else:
    raw_df = pd.read_excel(excel_yolu, sheet_name="WEB", header=None)
    df_hisseler = raw_df.iloc[2:].copy()
    
    tum_kodlar = []
    for idx, row in df_hisseler.iterrows():
        hisse_kodu = str(row[0]).strip() if pd.notna(row[0]) else ""
        if hisse_kodu and hisse_kodu != "None" and hisse_kodu != "" and hisse_kodu not in tum_kodlar:
            tum_kodlar.append(hisse_kodu)
    
    canli_fiyatlar = toplu_fiyat_cek(tum_kodlar)
    
    for idx, row in df_hisseler.iterrows():
        hisse_kodu = str(row[0]).strip() if pd.notna(row[0]) else ""
        if hisse_kodu == "" or hisse_kodu == "None":
            continue
            
        bta_alimi = float(str(row[1]).replace(",", ".")) if pd.notna(row[1]) and str(row[1]).strip() != "" else 0
        al_sat_skoru = str(row[2]).strip() if pd.notna(row[2]) else "0"  # C SÜTUNU -> AL SAT SKORU
        al_sat = str(row[3]).strip() if pd.notna(row[3]) else "0"        # D SÜTUNU -> AL SAT
        bta_puani = str(row[4]).strip() if pd.notna(row[4]) else "0"     # E SÜTUNU -> BTA PUANI
        bta_hisse_sutun = str(row[5]).strip() if pd.notna(row[5]) else "0" # F SÜTUNU -> BTA HISSE
        
        canli_fiyat = canli_fiyatlar.get(hisse_kodu, bta_alimi)
        if canli_fiyat == 0: 
            canli_fiyat = bta_alimi
        
        satir_veri = {
            "Hisse Kodu": hisse_kodu,
            "BTA Hisse": bta_hisse_sutun,
            "BTA Puanı": bta_puani,
            "BTA Alım Fiyatı": f"{bta_alimi:,.2f} TL" if bta_alimi > 0 else "0.00 TL",
            "Anlık Canlı Fiyat": f"{canli_fiyat:,.2f} TL" if canli_fiyat > 0 else "0.00 TL",
            "Al Sat": al_sat,
            "Al Sat Skoru": al_sat_skoru
        }
        
        if bta_hisse_sutun != "0" and bta_hisse_sutun != "" and bta_hisse_sutun != "nan":
            bta_listesi.append(satir_veri)
            
        if al_sat != "0" and al_sat != "" and al_sat != "nan":
            alsat_listesi.append(satir_veri)

# Tabloları Ekrana Basma
st.markdown('<div class="alt-baslik-bta">📈 BTA Model Hisseleri</div>', unsafe_allow_html=True)
if len(bta_listesi) > 0:
