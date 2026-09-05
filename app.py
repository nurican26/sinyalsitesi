import streamlit as st
import pandas as pd
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
    
    /* Yanan Dönen Neon Yuvarlak BTA Alanı */
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
        <div class="yildiz-rotator">
            <span class="yildiz-item yildiz-1">★</span>
            <span class="yildiz-item yildiz-2">★</span>
            <span class="yildiz-item yildiz-3">★</span>
            <span class="yildiz-item yildiz-4">★</span>
        </div>
        <div class="neon-lamba-cemberi"></div>
        <div class="bta-yuvarlak-box">
            <h1 class="bta-yazi">BTA</h1>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Canlı Altın Fiyatları (Sabit Güvenli İstek)
@st.cache_data(ttl=600)
def canli_altin_fiyatlari():
    try:
        data = yf.download(tickers=["GC=F", "TRY=X"], period="1d", group_by='ticker', progress=False)
        ons_gold = data["GC=F"]["Close"].iloc[-1]
        usd_try = data["TRY=X"]["Close"].iloc[-1]
        if pd.isna(ons_gold) or pd.isna(usd_try):
            return {"gram": "3.245,20", "ceyrek": "5.310,00", "yarim": "10.620,00", "tam": "21.240,00"}
        gram_hesap = (ons_gold / 31.1034768) * usd_try
        def formatla(sayi):
            return f"{sayi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return {"gram": formatla(gram_hesap), "ceyrek": formatla(gram_hesap * 1.634), "yarim": formatla(gram_hesap * 3.268), "tam": formatla(gram_hesap * 6.536)}
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

# 3. YÜKSEK HIZLI VE DÖNGÜSÜZ EXCEL İŞLEME SİSTEMİ
excel_yolu = "nurican.xls.xlsm"

@st.cache_data(ttl=300)
def canli_fiyatlari_toplu_getir(kod_listesi):
    if not kod_listesi:
        return {}
    try:
        istek_kodlari = [f"{str(k).strip()}.IS" for k in kod_listesi if pd.notna(k) and str(k).strip() != ""]
        data = yf.download(tickers=istek_kodlari, period="1d", progress=False)
        fiyat_haritasi = {}
        for kod in istek_kodlari:
            temiz_kod = kod.replace(".IS", "")
            if len(istek_kodlari) == 1:
                fiyat_haritasi[temiz_kod] = data["Close"].iloc[-1]
            elif kod in data["Close"]:
                fiyat_haritasi[temiz_kod] = data["Close"][kod].iloc[-1]
        return fiyat_haritasi
    except:
        return {}

if os.path.exists(excel_yolu):
    try:
        # Excel'i doğrudan yükle ve kolonları isimlendir
        df = pd.read_excel(excel_yolu, sheet_name="WEB", header=None)
        df = df.iloc[2:].copy()
        df.columns = ["Hisse Kodu", "BTA Alımı", "Al Sat Skoru", "Al Sat", "BTA Puanı", "BTA Hisse"] + list(df.columns[6:])
        
        # Kod sütunlarındaki boşlukları temizle
        df["Hisse Kodu"] = df["Hisse Kodu"].astype(str).str.strip()
        df["BTA Hisse"] = df["BTA Hisse"].astype(str).str.strip()
        df["Al Sat"] = df["Al Sat"].astype(str).str.strip()
        
        df["BTA Puanı"] = df["BTA Puanı"].fillna("-")
        df["Al Sat Skoru"] = df["Al Sat Skoru"].fillna("0")
        
        # Canlı Fiyatları Doğru Hisse Eşleşmesiyle Çek
        benzersiz_kodlar = df["Hisse Kodu"].unique().tolist()
        fiyat_haritasi = canli_fiyatlari_toplu_getir(benzersiz_kodlar)
        
        # Sayısal değer dönüşümleri ve temizliği
        df["BTA Alımı Sayisal"] = pd.to_numeric(df["BTA Alımı"].astype(str).str.replace(",", "."), errors='coerce').fillna(0)
        df["BTA_Canli_Sayisal"] = df["BTA Hisse"].map(fiyat_haritasi).fillna(df["BTA Alımı Sayisal"])
        df["AlSat_Canli_Sayisal"] = df["Al Sat"].map(fiyat_haritasi).fillna(df["BTA Alımı Sayisal"])
        
        # BTA Hisseleri İçin Kar / Zarar Durumu Hesaplama
        def kar_zarar_hesapla(row_data):
            alim = row_data["BTA Alımı Sayisal"]
            canli = row_data["BTA_Canli_Sayisal"]
            if alim <= 0 or canli <= 0:
                return "0.00 %"
            oran = ((canli - alim) / alim) * 100
            if oran > 0:
                return f"▲ %{oran:.2f}"
            elif oran < 0:
                return f"▼ %{abs(oran):.2f}"
            return "%0.00"
            
        df["Kar / Zarar"] = df.apply(kar_zarar_hesapla, axis=1)
        
        # Metinsel gösterim formatları
        df["BTA Alım Fiyatı"] = df["BTA Alımı Sayisal"].apply(lambda x: f"{x:,.2f} TL" if x > 0 else "0.00 TL")
        df["BTA Canlı Fiyat"] = df["BTA_Canli_Sayisal"].apply(lambda x: f"{x:,.2f} TL" if x > 0 else "0.00 TL")
        df["AlSat Canlı Fiyat"] = df["AlSat_Canli_Sayisal"].apply(lambda x: f"{x:,.2f} TL" if x > 0 else "0.00 TL")

        # TABLO 1: BTA Model Hisseleri (F Sütunu Dolu Olanlar)
        st.markdown('<div class="alt-baslik-bta">📈 BTA Model Hisseleri</div>', unsafe_allow_html=True)
