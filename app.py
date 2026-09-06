import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
from streamlit_autorefresh import st_autorefresh

# Sayfa Yapılandırması
st.set_page_config(page_title="Canlı Hisse Takip Programı", layout="wide")

st.markdown('<style>.stApp {background: #0f172a!important; padding: 0.5rem;} h1,h2,h3,h4,h5,h6,p,span,label {color: #fff!important;} .stDataFrame {width: 100% !important; border: 1px solid #10b981 !important; border-radius: 8px;} .alsat-baslik {background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;} .al-baslik {background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); padding: 8px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; color:#fff;} .spk-kutusu {background-color: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; padding: 15px; border-radius: 6px; color: #fca5a5 !important; font-size: 0.95rem;}</style>', unsafe_allow_html=True)

# 🔄 CANLI FİYAT KİLİDİ: Sayfa her 10 saniyede bir hiçbir şeye dokunmadan kendi kendini yeniler
st_autorefresh(interval=10 * 1000, key="hisse_canli_yenileyici")
# Her yenilemede animasyonu baştan oynatmak için zaman damgası
anim_id = int(time.time())

# Şık Neon Tasarım, Gökkuşağı Çember ve Yazı CSS Kodları
st.markdown(f'''
   /* 🌈 ANIMASYONLU GÖKKUŞAĞI ÇEMBER VE KAYAN BTA LOGO ALANI */
    .logo-konteyner {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px 0;
        margin-bottom: 10px;
    }}
    .cember-animasyon-{anim_id} {{
        width: 120px;
        height: 120px;
        border: 4px solid #fff;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: transparent;
        position: relative;
        overflow: hidden;
        animation: 
            gokkusagiCember 4s linear infinite,
            yukardanDus 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }}
    .bta-yazi-{anim_id} {{
        font-family: 'Caveat', 'Segoe UI', cursive, sans-serif;
        font-size: 3.2rem;
        font-weight: bold;
        margin: 0;
        padding: 0;
        z-index: 2;
        background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        filter: drop-shadow(0px 2px 8px rgba(255,255,255,0.3));
        animation: soldanYavascaKay 1.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }}
excel_yolu = "nurican.xls.xlsm"

if os.path.exists(excel_yolu):
    try:
        # Doğrudan "WEB" isimli sayfayı okuyoruz
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        
        tablo_bta = []
        tablo_alsat = []

        # İlk 10 satırı kontrol ederek gereksiz sayfa kasmalarını önlüyoruz
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
