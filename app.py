import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import re
import time

# 1. Sayfa Yapılandırması ve Şık Neon Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important; 
        color: #ffffff !important;
    }
    .bta-logo-konteyner { text-align: center; margin-bottom: 25px; }
    .bta-logo {
        font-family: 'Caveat', cursive;
        font-size: 55px;
        color: #f1c40f;
        text-shadow: 0 0 10px rgba(241, 196, 15, 0.5), 2px 2px 4px rgba(0,0,0,0.8);
    }
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
    .altin-val { color: #ffffff; font-family: 'Poppins', sans-serif; }
    .stDataFrame, div[data-testid="stTable"] { color: #ffffff !important; }
    h3, p, span, label { color: #ffffff !important; }
</style>
<div class="bta-logo-konteyner"><div class="bta-logo">BTA Analiz & Finans Takip Paneli</div></div>
""", unsafe_allow_html=True)

# 2. Canlı Altın Fiyatları Fonksiyonu
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
    st.subheader("📊 Hisselerim ve BTA Model Hesaplamaları")
    excel_yolu = "nurican.xls.xlsm"
    
    if os.path.exists(excel_yolu):
        try:
            # Sizin Excel tablonuzun gerçek yapısına göre sütun harflerini (indisleri) nokta atışı seçiyoruz
            # Sütun isimlerine bağımlı kalmadan direkt pozisyonel okuma yapıyoruz!
            raw_df = pd.read_excel(excel_yolu, sheet_name="WEB", header=None)
            
            # Verileriniz 3. satırdan (index 2) başladığı için üst kısmı kesiyoruz
            df_hisseler = raw_df.iloc[2:].copy()
            
            # Sizin Excel sütun harflerinizin karşılıkları:
            # 0->A (Hisse), 1->B (BTA Alımı), 3->D (Al Sat Skoru), 4->E (Al Sat), 5->F (BTA Puanı), 6->G (BTA Hisse)
            veri_listesi = []
            
            for idx, row in df_hisseler.iterrows():
                hisse_kodu = str(row[0]).strip() if pd.notna(row[0]) else ""
                
                # Eğer A sütunundaki hisse kodu boş değilse satırı işle
                if hisse_kodu != "" and hisse_kodu != "None":
                    bta_alimi = float(str(row[1]).replace(",", ".")) if pd.notna(row[1]) else 0
                    al_sat_skoru = str(row[3]) if pd.notna(row[3]) else "0"
                    al_sat = str(row[4]) if pd.notna(row[4]) else "0"
                    bta_puani = str(row[5]) if pd.notna(row[5]) else "0"
                    bta_hisse_sutun = str(row[6]) if pd.notna(row[6]) else "0"
                    
                    # İnternetten o hissenin anlık fiyatını çekiyoruz
                    try:
                        ticker = yf.Ticker(f"{hisse_kodu}.IS")
                        canli_fiyat = ticker.history(period="1d")['Close'].iloc[-1]
                    except:
                        canli_fiyat = bta_alimi if bta_alimi > 0 else 0
                    
                    # Kar / Zarar (%) Hesaplaması
                    if bta_alimi > 0 and canli_fiyat > 0:
                        kz = ((canli_fiyat - bta_alimi) / bta_alimi) * 100
                        kar_zarar_str = f"%{kz:+.2f}"
                    else:
                        kar_zarar_str = "%0.00"
                        
                    veri_listesi.append({
                        "Hisse Kodu": hisse_kodu,
                        "BTA Puanı": bta_puani,
                        "BTA Alım Fiyatı": f"{bta_alimi:,.2f} TL" if bta_alimi > 0 else "0.00 TL",
                        "Anlık Canlı Fiyat": f"{canli_fiyat:,.2f} TL" if canli_fiyat > 0 else "0.00 TL",
                        "Kar / Zarar (%)": kar_zarar_str,
                        "Al Sat Skoru": al_sat_skoru,
                        "Al Sat": al_sat,
                        "BTA Hisse": bta_hisse_sutun
                    })
            
            if len(veri_listesi) > 0:
                final_df = pd.DataFrame(veri_listesi)
                st.dataframe(final_df, use_container_width=True, hide_index=True)
            else:
                st.warning("Excel 'WEB' sayfasında işlenecek hisse kodu bulunamadı.")
                
        except Exception as e:
            st.error(f"Tablo eşleştirme hatası: {e}")
    else:
        st.info("⚙️ 'nurican.xls.xlsm' dosyası henüz yüklenmedi veya ismi tam uyuşmuyor.")

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
