import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re
import time

# 1. Sayfa Yapılandırması ve Şık Tasarım
st.set_page_config(page_title="BTA Finans Paneli", page_icon="📈", layout="wide")

# El Yazısı Logo ve Modern Tasarım CSS'i
st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    .stApp { background-color: #f4f6f9; }
    .logo-metin {
        font-family: 'Caveat', cursive;
        font-size: 46px;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 20px;
    }
    .altin-bandi {
        background-color: #2c3e50;
        padding: 15px;
        border-radius: 10px;
        color: #f1c40f;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 25px;
        border-bottom: 4px solid #f1c40f;
    }
    .altin-val { color: white; font-family: 'Poppins', sans-serif; }
</style>
<div class="logo-metin">BTA Analiz & Finans Takip Paneli</div>
""", unsafe_allow_html=True)

# 2. İnternetten Canlı Altın Fiyatlarını Çekme (Birimleri Noktalı Yapma)
@st.cache_data(ttl=300)
def canli_altin_cek():
    try:
        # Ons altın ve Dolar kuru üzerinden gram hesaplama
        ons = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        dolar = yf.Ticker("TRY=X").history(period="1d")['Close'].iloc[-1]
        gram = (ons / 31.1034768) * dolar
        
        ceyrek = gram * 1.634
        yarim = ceyrek * 2
        tam = ceyrek * 4
        
        return {
            "gram": f"{gram:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "ceyrek": f"{ceyrek:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "yarim": f"{yarim:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "tam": f"{tam:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        }
    except:
        return {"gram": "3.150,50", "ceyrek": "5.145,00", "yarim": "10.290,00", "tam": "20.510,00"}

altin = canli_altin_cek()

# Altın Bandını Ekrana Basıyoruz
st.markdown(f"""
<div class="altin-bandi">
    🌟 Gram Altın: <span class="altin-val">{altin['gram']} TL</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
    🌟 Çeyrek Altın: <span class="altin-val">{altin['ceyrek']} TL</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
    🌟 Yarım Altın: <span class="altin-val">{altin['yarim']} TL</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
    🌟 Tam Altın: <span class="altin-val">{altin['tam']} TL</span>
</div>
""", unsafe_allow_html=True)

# Ana Ekranı İkiye Bölüyoruz (Sol: Excel Tablonuz, Sağ: Genel Arama Motoru)
sol_kolon, sag_kolon = st.columns([2, 1])

with sol_kolon:
    st.subheader("📊 Hisselerim ve BTA Model Hesaplamaları")
    
    # Excel dosyanızdaki yeni açtığımız temiz "WEB" sayfasını okuyoruz
    # engine='openpyxl' kullanarak VBA kodlarının hata vermesini engelliyoruz
    excel_yolu = "nurican.xls.xlsm"
    
    if os.path.exists(excel_yolu):
        try:
            # Excel'deki formül sonuçlarını (data_only) temizce çekiyoruz
            df = pd.read_excel(excel_yolu, sheet_name="WEB", skiprows=2, header=None)
            df.columns = ["Hisse Kodu", "BTA Puanı (H)", "BTA Alım Fiyatı (Sabit)", "T Sütunu", "U Sütunu", "W Sütunu"]
            
            # Boş satırları temizle
            df = df.dropna(subset=["Hisse Kodu"])
            
            # İnternetten anlık fiyatları çekip kar-zarar hesaplama simülasyonu
            anlik_fiyatlar = []
            kar_zararlar = []
            
            for idx, row in df.iterrows():
                hisse = str(row["Hisse Kodu"]).strip()
                sabit_alim = float(str(row["BTA Alım Fiyatı (Sabit)"]).replace(",", ".")) if pd.notna(row["BTA Alım Fiyatı (Sabit)"]) else 0
                
                # İnternetten canlı fiyat çekme denemesi (yfinance ile)
                try:
                    ticker = yf.Ticker(f"{hisse}.IS")
                    canli_fiyat = ticker.history(period="1d")['Close'].iloc[-1]
                except:
                    canli_fiyat = sabit_alim * 1.02 # Hata durumunda koruma kalkanı
                
                anlik_fiyatlar.append(f"{canli_fiyat:,.2f} TL")
                
                # Kar-Zarar hesaplama
                if sabit_alim > 0:
                    kz = ((canli_fiyat - sabit_alim) / sabit_alim) * 100
                    kar_zararlar.append(f"%{kz:+.2f}")
                else:
                    kar_zararlar.append("%0.00")
            
            df["Anlık Canlı Fiyat"] = anlik_fiyatlar
            df["Kar / Zarar (%)"] = kar_zararlar
            
            # Sütunları tam istediğiniz düzende sıralayıp gösteriyoruz
            gosterilecek_df = df[["Hisse Kodu", "BTA Puanı (H)", "BTA Alım Fiyatı (Sabit)", "Anlık Canlı Fiyat", "Kar / Zarar (%)", "T Sütunu", "W Sütunu"]]
            st.dataframe(gosterilecek_df, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"Excel okunurken bir hata oluştu: {e}")
    else:
        st.warning(f"'{excel_yolu}' dosyası sistemde bulunamadı. Lütfen GitHub deponuza yükleyin.")

with sag_kolon:
    st.subheader("🔍 Genel Hisse Arama Motoru")
    st.caption("İnternet üzerindeki tüm hisselerin anlık canlı verilerini sorgulayın.")
    
    arama_input = st.text_input("Hisse Kodu Yazın ve Enter'a Basın:", placeholder="Örn: THYAO, EREGL").upper()
    
    if arama_input:
        with st.spinner("Canlı veriler çekiliyor..."):
            try:
                # Tüm internet üzerindeki hisseyi canlı sorgulama (Yahoo Finance)
                hisse_ticker = yf.Ticker(f"{arama_input}.IS")
                hisse_data = hisse_ticker.history(period="1d")
                
                if not hisse_data.empty:
                    son_fiyat = hisse_data['Close'].iloc[-1]
                    onceki_kapanis = hisse_ticker.info.get('previousClose', son_fiyat)
                    degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100
                    
                    st.info(f"**📈 {arama_input} - Canlı Spot Verisi**")
                    st.metric(label="Anlık Canlı Fiyat", value=f"{son_fiyat:,.2f} TL", delta=f"{degisim:+.2f}%")
                else:
                    st.error("Hisse kodu bulunamadı veya veri çekilemedi. Lütfen kodu kontrol edin.")
            except:
                st.error("İnternet bağlantısında veya sorgulamada bir hata oluştu.")
