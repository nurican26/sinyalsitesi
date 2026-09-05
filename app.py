import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re
import time

# 1. Sayfa Yapılandırması ve Şık Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important; 
        color: #ffffff !important;
    }
    
    /* BTA Animasyonlu Yıldızlı ve Dönen Çerçeve Tasarımı */
    .bta-cerceve-alani {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 25px;
        padding: 10px;
    }
    .bta-neon-box {
        position: relative;
        padding: 15px 50px;
        background: rgba(15, 23, 42, 0.9);
        border-radius: 15px;
        overflow: hidden;
        border: 3px solid #f1c40f;
        box-shadow: 0 0 20px #f1c40f, inset 0 0 15px rgba(241, 196, 15, 0.3);
        animation: neonYansima 2s ease-in-out infinite alternate;
    }
    .bta-yazi {
        font-family: 'Caveat', cursive;
        font-size: 65px;
        color: #f1c40f;
        font-weight: 700;
        text-align: center;
        margin: 0;
        line-height: 1;
    }
    /* Çerçeve İçinde Dönen Yıldızlar */
    .yildiz-sol, .yildiz-sag {
        position: absolute;
        top: 30%;
        font-size: 24px;
        color: #f1c40f;
        animation: spinYildiz 3s linear infinite;
    }
    .yildiz-sol { left: 15px; }
    .yildiz-sag { right: 15px; }
    
    @keyframes spinYildiz {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes neonYansima {
        0% { box-shadow: 0 0 10px #f1c40f; }
        100% { box-shadow: 0 0 25px #f39c12; }
    }

    /* Altın Fiyatları Bandı */
    .altin-bandi {
        background-color: rgba(30, 41, 59, 0.8);
        padding: 15px;
        border-radius: 12px;
        color: #f1c40f;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 30px;
        border: 1px solid #f1c40f;
    }
    .altin-val { color: #ffffff; font-family: 'Poppins', sans-serif; }
    .stDataFrame, div[data-testid="stTable"] { color: #ffffff !important; }
    h3, h4, p, span, label { color: #ffffff !important; }
    
    .alt-baslik-bta { border-left: 5px solid #f1c40f; padding-left: 10px; margin-top: 20px; margin-bottom: 10px; font-weight: 600; color: #f1c40f !important; }
    .alt-baslik-alsat { border-left: 5px solid #00d2ff; padding-left: 10px; margin-top: 30px; margin-bottom: 10px; font-weight: 600; color: #00d2ff !important; }
    
    /* SPK Yasal Uyarı Alanı */
    .yasal-uyari-kutusu {
        margin-top: 50px;
        padding: 20px;
        background-color: rgba(30, 41, 59, 0.6);
        border-top: 3px solid #e74c3c;
        border-radius: 8px;
        font-size: 12px;
        color: #bdc3c7 !important;
        text-align: justify;
        line-height: 1.6;
    }
</style>

<!-- Dönen Yıldızlı ve Kayan Efektli BTA Başlığı -->
<div class="bta-cerceve-alani">
    <div class="bta-neon-box">
        <span class="yildiz-sol">★</span>
        <h1 class="bta-yazi">BTA</h1>
        <span class="yildiz-sag">★</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Canlı Altın Fiyatları
@st.cache_data(ttl=300)
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
        return {"gram": "3.150,50", "ceyrek": "5.145,00", "yarim": "10.290,00", "tam": "20.510,00"}

altin_fiyatlari = canli_altin_fiyatlari()

st.markdown(f"""
<div class="altin-bandi">
    🌟 Gram Altın: <span class="altin-val">{altin_fiyatlari['gram']} TL</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
    🌟 Çeyrek Altın: <span class="altin-val">{altin_fiyatlari['ceyrek']} TL</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
    🌟 Yarım Altın: <span class="altin-val">{altin_fiyatlari['yarim']} TL</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
    🌟 Tam Altın: <span class="altin-val">{altin_fiyatlari['tam']} TL</span>
</div>
""", unsafe_allow_html=True)

sol_kolon, sag_kolon = st.columns(2)

with sol_kolon:
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
                    al_sat_skoru = str(row[3]).strip() if pd.notna(row[3]) else "0" # D Sütunu
                    al_sat = str(row[4]).strip() if pd.notna(row[4]) else "0"      # E Sütunu
                    bta_hisse_sutun = str(row[6]).strip() if pd.notna(row[6]) else "0" # G Sütunu
                    
                    # Canlı piyasa verisi çekme (Ok işaretleri için)
                    try:
                        ticker = yf.Ticker(f"{hisse_kodu}.IS")
                        hisse_data = ticker.history(period="1d")
                        canli_fiyat = hisse_data['Close'].iloc[-1]
                        
                        # Anlık durum ok işaretleri
                        onceki_kapanis = ticker.info.get('previousClose', canli_fiyat)
                        if canli_fiyat > onceki_kapanis:
                            canli_durum_oku = "▲ Yükselişte"
                        elif canli_fiyat < onceki_kapanis:
                            canli_durum_oku = "▼ Düşüşte"
                        else:
                            canli_durum_oku = "● Yatay"
                    except:
                        canli_fiyat = bta_alimi
                        canli_durum_oku = "● Spot Canlı"
                    
                    # 1. Filtre: G Sütununda hisse adı varsa BTA Listesine ekle (Sıralama: BTA Hisse başa alındı)
                    if bta_hisse_sutun != "0" and bta_hisse_sutun != "":
                        bta_listesi.append({
                            "BTA Hisse": bta_hisse_sutun,
                            "BTA Puanı (Skor)": al_sat_skoru, # D sütunundaki puan
                            "BTA Alım Fiyatı": f"{bta_alimi:,.2f} TL" if bta_alimi > 0 else "0.00 TL",
                            "Anlık Canlı Fiyat": f"{canli_fiyat:,.2f} TL" if canli_fiyat > 0 else "0.00 TL"
                        })
                        
                    # 2. Filtre: E Sütununda hisse adı varsa Al Sat Listesine ekle (Sıralama: Al Sat başa alındı)
                    if al_sat != "0" and al_sat != "":
                        alsat_listesi.append({
                            "Al Sat": al_sat,
                            "Al Sat Skoru": al_sat_skoru,
                            "Anlık Canlı Fiyat": f"{canli_fiyat:,.2f} TL" if canli_fiyat > 0 else "0.00 TL",
                            "Piyasa Yönü": canli_durum_oku # Kar/zarar yerine canlı ok işaretleri geldi
                        })
            
            # 1. GÖRSEL TABLO: BTA HİSSELERİ
            st.markdown('<div class="alt-baslik-bta">📈 BTA Model Hisseleri</div>', unsafe_allow_html=True)
            if len(bta_listesi) > 0:
                bta_df = pd.DataFrame(bta_listesi)[["BTA Hisse", "BTA Puanı (Skor)", "BTA Alım Fiyatı", "Anlık Canlı Fiyat"]]
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

with sag_kolon:
    st.subheader("🔍 Genel Hisse Arama Motoru")
    st.write("İnternet üzerindeki tüm şirketlerin canlı borsa fiyatlarını anında sorgulayın.")
    arama_input = st.text_input("Hisse Kodu Yazın ve Enter'a Basın (Örn: THYAO):", key="hisse_ara").upper()
    
    if arama_input:
        with st.spinner("Canlı veri sorgulanıyor..."):
            try:
                hisse_ticker = yf.Ticker(f"{arama_input}.IS")
                hisse_data = hisse_ticker.history(period="1d")
                if not hisse_data.empty:
                    son_fiyat = hisse_data['Close'].iloc[-1]
                    onceki_kapanis = hisse_ticker.info.get('previousClose', son_fiyat)
                    degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100
                    st.success(f"**📈 {arama_input} - Canlı Spot Verisi Başarıyla Çekildi**")
                    st.metric(label="Anlık Hisse Fiyatı", value=f"{son_fiyat:,.2f} TL", delta=f"{degisim:+.2f}%")
                else:
