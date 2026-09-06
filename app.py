import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
from streamlit_autorefresh import st_autorefresh

# Sayfa Yapılandırması
st.set_page_config(page_title="Canlı Hisse Takip Programı", layout="wide")

# 🔄 CANLI FİYAT VE ANIMASYON KİLİDİ: Sayfa her 10 saniyede bir otomatik yenilenir ve animasyonlar baştan tetiklenir
st_autorefresh(interval=10 * 1000, key="hisse_canli_yenileyici")

# Şık Neon Tasarım, Her Yenilemede Hareketlenen Gökkuşağı Çember ve Yazı CSS Kodları
st.markdown('''
<style>
    .stApp {background: #0f172a!important; padding: 0.5rem;} 
    h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important;} 
    .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} 
    .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;} 
    .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;} 
    .spk-kutusu {background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; color: #fca5a5 !important; font-size: 0.95rem;}
    
    /* 🌈 ANIMASYONLU GÖKKUŞAĞI ÇEMBER VE KAYAN BTA LOGO ALANI */
    .logo-konteyner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px 0;
        margin-bottom: 10px;
    }
    .cember-animasyon {
        width: 110px;
        height: 110px;
        border: 4px solid #fff;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: transparent;
        position: relative;
        overflow: hidden;
        
        /* Gökkuşağı renk geçişi ve yukarıdan düşme animasyonu */
        animation: 
            gokkusagiRenk 6s linear infinite,
            yukardanDus 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    .bta-yazi {
        font-family: 'Caveat', 'Segoe UI', cursive, sans-serif;
        font-size: 2.8rem;
        font-weight: bold;
        margin: 0;
        padding: 0;
        z-index: 2;
        
        /* Yazının rengi ve soldan yavaşça kayma animasyonu */
        animation: 
            gokkusagiYaziRenk 6s linear infinite,
            soldanYavascaKay 1.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }
    
    /* 🎯 Gökkuşağı Renk Animasyonları */
    @keyframes gokkusagiRenk {
        0% { border-color: #ff0000; box-shadow: 0 0 15px #ff0000, inset 0 0 15px #ff0000; }
        17% { border-color: #ff7f00; box-shadow: 0 0 15px #ff7f00, inset 0 0 15px #ff7f00; }
        33% { border-color: #ffff00; box-shadow: 0 0 15px #ffff00, inset 0 0 15px #ffff00; }
        50% { border-color: #00ff00; box-shadow: 0 0 15px #00ff00, inset 0 0 15px #00ff00; }
        67% { border-color: #0000ff; box-shadow: 0 0 15px #0000ff, inset 0 0 15px #0000ff; }
        83% { border-color: #4b0082; box-shadow: 0 0 15px #4b0082, inset 0 0 15px #4b0082; }
        100% { border-color: #9400d3; box-shadow: 0 0 15px #9400d3, inset 0 0 15px #9400d3; }
    }

    @keyframes gokkusagiYaziRenk {
        0% { color: #ff0000; text-shadow: 0 0 10px rgba(255,0,0,0.5); }
        17% { color: #ff7f00; text-shadow: 0 0 10px rgba(255,127,0,0.5); }
        33% { color: #ffff00; text-shadow: 0 0 10px rgba(255,255,0,0.5); }
        50% { color: #00ff00; text-shadow: 0 0 10px rgba(0,255,0,0.5); }
        67% { color: #0000ff; text-shadow: 0 0 10px rgba(0,0,255,0.5); }
        83% { color: #4b0082; text-shadow: 0 0 10px rgba(75,0,130,0.5); }
        100% { color: #9400d3; text-shadow: 0 0 10px rgba(148,0,211,0.5); }
    }

    /* Çemberin düşme efekti */
    @keyframes yukardanDus {
        0% { transform: translateY(-200px) scale(0.3); opacity: 0; }
        70% { transform: translateY(10px) scale(1.05); opacity: 1; }
        100% { transform: translateY(0) scale(1); opacity: 1; }
    }

    /* Yazının soldan sağa yavaş akma efekti */
    @keyframes soldanYavascaKay {
        0% { transform: translateX(-120px); opacity: 0; }
        40% { opacity: 0.3; }
        100% { transform: translateX(0); opacity: 1; }
    }
</style>
<link href="https://googleapis.com" rel="stylesheet">
''', unsafe_allow_html=True)

# LOGO EKRAN ÇIKTISI
st.markdown('''
<div class="logo-konteyner">
    <div class="cember-animasyon">
        <span class="bta-yazi">BTA</span>
    </div>
</div>
''', unsafe_allow_html=True)

# Saat Göstergesi
guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.markdown(f'<div style="font-size: 1.1rem; color: #cbd5e1; margin-bottom: 15px; font-weight: bold;">🕒 Canlı Veri Saati: {guncel_an} <span style="color:#10b981; font-size:0.9rem;">(10sn de bir otomatik yenileniyor)</span></div>', unsafe_allow_html=True)

excel_yolu = "nurican.xls.xlsm"

if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        tablo_bta = []
        tablo_alsat = []

        sinir = min(10, len(df))
        
        for idx in range(sinir):
            # 1. ÜST PANEL VERİLERİ (A, C, D Sütunları)
            hisse_a = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]

            if hisse_a and hisse_a not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                
                # BTA PUAN YUVARLAMA KONTROLÜ
                try:
                    puan_temiz = f"{float(puan_d):.2f}"
                except:
                    puan_temiz = str(puan_d).strip() if pd.notna(puan_d) else ""

                try:
                    ticker = yf.Ticker(f"{hisse_a}.IS")
                    hist = ticker.history(period="1d")
                    canli_fiyat = float(hist['Close'].iloc[-1]) if not hist.empty else 0.0
                except:
                    canli_fiyat = 0.0
                
                try: maliyet = float(alim_c.replace(",", "."))
                except: maliyet = 0.0
                
                kz_oran_str = "-"
                if maliyet > 0 and canli_fiyat > 0:
                    kz = ((canli_fiyat - maliyet) / maliyet) * 100
                    kz_oran_str = f"%{kz:+.2f}"

                tablo_bta.append({
                    "BTA PUAN 🔢": puan_temiz,
                    "BTA HİSSE 📈": hisse_a,
                    "BTA ALIM 📥": f"{maliyet:.2f} TL" if maliyet > 0 else alim_c,
                    "GÜNCEL FİYAT 💥": f"{canli_fiyat:.2f} TL" if canli_fiyat > 0 else "Yükleniyor...",
                    "KAR / ZARAR 📊": kz_oran_str
                })

            # 2. ALT PANEL VERİLERİ (B Sütunu)
            alsat_b = str(df.iloc[idx, 1]).strip().upper() if pd.notna(df.iloc[idx, 1]) else ""
            
            if alsat_b and alsat_b not in ["BTA AL SAT", "HİSSE", "NAN", "NONE"]:
                try:
                    ticker_as = yf.Ticker(f"{alsat_b}.IS")
                    hist_as = ticker_as.history(period="2d")
                    as_canli_fiyat = float(hist_as['Close'].iloc[-1]) if not hist_as.empty else 0.0
                    
                    if len(hist_as) >= 2:
                        onceki_kapanis = float(hist_as['Close'].iloc[-2])
                        as_degisim = ((as_canli_fiyat - onceki_kapanis) / onceki_kapanis) * 100
                    else:
                        as_degisim = 0.0
                except:
                    as_canli_fiyat, as_degisim = 0.0, 0.0

                tablo_alsat.append({
                    "GÜNLÜK AL SAT HİSSELERİ ⚡": alsat_b,
                    "ANLIK VERİ CANLI 📊": f"{as_canli_fiyat:.2f} TL" if as_canli_fiyat > 0 else "Yükleniyor...",
                    "YÜKSELİŞ ORANI 📈": f"%{as_degisim:+.2f}" if as_canli_fiyat > 0 else "-"
                })

        # EKRANA BASMA İŞLEMLERİ
        st.markdown('<div class="al-baslik">📈 BTA HİSSELERİ (ÜST PANEL)</div>', unsafe_allow_html=True)
        if tablo_bta:
            st.dataframe(pd.DataFrame(tablo_bta), use_container_width=True, hide_index=True)
        else:
            st.info("Üst panel için veri işleniyor...")

        st.write("")

        st.markdown('<div class="alsat-baslik">⚡ GÜNLÜK AL SAT HİSSELERİ (ALT PANEL)</div>', unsafe_allow_html=True)
        if tablo_alsat:
            st.dataframe(pd.DataFrame(tablo_alsat), use_container_width=True, hide_index=True)
        else:
            st.info("Alt panel için veri işleniyor...")

    except Exception as e:
        st.error(f"Excel okunurken bir sorun oluştu: {e}")
else:
    st.error("Excel dosyası 'nurican.xls.xlsm' bulunamadı!")

st.markdown('<div class="spk-kutusu">⚠️ <b>SPK YASAL UYARI:</b> Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir.</div>', unsafe_allow_html=True)
