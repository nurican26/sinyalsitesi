import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="BİST Hacimli Yükselenler", layout="centered")

# CSS ile Görsel Özelleştirme (Resimdeki Tema)
st.markdown("""
    <style>
    /* Arka Plan ve Genel Yazılar */
    .stApp {
        background-color: #0b111e;
        color: #ffffff;
    }
    
    /* Ana Kart Çerçevesi */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #050c17;
        border-radius: 8px;
        border: 1px solid #1a2638;
    }

    /* Yeşil Başlık Kutusu */
    .widget-header {
        background-color: #00f2c3;
        color: #000000;
        text-align: center;
        padding: 12px;
        font-weight: bold;
        font-size: 18px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-bottom: 10px;
    }

    /* Tablo Stil Özelleştirmeleri */
    .dataframe {
        width: 100% !important;
        background-color: #050c17 !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    .dataframe th {
        color: #00f2c3 !important;
        background-color: #091424 !important;
        border-bottom: 1px solid #1a2638 !important;
        text-align: right !important;
    }
    
    .dataframe th:first-child {
        text-align: left !important;
    }

    .dataframe td {
        border-bottom: 1px dashed #142033 !important;
        text-align: right !important;
        padding: 8px !important;
    }

    .dataframe td:first-child {
        text-align: left !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<div class="widget-header">BİST Hacimli Yükselenler</div>', unsafe_allow_html=True)

# Takip Edilecek Hisseler
hisseler = [
    "RTALB.IS", "IHYAY.IS", "TDGYO.IS", "KARSN.IS", "EGEEN.IS", 
    "AKSUE.IS", "IHLGM.IS", "ALCAR.IS", "EDATA.IS", "THYAO.IS", 
    "ASELS.IS", "EREGL.IS", "AKBNK.IS", "GARAN.IS", "SASA.IS"
]

@st.cache_data(ttl=60)
def verileri_getir():
    data = []
    for sembol in hisseler:
        try:
            ticker = yf.Ticker(sembol)
            df = ticker.history(period="2d")
            
            if len(df) >= 2:
                son_fiyat = df['Close'].iloc[-1]
                onceki_kapanis = df['Close'].iloc[-2]
                hacim_lot = df['Volume'].iloc[-1]
                
                # Yüzde Değişim Hesabı
                degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100
                
                # TL Cinsinden İşlem Hacmi (Yaklaşık)
                hacim_tl = hacim_lot * son_fiyat
                
                # Hacim Formatlama (Milyon / Bin TL)
                if hacim_tl >= 1_000_000:
                    hacim_str = f"{hacim_tl / 1_000_000:.1f}M TL"
                else:
                    hacim_str = f"{hacim_tl / 1_000:.0f}K TL"

                data.append({
                    "HİSSE": sembol.replace(".IS", ""),
                    "SON (TL)": f"{son_fiyat:.2f}",
                    "HACİM (TL)": hacim_str,
                    "DEĞİŞİM": degisim,
                    "DEĞİŞİM (%)": f"+{degisim:.2f} %" if degisim > 0 else f"{degisim:.2f} %"
                })
        except Exception:
            continue

    df_result = pd.DataFrame(data)
    if not df_result.empty:
        # En çok yükselene göre sırala
        df_result = df_result.sort_values(by="DEĞİŞİM", ascending=False)
        return df_result[["HİSSE", "SON (TL)", "HACİM (TL)", "DEĞİŞİM (%)"]]
    return pd.DataFrame()

# Veri Yükleme ve Gösterim
with st.spinner("Piyasa verileri güncelleniyor..."):
    df_sonuc = verileri_getir()

if not df_sonuc.empty:
    # Tabloyu HTML olarak bas (Özel tasarım için)
    st.write(df_sonuc.to_html(index=False, escape=False), unsafe_allow_html=True)
else:
    st.error("Veriler çekilemedi. Lütfen internet bağlantınızı veya simgeleri kontrol edin.")

# Yenileme Butonu
if st.button("Verileri Yenile"):
    st.cache_data.clear()
    st.rerun()
