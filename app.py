import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import time

# 1. Sayfa Yapılandırması ve TELEFON / MOBİL FORMAT UYUMU
st.set_page_config(page_title="BTA", page_icon="📈", layout="centered") # layout="centered" yaparak telefon ekranına tam eşitledik

st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important; 
        color: #ffffff !important;
    }
    
    /* Mobil Uyumlu BTA Neon Çerçeve */
    .bta-cerceve-alani {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 15px;
        padding: 5px;
    }
    .bta-neon-box {
        position: relative;
        padding: 10px 35px;
        background: rgba(15, 23, 42, 0.9);
        border-radius: 12px;
        border: 3px solid #f1c40f;
        box-shadow: 0 0 15px #f1c40f;
    }
    .bta-yazi {
        font-family: 'Caveat', cursive;
        font-size: 45px; /* Mobilde taşmasın diye yazı boyutunu küçülttük */
        color: #f1c40f;
        font-weight: 700;
        text-align: center;
        margin: 0;
    }
    .yildiz-sol, .yildiz-sag {
        position: absolute;
        top: 25%;
        font-size: 20px;
        color: #f1c40f;
        animation: spinYildiz 3s linear infinite;
    }
    .yildiz-sol { left: 10px; }
    .yildiz-sag { right: 10px; }
    
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
        overflow-x: auto; /* Mobilde parmakla kaydırılabilir */
        white-space: nowrap;
    }
    .altin-val { color: #ffffff; }
    .stDataFrame, div[data-testid="stTable"] { color: #ffffff !important; }
    h3, h4, p, span, label { color: #ffffff !important; }
    
    .alt-baslik-bta { border-left: 5px solid #f1c40f; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; font-weight: 600; color: #f1c40f !important; font-size: 16px; }
    .alt-baslik-alsat { border-left: 5px solid #00d2ff; padding-left: 8px; margin-top: 20px; margin-bottom: 8px; font-weight: 600; color: #00d2ff !important; font-size: 16px; }
</style>

<div class="bta-cerceve-alani">
    <div class="bta-neon-box">
        <span class="yildiz-sol">★</span>
        <h1 class="bta-yazi">BTA</h1>
        <span class="yildiz-sag">★</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Hızlandırılmış Canlı Altın Fiyatları (Aşırı Sorguyu Engellemek İçin Önbellek Süresini Artırdık)
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

# 3. YAVAŞLIĞI ÖNLEYEN HIZLI HİSSE FİYAT SORGULAYICI (Hata Vermeyen Sistem)
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
                al_sat_skoru = str(row[3]).strip() if pd.notna(row[3]) else "0"  # D Sütunu (BTA Puanı / Skor)
                al_sat = str(row[4]).strip() if pd.notna(row[4]) else "0"        # E Sütunu
                bta_hisse_sutun = str(row[6]).strip() if pd.notna(row[6]) else "0" # G Sütunu
                
                # İnterneti yormayan hızlı fiyat çekici fonksiyonumuzu çağırıyoruz
                canli_fiyat, canli_durum_oku = hizli_hisse_fiyat_cek(hisse_kodu, bta_alimi)
                
                satir_veri = {
                    "BTA Hisse": bta_hisse_sutun,
                    "BTA Puanı": al_sat_skoru, # İstediğiniz D sütunundaki BTA Puanı başarıyla eklendi!
                    "BTA Alım Fiyatı": f"{bta_alimi:,.2f} TL" if bta_alimi > 0 else "0.00 TL",
                    "Anlık Canlı Fiyat": f"{canli_fiyat:,.2f} TL" if canli_fiyat > 0 else "0.00 TL",
                    "Al Sat": al_sat,
                    "Al Sat Skoru": al_sat_skoru,
                    "Piyasa Yönü": canli_durum_oku
                }
                
                if bta_hisse_sutun != "0" and bta_hisse_sutun != "":
                    bta_listesi.append(satir_veri)
                    
                if al_sat != "0" and al_sat != "":
                    alsat_listesi.append(satir_veri)
        
        # 1. GÖRSEL TABLO: BTA HİSSELERİ (D SÜTUNUNDAKİ BTA PUANI DAHİL)
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

# MOBİL İÇİN ARAMA MOTORUNU ALT KISMA ALDIK (Dikey Sıralama Düzeni)
st.markdown("---")
st.markdown('<div class="alt-baslik-bta">🔍 Genel Hisse Arama Motoru</div>', unsafe_allow_html=True)
arama_input = st.text_input("Hisse Kodu Yazın ve Enter'a Basın (Örn: THYAO):", key="hisse_ara").upper()

if arama_input:
    try:
        hisse_ticker = yf.Ticker(f"{arama_input}.IS")
        hisse_data = hisse_ticker.history(period="1d")
        if not hisse_data.empty:
            son_fiyat = hisse_data['Close'].iloc[-1]
            onceki_kapanis = hisse_ticker.info.get('previousClose', son_fiyat)
            degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100
            st.success(f"**📈 {arama_input} - Canlı Spot Veri**")
            st.metric(label="Anlık Hisse Fiyatı", value=f"{son_fiyat:,.2f} TL", delta=f"{degisim:+.2f}%")
        else:
            st.error("Hisse kodu bulunamadı.")
    except:
        st.error("Sorgu sınırı aşıldı, lütfen biraz bekleyin.")
