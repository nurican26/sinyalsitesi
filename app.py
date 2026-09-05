import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time

# 1. Sayfa Yapılandırması ve TELEFON / MOBİL FORMAT UYUMU
st.set_page_config(page_title="BTA", page_icon="📈", layout="centered")

st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important; 
        color: #ffffff !important;
    }
    
    /* Mobil Uyumlu Yuvarlak BTA Tasarımı */
    .bta-cerceve-alani {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
        padding: 10px;
    }
    .bta-yuvarlak-box {
        position: relative;
        width: 140px;
        height: 140px;
        background: rgba(15, 23, 42, 0.9);
        border-radius: 50%;
        border: 4px solid #f1c40f;
        box-shadow: 0 0 20px #f1c40f;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
    }
    .bta-yazi {
        font-family: 'Caveat', cursive !important;
        font-size: 42px !important;
        color: #f1c40f !important;
        font-weight: 700;
        text-align: center;
        margin: 0;
        z-index: 2;
    }
    
    /* Daire İçinde Dönen Yıldızlar */
    .yildiz-container {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        animation: spinYildiz 6s linear infinite;
        z-index: 1;
    }
    .yildiz-ust, .yildiz-alt, .yildiz-sol, .yildiz-sag {
        position: absolute;
        font-size: 16px;
        color: rgba(241, 196, 15, 0.8);
    }
    .yildiz-ust { top: 8px; left: 50%; transform: translateX(-50%); }
    .yildiz-alt { bottom: 8px; left: 50%; transform: translateX(-50%); }
    .yildiz-sol { left: 8px; top: 50%; transform: translateY(-50%); }
    .yildiz-sag { right: 8px; top: 50%; transform: translateY(-50%); }
    
    @keyframes spinYildiz {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Mobil Uyumlu Kayan Altın Bandı */
    .altin-bandi {
        background-color: rgba(30, 41, 59, 0.8);
        padding: 10px;
        border-radius: 8px;
        color: #f1c40f;
        text-align: center;
        font-weight: bold;
        font-size: 13px;
        margin-bottom: 20px;
        border: 1px solid #f1c40f;
        overflow-x: auto;
        white-space: nowrap;
    }
    .altin-val { color: #ffffff; }
    .stDataFrame, div[data-testid="stTable"] { color: #ffffff !important; }
    h3, h4, p, span, label { color: #ffffff !important; }
    
    .alt-baslik-bta { border-left: 5px solid #f1c40f; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; font-weight: 600; color: #f1c40f !important; font-size: 16px; }
    .alt-baslik-alsat { border-left: 5px solid #00d2ff; padding-left: 8px; margin-top: 20px; margin-bottom: 8px; font-weight: 600; color: #00d2ff !important; font-size: 16px; }
</style>

<div class="bta-cerceve-alani">
    <div class="bta-yuvarlak-box">
        <div class="yildiz-container">
            <span class="yildiz-ust">★</span>
            <span class="yildiz-sag">★</span>
            <span class="yildiz-alt">★</span>
            <span class="yildiz-sol">★</span>
        </div>
        <h1 class="bta-yazi">BTA</h1>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Hızlandırılmış Canlı Altın Fiyatları (Önbellek Süresi 10 Dakika)
@st.cache_data(ttl=600)
def canli_altin_fiyatlari():
    try:
        ons_gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        usd_try = yf.Ticker("TRY=X").history(period="1d")['Close'].iloc[-1]
        gram_hesap = (ons_gold / 31.1034768) * usd_try
        ceyrek_hesap = gram_hesap * 1.634
        yarim_hesap = ceyrek_hesap * 2
        tam_hesap = ceyrek_hesap * 4
        
        def formatla(sayi):
            return f"{sayi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return {"gram": formatla(gram_hesap), "ceyrek": formatla(ceyrek_hesap), "yarim": formatla(yarim_hesap), "tam": formatla(tam_hesap)}
    except:
        # Bağlantı hatası durumunda çökmemesi için yedek sabit fiyatlar
        return {"gram": "3.165,20", "ceyrek": "5.175,00", "yarim": "10.350,00", "tam": "20.700,00"}

altin_fiyatlari = canli_altin_fiyatlari()

st.markdown(f"""
<div class="altin-bandi">
    🌟 Gr: <span class="altin-val">{altin_fiyatlari['gram']} TL</span> | 
    🌟 Çeyrek: <span class="altin-val">{altin_fiyatlari['ceyrek']} TL</span> | 
    🌟 Yarım: <span class="altin-val">{altin_fiyatlari['yarim']} TL</span> | 
    🌟 Tam: <span class="altin-val">{altin_fiyatlari['tam']} TL</span>
</div>
""", unsafe_allow_html=True)

# 3. YAVAŞLIĞI ÖNLEYEN HIZLI HİSSE FİYAT SORGULAYICI
@st.cache_data(ttl=300)
def hizli_hisse_fiyat_cek(hisse_kod, varsayilan_fiyat):
    try:
        ticker = yf.Ticker(f"{hisse_kod}.IS")
        hisse_data = ticker.history(period="1d")
        if not hisse_data.empty:
            canli_fiyat = hisse_data['Close'].iloc[-1]
            onceki_kapanis = ticker.info.get('previousClose', canli_fiyat)
            yön = "▲ Yükselişte" if canli_fiyat > onceki_kapanis else ("▼ Düşüşte" if canli_fiyat < onceki_kapanis else "● Yatay")
            return canli_fiyat, yön
        return varsayilan_fiyat, "● Spot Canlı"
    except:
        return varsayilan_fiyat, "● Spot Canlı"

excel_yolu = "nurican.xls.xlsm"

if os.path.exists(excel_yolu):
    try:
        raw_df = pd.read_excel(excel_yolu, sheet_name="WEB", header=None)
        df_hisseler = raw_df.iloc[2:].copy()
        
        bta_listesi = []
        alsat_listesi = []
        
        for idx, row in df_hisseler.iterrows():
            hisse_kodu = str(row[0]).strip() if pd.notna(row[0]) else ""
            
            if hisse_kodu != "" and hisse_kodu != "None":
                bta_alimi = float(str(row[1]).replace(",", ".")) if pd.notna(row[1]) else 0
                al_sat_skoru = str(row[3]).strip() if pd.notna(row[3]) else "0"  # D SÜTUNU (Al Sat Skoru)
                al_sat = str(row[4]).strip() if pd.notna(row[4]) else "0"        # E SÜTUNU
                bta_puani = str(row[5]).strip() if pd.notna(row[5]) else "0"     # F SÜTUNU (BTA Puanı)
                bta_hisse_sutun = str(row[6]).strip() if pd.notna(row[6]) else "0" # G SÜTUNU
                
                canli_fiyat, canli_durum_oku = hizli_hisse_fiyat_cek(hisse_kodu, bta_alimi)
                
                satir_veri = {
                    "BTA Hisse": bta_hisse_sutun,
                    "BTA Puanı": bta_puani,       # Artık F sütununa bakıyor
                    "BTA Alım Fiyatı": f"{bta_alimi:,.2f} TL" if bta_alimi > 0 else "0.00 TL",
                    "Anlık Canlı Fiyat": f"{canli_fiyat:,.2f} TL" if canli_fiyat > 0 else "0.00 TL",
                    "Al Sat": al_sat,
                    "Al Sat Skoru": al_sat_skoru, # Artık D sütununa bakıyor
                    "Piyasa Yönü": canli_durum_oku
                }
                
                if bta_hisse_sutun != "0" and bta_hisse_sutun != "":
                    bta_listesi.append(satir_veri)
                    
                if al_sat != "0" and al_sat != "":
                    alsat_listesi.append(satir_veri)
        
        # 1. GÖRSEL TABLO: BTA HİSSELERİ
        st.markdown('<div class="alt-baslik-bta">📈 BTA Model Hisseleri</div>', unsafe_allow_html=True)
        if len(bta_listesi) > 0:
            bta_df = pd.DataFrame(bta_listesi)[["BTA Hisse", "BTA Puanı", "BTA Alım Fiyatı", "Anlık Canlı Fiyat"]]
            st.dataframe(bta_df, use_container_width=True, hide_index=True)
        else:
            st.caption("Şu anda aktif BTA modeli hissesi bulunmuyor.")

        # 2. GÖRSEL TABLO: AL SAT HİSSELERİ
        st.markdown('<div class="alt-baslik-alsat">🚦 Al Sat Sinyal Hisseleri</div>', unsafe_allow_html=True)
        if len(alsat_listesi) > 0:
            alsat_df = pd.DataFrame(alsat_listesi)[["Al Sat", "Al Sat Skoru", "Anlık Canlı Fiyat", "Piyasa Yönü"]]
            st.dataframe(alsat_df, use_container_width=True, hide_index=True)
        else:
            st.caption("Şu anda aktif Al Sat sinyali veren hisse bulunmuyor.")
            
    except Exception as e:
        st.error(f"Filtreleme hatası: {e}")
else:
    st.info("⚙️ 'nurican.xls.xlsm' dosyası bekleniyor...")

# 4. GENEL HİSSE ARAMA MOTORU (Yarım Kalan Kısım Tamamlandı)
st.markdown("---")
st.markdown('<div class="alt-baslik-bta">🔍 Genel Hisse Arama Motoru</div>', unsafe_allow_html=True)
arama_input = st.text_input("Hisse Kodu Yazın ve Enter'a Basın (Örn: THYAO):", key="hisse_ara").upper()

if arama_input:
    try:
        hisse_ticker = yf.Ticker(f"{arama_input}.IS")
        hisse_data = hisse_ticker.history(period="1d")
        if not hisse_data.empty:
            son_fiyat = hisse_data['Close'].iloc[-1]
            st.success(f"🔍 {arama_input} Son Güncel Fiyatı: **{son_fiyat:,.2f} TL**")
        else:
            st.warning("Hisse verisi bulunamadı. Lütfen kodu kontrol edin.")
    except Exception as e:
        st.error(f"Arama sırasında hata oluştu: {e}")
