import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re
import time

# 1. Sayfa Yapılandırması ve Sizin İstediğiniz Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

# Sitenin arka planını koyu neon yapan CSS kodlarınız (Ekranı kararttık)
st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    /* Koyu Şık Neon Arka Plan */
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important; 
        color: #ffffff !important;
    }
    
    /* El Yazısı Başlık Logosu */
    .bta-logo-konteyner {
        text-align: center;
        margin-bottom: 25px;
    }
    .bta-logo {
        font-family: 'Caveat', cursive;
        font-size: 55px;
        color: #f1c40f;
        text-shadow: 0 0 10px rgba(241, 196, 15, 0.5), 2px 2px 4px rgba(0,0,0,0.8);
    }
    
    /* Altın Fiyatları Bandı (Sarı Neon) */
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
        box-shadow: 0 0 15px rgba(241, 196, 15, 0.2);
    }
    .altin-val { 
        color: #ffffff; 
        font-family: 'Poppins', sans-serif; 
    }
    
    /* Streamlit Tablo Yazı Renklerini Beyaz Yapma */
    .stDataFrame, div[data-testid="stTable"] {
        color: #ffffff !important;
    }
    h3, p, span, label { color: #ffffff !important; }
</style>
<div class="bta-logo-konteyner">
    <div class="bta-logo">BTA Analiz & Finans Takip Paneli</div>
</div>
""", unsafe_allow_html=True)

# 2. İnternetten Canlı Altın Fiyatlarını Çekme (Tam İstediğiniz Noktalı Birim)
@st.cache_data(ttl=300)
def canli_altin_fiyatlari():
    try:
        # Altın Ons ve Dolar kurunu çekip Gram Altın hesaplama
        ons_gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        usd_try = yf.Ticker("TRY=X").history(period="1d")['Close'].iloc[-1]
        gram_hesap = (ons_gold / 31.1034768) * usd_try
        
        ceyrek_hesap = gram_hesap * 1.634
        yarim_hesap = ceyrek_hesap * 2
        tam_hesap = ceyrek_hesap * 4
        
        # Noktalı Türk Lirası formatına çevirme fonksiyonu
        def formatla(sayi):
            return f"{sayi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
        return {
            "gram": formatla(gram_hesap),
            "ceyrek": formatla(ceyrek_hesap),
            "yarim": formatla(yarim_hesap),
            "tam": formatla(tam_hesap)
        }
    except:
        # İnternet kesilirse koruma amaçlı sabit Türk Lirası fiyatları
        return {"gram": "3.150,50", "ceyrek": "5.145,00", "yarim": "10.290,00", "tam": "20.510,00"}

altin_fiyatlari = canli_altin_fiyatlari()

# Altın Bandını Ekrana Basıyoruz
st.markdown(f"""
<div class="altin-bandi">
    🌟 Gram Altın: <span class="altin-val">{altin_fiyatlari['gram']} TL</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
    🌟 Çeyrek Altın: <span class="altin-val">{altin_fiyatlari['ceyrek']} TL</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
    🌟 Yarım Altın: <span class="altin-val">{altin_fiyatlari['yarim']} TL</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
    🌟 Tam Altın: <span class="altin-val">{altin_fiyatlari['tam']} TL</span>
</div>
""", unsafe_allow_html=True)

# Ekranı İki Sütuna Bölüyoruz
sol_kolon, sag_kolon = st.columns(2)

with sol_kolon:
    st.subheader("📊 Hisselerim ve BTA Model Hesaplamaları")
    
    excel_yolu = "nurican.xls.xlsm"
    
    # Excel dosyanız henüz yüklenmediyse sitenin kırmızı hata verip çökmesini engelliyoruz!
    if os.path.exists(excel_yolu):
        try:
            # Excel'deki formüllü yeni temiz WEB sayfanızı okuyoruz
            df = pd.read_excel(excel_yolu, sheet_name="WEB", skiprows=2, header=None)
            df.columns = ["Hisse Kodu", "BTA Puanı (H)", "BTA Alım Fiyatı (Sabit)", "R Sütunu", "T Sütunu", "U Sütunu", "W Sütunu"]
            
            # Boş hisseleri temizle
            df = df.dropna(subset=["Hisse Kodu"])
            
            anlik_fiyatlar = []
            kar_zararlar = []
            
            for idx, row in df.iterrows():
                hisse = str(row["Hisse Kodu"]).strip()
                sabit_alim = float(str(row["BTA Alım Fiyatı (Sabit)"]).replace(",", ".")) if pd.notna(row["BTA Alım Fiyatı (Sabit)"]) else 0
                
                # Canlı borsa fiyatını internetten anlık çekiyoruz
                try:
                    ticker = yf.Ticker(f"{hisse}.IS")
                    canli_fiyat = ticker.history(period="1d")['Close'].iloc[-1]
                except:
                    canli_fiyat = sabit_alim
                
                anlik_fiyatlar.append(f"{canli_fiyat:,.2f} TL")
                
                # Kar / Zarar (%) Hesaplama mekanizması
                if sabit_alim > 0:
                    kz = ((canli_fiyat - sabit_alim) / sabit_alim) * 100
                    kar_zararlar.append(f"%{kz:+.2f}")
                else:
                    kar_zararlar.append("%0.00")
            
            df["Anlık Canlı Fiyat"] = anlik_fiyatlar
            df["Kar / Zarar (%)"] = kar_zararlar
            
            # Tablo düzenini tam istediğiniz gibi gösteriyoruz
            gosterilecek_df = df[["Hisse Kodu", "BTA Puanı (H)", "BTA Alım Fiyatı (Sabit)", "Anlık Canlı Fiyat", "Kar / Zarar (%)", "T Sütunu", "W Sütunu"]]
            st.dataframe(gosterilecek_df, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.info("Excel verileri hazırlanıyor, lütfen bekleyin...")
    else:
        # Kırmızı hata yerine kullanıcılara şık bir bilgilendirme mesajı bırakıyoruz
        st.info("⚙️ Excel veri tabanı henüz yüklenmedi. Lütfen 'nurican.xls.xlsm' dosyanızı GitHub deponuza yükleyin. Tablonuz otomatik olarak burada belirecektir.")

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
                    st.error("Hisse kodu bulunamadı. Lütfen geçerli bir kod girin (Örn: EREGL).")
            except:
                st.error("Veri çekme sınırına ulaşıldı veya internet bağlantısı kesildi.")
